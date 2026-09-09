# Retrom PC-98 Web candidate

Upstream: https://github.com/AZO234/NP2kai, commit
`5939e0c6d5985c4c08fc70f289a83290e5d3e6f7` (`wx_alpha`).
The `wx_alpha` branch is an upstream mirror. Retrom changes belong on
`retrom/g5939e0c6d598` through a feature branch; `retrom-fork.json` records this boundary.

Build with Docker as the current non-root user:

```sh
.github/rpg-runtime/build-candidate.sh /absolute/empty/output
```

The SDK image is pinned by digest. CMake builds the SDL2 NP21kai entry with Asyncify,
ES modules, an explicit main and growing WASM memory. No proprietary BIOS is included.
`prepare-font.py` pins the np2-wasm 0.3.1 archive by SHA-256 and extracts its redistributable
Shinonome font. Third-party notices from NP2kai and the linked SDK ports accompany the output.
NP2kai combines MIT/BSD code with components under other licenses (including DOSBox GPL);
its root MIT license alone does not describe every compiled component. The generated LICENSE
preserves the full upstream LICENSES collection. Redistributed binaries require the applicable
corresponding source and notices.

The output contains `font.bmp`, `np2kai.mjs`, `np2kai.wasm`, `np2kai-register.mjs`, `LICENSE`
and `retrom-core-candidate.json`. The descriptor records the actual branch, commit, dirty state,
source tree hash and every output size/hash. The build never fetches games. It caches only build
inputs and products under ignored `.retrom-build/`.

## Host ABI: np2kai-host-v1

The registration module installs `__RETROM_NP2KAI_FACTORY_V1__` in the game's same-origin frame.
The factory exposes FS/callMain plus `_retrom_is_ready`, `_retrom_frame_count`, `_retrom_pause`,
`_retrom_key`, `_retrom_save`, `_retrom_restore` and `_retrom_stop`.
The host installs a configuration, a single HDI/D88 and font under `/emulator/np2kai` before
calling main. Execution initially yields while paused. Save/restore is allowed only when ready
and paused, completes the upstream queued operation synchronously, and uses `/emulator/np2kai/state.bin`. The host must restore the disk content before
loading that state. NP2 disk-change warnings are accepted for the fresh in-memory disk; other
state validation errors are fatal. The software SDL framebuffer remains readable while paused. Pause also stops audio; stop requests ordinary main cleanup.

The runtime owns persistent immutable disk caching, progress, gamepad translation and the bounded
content-bound state/disk-delta envelope. It does not compile this repository. Test integration
through Retrom PFB Review Preview and Product Launch, including input, pause, snapshot and a
separate restored Launch. A successful build alone is not a product compatibility result.

## Publication boundary

This feature supplies an unpublished PFB candidate. Do not create a stable tag or modify upstream
mirror history as part of local testing. Future releases use immutable
`retrom-core-g5939e0c6d598-rN[-rc.N]` tags and must include the recorded corresponding source,
licenses and validated release metadata before the runtime replaces its development input with
a pinned published release. The current source manifest intentionally rejects ordinary release
builds while NP2kai remains unpublished.
