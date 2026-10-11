"""
Duplicate-recording audit for the COG-BCI dataset (Hinss et al., Sci. Data 2023, Zenodo release).

Hashes the EEG content of every subject x session recording and reports groups of DIFFERENT subjects whose
recordings are byte-identical. Two input modes:
  --raw-dir   : the downloaded Zenodo release (sub-XX/ses-SY/**.set|.fdt); hashes file bytes per subject-session
  --clean-dir : per-subject-session .npz arrays produced by any deterministic preprocessing
                (sub-XX_SY.npz); hashes the array contents
Usage:  python audit_duplicates.py --raw-dir /path/to/cogbci   |   python audit_duplicates.py --clean-dir /path/to/clean
"""
import argparse
import hashlib
import re
from collections import defaultdict
from pathlib import Path

import numpy as np


def raw_hashes(root):
    out = defaultdict(hashlib.sha256)
    for f in sorted(Path(root).rglob("*")):
        if f.suffix.lower() not in (".set", ".fdt") or f.name.startswith("._"):
            continue
        m = re.search(r"sub-?(\d+).*?ses-?S?(\d)", str(f.relative_to(root)), re.I)
        if m:
            out[(int(m.group(1)), f"S{m.group(2)}")].update(f.name.encode() + f.read_bytes())
    return {k: h.hexdigest() for k, h in out.items()}


def clean_hashes(root):
    out = {}
    for f in sorted(Path(root).glob("sub-*_S*.npz")):
        m = re.match(r"sub-(\d+)_(S\d)\.npz", f.name)
        if not m:
            continue
        z = np.load(f); h = hashlib.sha256()
        for k in sorted(z.files):
            h.update(k.encode()); h.update(np.ascontiguousarray(z[k]).tobytes())
        out[(int(m.group(1)), m.group(2))] = h.hexdigest()
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--raw-dir"); g.add_argument("--clean-dir")
    a = ap.parse_args()
    H = raw_hashes(a.raw_dir) if a.raw_dir else clean_hashes(a.clean_dir)
    groups = defaultdict(list)
    for (sub, ses), h in H.items():
        groups[(ses, h)].append(sub)
    dup = {k: v for k, v in groups.items() if len(set(v)) > 1}
    print(f"recordings hashed: {len(H)}  subjects: {len({s for s, _ in H})}")
    if not dup:
        print("no cross-subject duplicates found")
    for (ses, h), subs in sorted(dup.items()):
        print(f"session {ses}: identical EEG in subjects {sorted(subs)}  (sha256 {h[:12]}...)")
    dsubs = sorted({s for v in dup.values() for s in v})
    print(f"subjects involved in any duplicate group: {dsubs}")
