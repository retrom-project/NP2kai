#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
output=${1:?absolute empty output directory required}
python3 "$root/.github/rpg-runtime/candidate_descriptor.py" prepare "$output"
python3 "$root/.github/rpg-runtime/test-host-abi.py"
python3 "$root/.github/rpg-runtime/test-state-check.py"
python3 "$root/.github/rpg-runtime/test-events.py"
mkdir -p "$root/.retrom-build/emscripten-cache"
docker run --rm --entrypoint bash --user "$(id -u):$(id -g)" --env HOME=/tmp --env EM_CACHE=/source/.retrom-build/emscripten-cache --env NP2KAI_VERSION=retrom-g5939e0c6d598 --env NP2KAI_HASH=5939e0c6d598 --volume "$root:/source" --workdir /source emscripten/emsdk@sha256:90b757eb11fa9a0e3ce4d2d9f76d932a56018e4accc37b5a28b2783751e60eb7 /source/.github/rpg-runtime/build-web.sh
python3 "$root/.github/rpg-runtime/prepare-font.py"
cp "$root/.retrom-build/font.bmp" "$root/.retrom-build/LICENSE" "$root/sdl/em/np2kai-register.mjs" "$output/"
cp "$root/.retrom-build/web/np2kai.mjs" "$root/.retrom-build/web/np2kai.wasm" "$output/"
python3 "$root/.github/rpg-runtime/candidate_descriptor.py" finalize "$output" --core-id np2kai
