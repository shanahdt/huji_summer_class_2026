# Corpus Studies in Music
## Summer Institute 2026 · Bienen School of Music, Northwestern University

## Instructor

**Daniel Shanahan**
Associate Professor of Music Theory and Cognition
Bienen School of Music, Northwestern University

# Welcome! 

Thank you for joining me in this session on quantitative methods in musicology!

Over the course of these next eight days, we will focus on the following questions:

> **What kind of knowledge does corpus analysis produce?**

Every method we use encodes assumptions about what music is, what matters about it,
and whose music counts as data. We develop technical fluency in Python—but fluency
is not the goal. 

> **How can one ask questions of data that are musicologically meaningful?**


The goal is the ability to design an interesting research question, choose a method that fits it, and interpret the results in a meaningful and interesting way. 

It's obviously not a lot to just say that there's a lot of something, and the distance between **frequency** and **meaning** can often be a big one.

> **Ask questions that are specifically of interest to _you_.**

## Primary corpora

We have a few corpora that we will be working with in this class:

1. Beregovski's Klezmer Corpus (see Malin and Shanahan, 2025); see [here](https://shanahdt.github.io/mode_in_klezmer/).
2. The Essen Folksong Collection (Schaffrath and Huron, 1995; see [here](https://github.com/ccarh/essen-folksong-collection)).
3. The Meertens Tune Collection of Dutch Folksongs (Van Kranenburg, et al. 2014; see [here](https://www.liederenbank.nl/mtc/))
4. The Bach Chorales (encoded by David Huron)
5. The McGill Billboard Corpus (Burgoyne, 2012; see [here](https://ddmal.ca/research/The_McGill_Billboard_Project_(Chord_Analysis_Dataset)/)).


It's very possible that conversations will take us to other copora, as well! Also, if you're interested in working with another corpus for your own project, please let me know!

## Session schedule

| Day | Date | Topic |
|-----|------|-------|
| 1 | Sun 21 Jun | Encoding as Interpretation and Beginning to Count Things! |
| 2 | Mon 22 Jun | N-grams and Melodic Tendency |
| 3 | Tue 23 Jun | Pitch Distributions and Key-Finding |
| 4 | Wed 24 Jun | Melodic Similarity |
| 5 | Thu 25 Jun | Metadata and Categories |
| — | Fri–Sat | *No class* |
| 6 | Sun 28 Jun | Clustering and Machine Learning |
| 7 | Mon 29 Jun | Audio Features and What They Measure |
| 8 | Tue 30 Jun | Synthesis, Final Thoughts, and (Brief) Presentations/Discussions |


## Assessments 

1. Daily Quizzes (Ungraded—-I'm treating these as simply self-reflective knowledge checks)
2. Daily emails logging of progress on your project (I'll give prompts)
3. A final project with a brief presentation 


### The Daily Quizzes

These can all be found here on teh website. They are simply meant to reinforce the topics discussed. None of the data is saved and you can feel retake anything as much as you need.


### The Daily Logging

I'd like to work closely with each of you on your projects for the next couple of weeks. Please **email me** daily a response to the prompt at the end of each class--I will do my best to respond promptly to each (although there is a bit of timezone difference in my favor; you might get responses when you're sleeping). 

### The Final Project 

Two weeks isn't really enough time to come up with an earth-shattering presentation, but it is long enough to dive deeply into something that interests you. My hope is that you can take a question that might be of interest to you (with the data available), and make a meaningful step toward answering it. If you're interested in another repertoire, you can view this as an opportunity to build a tool that could be applied to a different corpus at a later date. I'm hoping that you can have a 10-minute presentation ready to discuss:

- your dataset
- what you did with it
- what you expected to find
- how you tested your hypothesis
- and what you would do differently or expand upon in the future

## Running the notebooks

Each notebook has a **launch button** at the top to open it in Google Colab.
No installation required — click and run. This might be the easiest way to go in the first day or two. It might sometimes run a little slower (especially for the first setup cells) but it doesn't require any of installation on your own local machine.

If you'd like to run these notebooks on your own machine, you would first clone the [github repo](https://github.com/shanahdt/huji_summer_class_2026), and run the following lines in your terminal:

```bash
python -m venv corpus-env
source corpus-env/bin/activate
pip install music21 pandas matplotlib seaborn scipy scikit-learn librosa jupyterquiz requests
jupyter notebook
```

This can sometimes cause frustration. Just let me know and we can work through anything together!
