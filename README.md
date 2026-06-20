# Corpus Studies in Music — Summer Institute 2026

8-session intensive course on computational corpus analysis using the Beregovski klezmer corpus.

**Instructor:** Daniel Shanahan, Northwestern University  
**Corpus:** Malin & Shanahan (2025), *MTO* 31(3)

## Quick start (local)

```bash
git clone https://github.com/shanahdt/corpus-studies-israel-2026.git
cd corpus-studies-israel-2026
python -m venv corpus-env && source corpus-env/bin/activate
pip install music21 pandas matplotlib seaborn scipy scikit-learn librosa jupyterquiz requests jupyter-book
jupyter notebook notebooks/day1_encoding.ipynb
```

Or click any Colab badge in the notebooks to run in the browser.

## Building the Jupyter Book

```bash
pip install jupyter-book
jupyter-book build .
# Site appears in _build/html/
```

## Deploying to GitHub Pages

```bash
pip install ghp-import
ghp-import -n -p -f _build/html
```

## Structure

```
corpus-studies-israel-2026/
├── _config.yml              # Jupyter Book config
├── _toc.yml                 # Table of contents
├── intro.md                 # Landing page
├── notebooks/               # One notebook per session (Days 1-8)
├── quizzes/                 # Quiz JSON files (one per session)
├── PROJECT_BRIEF.md         # Full project context for collaborators
└── README.md
```
