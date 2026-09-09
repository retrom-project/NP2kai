#!/usr/bin/env python3
"""Validate the immutable NP2kai baseline and publication boundaries."""
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
BASE = "5939e0c6d5985c4c08fc70f289a83290e5d3e6f7"

def main():
    fork = json.loads((ROOT / "retrom-fork.json").read_text())
    assert fork["schemaVersion"] == 1
    assert fork["forkRepository"] == "https://github.com/retrom-project/NP2kai"
    assert fork["defaultBranch"] == "retrom/g5939e0c6d598"
    assert fork["upstreamMirrorBranch"] == "wx_alpha"
    assert fork["adapterAbi"] == "np2kai-host-v1"
    assert fork["upstreams"] == [{"role": "np2kai", "repository": "https://github.com/AZO234/NP2kai",
        "refType": "COMMIT", "ref": BASE, "commit": BASE}]
    assert fork["releaseAssets"] == ["LICENSE", "font.bmp", "np2kai-register.mjs", "np2kai.mjs", "np2kai.wasm", "rpg-runtime-release.json"]
    subprocess.run(["git", "merge-base", "--is-ancestor", BASE, "HEAD"], cwd=ROOT, check=True)
    print("NP2kai fork source contract: ok")

if __name__ == "__main__":
    main()
