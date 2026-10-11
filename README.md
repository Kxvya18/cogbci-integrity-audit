# COG-BCI duplicate-recording audit

The COG-BCI database (Hinss et al., *Scientific Data* 10:85, 2023; Zenodo) is a widely used open EEG dataset for
passive BCI research (29 participants x 3 sessions; MATB, N-back, PVT, Flanker).

While building leakage-controlled cross-session workload benchmarks on this dataset, we found that the released EEG of
**eight participant IDs is identical**: subjects **18, 19, 20, 21, 22, 23, 24 and 27** contain byte-identical EEG in
every session (S1, S2, S3), even though the dataset notebook lists distinct recording dates and task orders for them.

```
$ python audit_duplicates.py --clean-dir <per-session npz arrays>
recordings hashed: 87  subjects: 29
session S1: identical EEG in subjects [18, 19, 20, 21, 22, 23, 24, 27]
session S2: identical EEG in subjects [18, 19, 20, 21, 22, 23, 24, 27]
session S3: identical EEG in subjects [18, 19, 20, 21, 22, 23, 24, 27]
```

## Why it matters
Any evaluation that treats these IDs as different people places the same recording in both training and test data
(cross-subject splits, leave-one-subject-out, or train/test competitions using these participants). This inflates
reported accuracy and shrinks the effective sample to 22 unique participants.

## Use
```
python audit_duplicates.py --raw-dir /path/to/cogbci_release     # hashes .set/.fdt bytes per subject-session
python audit_duplicates.py --clean-dir /path/to/preprocessed_npz  # hashes arrays (sub-XX_SY.npz)
```
Requires Python 3 and NumPy. No data is redistributed here.

## Recommendation
Exclude seven of the eight duplicated IDs (keep one) when using COG-BCI, and report results on the 22 unique
participants. This audit reports an observed property of the public release; it makes no claim about how it arose.
