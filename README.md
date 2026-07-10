# NCT Diagnostic Probe

Reference implementation of the **Negative Contrast Trap (NCT) Diagnostic Probe** described by Tionne Smith.

The script measures three structural signals:

- **NCP:** Negative Contrast Pattern frequency
- **ASI:** sentence-opener lock-in
- **ND:** nominalization density

It reports a weighted Trap Score from 0 to 100.

## Requirements

Python 3.9 or newer. No third-party packages are required.

## Usage

```bash
python nct_probe.py input.txt
```

Run the included reference samples:

```bash
python nct_probe.py
```

Run verification tests:

```bash
python -m unittest -v
```

## Reproduced reference result

The included paired samples produce:

- AI-style sample: **90.0/100 — SEVERE**
- Human-style sample: **19.3/100 — CLEAN**
- Divergence: **70.7 points**

## Citation

Smith, Tionne. “The Negative Contrast Trap.” Antiparty Press, 2026.

## Research status

This repository contains the paper’s diagnostic reference implementation. Scores are structural indicators and should not be treated as proof of authorship or as a general-purpose AI detector.
