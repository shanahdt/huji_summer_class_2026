# Corpus Studies in Music
## Summer Institute 2026 · Bienen School of Music, Northwestern University

This intensive course asks a single question across eight sessions:

> **What kind of knowledge does corpus analysis produce, and at what cost?**

Every method we use encodes assumptions about what music is, what matters about it,
and whose music counts as data. We develop technical fluency in Python — but fluency
is not the goal. The goal is the ability to design a research question, choose a method
that fits it, and account for what the method cannot see.

## Primary corpus

We work throughout with **Beregovski's *Jewish Instrumental Folk Music*** —
245 tunes collected from Ukrainian Jewish musicians in the 1930s and 40s,
suppressed under Stalin, published posthumously, and encoded in Humdrum kern
by Malin & Shanahan (2025), *Music Theory Online* 31(3).

- Companion website: [shanahdt.github.io/mode_in_klezmer](https://shanahdt.github.io/mode_in_klezmer/)

## Running the notebooks

Each notebook has a **launch button** at the top to open it in Google Colab.
No installation required — click and run.

For local use:
```bash
python -m venv corpus-env
source corpus-env/bin/activate
pip install music21 pandas matplotlib seaborn scipy scikit-learn librosa jupyterquiz requests
jupyter notebook
```

## Session schedule

| Day | Date | Topic |
|-----|------|-------|
| 1 | Sun 21 Jun | Encoding as Interpretation |
| 2 | Mon 22 Jun | Pitch Distributions and Mode |
| 3 | Tue 23 Jun | N-grams and Melodic Tendency |
| 4 | Wed 24 Jun | Melodic Similarity |
| 5 | Thu 25 Jun | Metadata and the Collector's Categories |
| — | Fri–Sat | *No class (Shabbat)* |
| 6 | Sun 28 Jun | Audio Features and What They Measure |
| 7 | Mon 29 Jun | Mode Detection and Clustering |
| 8 | Tue 30 Jun | Presentations and Synthesis |

## Instructor

**Daniel Shanahan**
Associate Professor of Music Theory and Cognition
Bienen School of Music, Northwestern University
