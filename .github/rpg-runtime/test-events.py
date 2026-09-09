#!/usr/bin/env python3
"""Round-trip the real timer event codec and its registration tables."""
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
s = (ROOT / "statsave.c").read_text()
t = (ROOT / "statsave.tbl").read_text()
tables = t[t.index("static const PROCTBL evtproc"):t.index("static const PROCTBL dmaproc")]
callbacks = set(re.findall(r"PROCID\([^\n]+?\),\s*(\w+)\}", tables.split("static const ENUMTBL")[0]))
callbacks.add("upd4990_hrtimer_proc")
converters = s[s.index("static BRESULT proc2num"):s.index("// ---- file")]
writer = s[s.index("typedef struct {\n  UINT readyevents;"):s.index("static int flagsave_evt")]
reader = s[s.index("static int nevent_read"):s.index("static int flagload_evt")]
with tempfile.TemporaryDirectory() as directory:
    root = pathlib.Path(directory)
    header = r'''
#include <assert.h>
#include <stdint.h>
#include <string.h>
#define SUPPORT_HRTIMER 1
#define DISABLE_SOUND 1
#define NELEMENTS(a) (sizeof(a)/sizeof((a)[0]))
#define ZeroMemory(a,b) memset(a,0,b)
#define PROCID(a,b,c,d) (((d)<<24)+((c)<<16)+((b)<<8)+(a))
#define PROC2NUM(a,b) proc2num(&(a),(b),NELEMENTS(b))
#define NUM2PROC(a,b) num2proc(&(a),(b),NELEMENTS(b))
#define SUCCESS 0
#define FAILURE 1
#define STATFLAG_SUCCESS 0
#define STATFLAG_WARNING 128
#define STATFLAG_FAILURE -1
typedef int BOOL;typedef unsigned UINT;typedef uint32_t UINT32;typedef int32_t SINT32;typedef intptr_t INTPTR;typedef int BRESULT;typedef void* STFLAGH;
#include "nevent.h"
typedef struct {UINT32 id;void *proc;} PROCTBL;
typedef struct {UINT32 id;NEVENTID num;} ENUMTBL;
_NEVENT g_nevent;
static unsigned char buffer[128];
static int statflag_write(STFLAGH h,const void*p,UINT n){(void)h;assert(n<=sizeof(buffer));memcpy(buffer,p,n);return 0;}
static int statflag_read(STFLAGH h,void*p,UINT n){(void)h;assert(n<=sizeof(buffer));memcpy(p,buffer,n);return 0;}
'''
    stubs = "\n".join(f"void {name}(NEVENTITEM item) {{(void)item;}}" for name in sorted(callbacks))
    main = r'''
int main(void) {
 NEVENTID restored[1];UINT count=0;
 g_nevent.item[NEVENT_HRTIMER].clock=123;
 g_nevent.item[NEVENT_HRTIMER].proc=upd4990_hrtimer_proc;
 assert(nevent_write(0,NEVENT_HRTIMER)==0);
 memset(&g_nevent,0,sizeof(g_nevent));
 assert(nevent_read(0,restored,&count)==0 && count==1 && restored[0]==NEVENT_HRTIMER);
 assert(g_nevent.item[NEVENT_HRTIMER].clock==123 && g_nevent.item[NEVENT_HRTIMER].proc==upd4990_hrtimer_proc);
 assert(nevent_write(0,NEVENT_MAXEVENTS-3)==STATFLAG_FAILURE);
 g_nevent.item[NEVENT_HRTIMER].proc=0;
 assert(nevent_write(0,NEVENT_HRTIMER)==STATFLAG_FAILURE);
 return 0;
}
'''
    (root / "test.c").write_text(header + stubs + tables + converters + writer + reader + main)
    subprocess.run(["cc", "-Wall", "-Wextra", "-Werror", "-I", str(ROOT), str(root / "test.c"), "-o", str(root / "test")], check=True)
    subprocess.run([str(root / "test")], check=True)
print("np2kai events: high-resolution timer round-trip and unknown event rejection passed")
