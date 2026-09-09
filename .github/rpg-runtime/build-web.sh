#!/usr/bin/env bash
set -euo pipefail
emcmake cmake -S /source -B /source/.retrom-build/web -D__EMSCRIPTEN__=ON -DCMAKE_BUILD_TYPE=Release -DUSE_NETWORK=OFF -DUSE_SDL_TTF=OFF -DUSE_SDL_MIXER=OFF -DRETROM_WEB=ON
cmake --build /source/.retrom-build/web --target emnp21kai_sdl2 --parallel 6
