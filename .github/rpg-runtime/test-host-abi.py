#!/usr/bin/env python3
"""Exercise the real host bridge against the upstream queued state API contract."""
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
with tempfile.TemporaryDirectory() as directory:
    root = pathlib.Path(directory)
    (root / "bms-reset.c").write_text("#include <stdint.h>\n"
        "typedef int BOOL; typedef uint8_t BYTE; typedef uint8_t UINT8; typedef uint16_t UINT16; typedef uint32_t UINT32; typedef struct {int value;} NP2CFG;\n"
        '#include "bmsio.h"\nvoid (*reset_callback)(const NP2CFG*) = bmsio_reset;\n')
    subprocess.run(["cc", "-Wall", "-Wextra", "-Werror", "-fsyntax-only", "-I", str(ROOT / "io"), str(root / "bms-reset.c")], check=True)
    (root / "retrom.c").write_bytes((ROOT / "sdl/em/retrom.c").read_bytes())
    (root / "compiler.h").write_text("#include <stdio.h>\n#include <stdint.h>\n#define EMSCRIPTEN_KEEPALIVE\n")
    (root / "statsave.h").write_text("extern uint8_t g_u8ControlState;\n#define STATFLAG_DISKCHG 1\nint statsave_save(const char*); int statsave_save_d(void); int statsave_load(const char*); int statsave_load_d(void); int statsave_check(const char*,char*,int);\n")
    for name, declaration in {"keystat.h": "void keystat_senddata(int);", "taskmng.h": "void taskmng_exit(void);", "soundmng.h": "void soundmng_stop(void); void soundmng_play(void);"}.items():
        (root / name).write_text(declaration)
    (root / "test.c").write_text(r'''#include <assert.h>
#include "retrom.c"
uint8_t g_u8ControlState;
static int saved, loaded, result, checked;
int statsave_save(const char *p) {(void)p; g_u8ControlState=1; return 0;}
int statsave_load(const char *p) {(void)p; g_u8ControlState=2; return 0;}
int statsave_save_d(void) {saved++; return result;}
int statsave_load_d(void) {loaded++; return result;}
int statsave_check(const char *p,char *m,int n) {(void)p;(void)m;(void)n; return checked;}
void keystat_senddata(int n) {(void)n;}
void taskmng_exit(void) {}
void soundmng_stop(void) {}
void soundmng_play(void) {}
int main(void) {
 assert(retrom_save()==-1 && retrom_restore()==-1);
 retrom_ready=1; retrom_pause(0); assert(retrom_save()==-1);
 retrom_pause(1);
 assert(retrom_save()==0 && saved==1 && g_u8ControlState==0);
 assert(retrom_restore()==0 && loaded==1 && g_u8ControlState==0);
 result=-1; assert(retrom_save()==-1 && retrom_restore()==-1);
 checked=4; assert(retrom_restore()==-1 && loaded==2);
 return 0;
}
''')
    subprocess.run(["cc", "-Wall", "-Wextra", "-Werror", "-I", str(root), "-I", str(ROOT / "sdl/em"), str(root / "test.c"), "-o", str(root / "test")], check=True)
    subprocess.run([str(root / "test")], check=True)
print("np2kai host ABI: synchronous state and failure propagation passed")
