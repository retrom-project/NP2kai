#!/usr/bin/env python3
"""Check the real section dispatcher against a serialized BMS entry."""
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
source = (ROOT / "statsave.c").read_text()
check = "int statsave_check(" + source.split("int statsave_check(", 1)[1].split("int statsave_load(", 1)[0]
with tempfile.TemporaryDirectory() as directory:
    root = pathlib.Path(directory)
    harness = r'''
#include <assert.h>
#include <string.h>
#define SUPPORT_BMS 1
#define DISABLE_SOUND 1
#define NELEMENTS(a) (sizeof(a)/sizeof((a)[0]))
#define FALSE 0
#define TRUE 1
#define STATFLAG_MASK 0x3fff
#define STATFLAG_SUCCESS 0
#define STATFLAG_WARNING 0x80
#define STATFLAG_FAILURE -1
#define OEMCHAR char
typedef int BOOL;
enum {STATFLAG_BIN,STATFLAG_MEM,STATFLAG_TERM,STATFLAG_COM,STATFLAG_DMA,STATFLAG_EGC,STATFLAG_EPSON,STATFLAG_EVT,STATFLAG_EXT,STATFLAG_GIJ,STATFLAG_FDD,STATFLAG_SXSI,STATFLAG_BMS};
typedef struct {char index[12];int type;} SFENTRY;
static const SFENTRY np2tbl[]={{"BMS",STATFLAG_BMS},{"END",STATFLAG_TERM}};
static struct {struct {struct {char index[12];} hdr;} sfh;} file;
typedef __typeof__(&file) SFFILEH;
static int section, checked, version;
static SFFILEH statflag_open(const char*p,char*b,int s){(void)p;(void)b;(void)s;section=0;return &file;}
static void statflag_close(SFFILEH f){(void)f;}
static int statflag_readsection(SFFILEH f){assert(section<2);memcpy(f->sfh.hdr.index,np2tbl[section++].index,12);return 0;}
static int flagcheck_veronly(void*f,const SFENTRY*t){(void)f;assert(t->type==STATFLAG_BMS);checked++;return version;}
static int flagcheck_versize(void*f,const SFENTRY*t){(void)f;(void)t;return 0;}
static int flagcheck_fdd(void*f,const SFENTRY*t){(void)f;(void)t;return 0;}
static int flagcheck_sxsi(void*f,const SFENTRY*t){(void)f;(void)t;return 0;}
'''
    (root / "test.c").write_text(harness + check + r'''
int main(void){
 assert(statsave_check("state",0,0)==0 && checked==1);
 version=-1;assert(statsave_check("state",0,0)==-1 && checked==2);
 return 0;
}
''')
    subprocess.run(["cc", "-Wall", "-Wextra", "-Werror", str(root / "test.c"), "-o", str(root / "test")], check=True)
    subprocess.run([str(root / "test")], check=True)
print("np2kai state section validation: BMS and version rejection passed")
