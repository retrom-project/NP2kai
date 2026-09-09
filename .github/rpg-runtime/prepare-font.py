"""Materialize the pinned, freely distributed Shinonome NP2 font."""
import hashlib
import io
import tarfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
URL = "https://registry.npmjs.org/np2-wasm/-/np2-wasm-0.3.1.tgz"
SHA = "54d9d05667004ebddf7ebd0689a985b4ce7578fb4e94d3e3aacccd4c907c9fe5"
archive = ROOT / ".retrom-build/np2-wasm-0.3.1.tgz"
if not archive.exists():
    archive.write_bytes(urllib.request.urlopen(URL, timeout=60).read(16 * 1024 * 1024))
content = archive.read_bytes()
if hashlib.sha256(content).hexdigest() != SHA:
    raise SystemExit("NP2KAI_FONT_SOURCE_INVALID")
with tarfile.open(fileobj=io.BytesIO(content), mode="r:gz") as source:
    font = source.extractfile("package/dist/font.bmp").read()
    license_text = source.extractfile("package/LICENSE").read()
if len(font) != 524350 or font[:2] != b"BM":
    raise SystemExit("NP2KAI_FONT_INVALID")
(ROOT / ".retrom-build/font.bmp").write_bytes(font)
notices = [("NP2kai", (ROOT / "LICENSE").read_bytes()), ("NP2 Web Shinonome font", license_text)]
for path in sorted((ROOT / "LICENSES").rglob("*")):
    if path.is_file():
        notices.append((str(path.relative_to(ROOT)), path.read_bytes()))
ports = ROOT / ".retrom-build/emscripten-cache/ports"
for relative in ["sdl2/SDL-release-2.32.0/include/SDL_copying.h", "libpng/libpng-1.6.39/LICENSE", "zlib/zlib-1.3.1/LICENSE"]:
    notices.append((relative, (ports / relative).read_bytes()))
text = []
for label, raw in notices:
    try:
        decoded = raw.decode("utf-8")
    except UnicodeDecodeError:
        decoded = raw.decode("cp932")
    text.append(f"\n=== {label} ===\n{decoded}\n")
(ROOT / ".retrom-build/LICENSE").write_text("".join(text), encoding="utf-8")
