/* Retrom Web host ABI. CPU work and snapshots run on the browser thread. */
#include "compiler.h"
#include "statsave.h"
#include "keystat.h"
#include "taskmng.h"
#include "soundmng.h"

int retrom_paused = 1;
int retrom_ready = 0;
int retrom_frames = 0;

EMSCRIPTEN_KEEPALIVE int retrom_is_ready(void) { return retrom_ready; }
EMSCRIPTEN_KEEPALIVE int retrom_frame_count(void) { return retrom_frames; }
EMSCRIPTEN_KEEPALIVE void retrom_pause(int paused) {
    retrom_paused = paused != 0;
    if (retrom_paused) { soundmng_stop(); } else { soundmng_play(); }
}
EMSCRIPTEN_KEEPALIVE void retrom_key(int key, int pressed) {
    if (retrom_ready && key >= 0 && key < 128) {
        keystat_senddata(key | (pressed ? 0 : 0x80));
    }
}
EMSCRIPTEN_KEEPALIVE int retrom_save(void) {
    if (!retrom_ready || !retrom_paused) { return -1; }
    fflush(NULL);
    /* Upstream public entry only queues work; complete it while paused. */
    statsave_save("/emulator/np2kai/state.bin");
    g_u8ControlState = 0;
    return statsave_save_d();
}
EMSCRIPTEN_KEEPALIVE int retrom_restore(void) {
    char message[1024] = {0};
    int result;
    if (!retrom_ready || !retrom_paused) { return -1; }
    result = statsave_check("/emulator/np2kai/state.bin", message, sizeof(message));
    if (result & ~STATFLAG_DISKCHG) {
        fprintf(stderr, "NP2kai state check failed (%d): %s\n", result, message);
        return -1;
    }
    statsave_load("/emulator/np2kai/state.bin");
    g_u8ControlState = 0;
    result = statsave_load_d();
    if (result) { fprintf(stderr, "NP2kai state load failed (%d)\n", result); }
    return result;
}
EMSCRIPTEN_KEEPALIVE void retrom_stop(void) {
    retrom_ready = 0;
    retrom_paused = 0;
    taskmng_exit();
}
