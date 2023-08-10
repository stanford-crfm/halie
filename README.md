<div align="center">

<img src="./halie.png" width="350px"/>

**An Interactive Evaluation Framework for Human-Language Model Interaction**

</div>

## Overview

This repository contains the code for HALIE (Human-AI Language-based Interaction Evaluation), a new framework for evaluating human-LM interaction. It is designed to be flexible and extensible to support a variety of interactive tasks beyond the five tasks we considered in our paper: **social dialogue, question answering, crossword puzzles, text summarization, and metaphor generation**. All the code for the five tasks are included in this repository.

- Paper: [Evaluating Human-Language Model Interaction](https://arxiv.org/abs/2212.09746) (Mina Lee, Megha Srivastava, Amelia Hardy, John Thickstun, Esin Durmus, Ashwin Paranjape, Ines Gerard-Ursin, Xiang Lisa Li, Faisal Ladhak, Frieda Rong, Rose E. Wang, Minae Kwon, Joon Sung Park, Hancheng Cao, Tony Lee, Rishi Bommasani, Michael Bernstein, Percy Liang, 2022)

If you have any questions, please reach out to [Mina Lee](https://minalee.info/) at `minalee@stanford.edu`. For scenario-specific questions or feedback (e.g. task design, data issues), please include the following authors:
* **Social Dialogue**: [Amelia Hardy](https://www.linkedin.com/in/ameliahardy/) (`ahardy@stanford.edu`), [Ashwin Paranjape](https://ashwinparanjape.github.io/) (`ashwinp@cs.stanford.edu`), [Ines Gerard-Ursin](https://www.linkedin.com/in/ines-gerard-ursin/?originalSubdomain=uk) (`ines.gerard-ursin20@imperial.ac.uk`), [Esin Durmus](https://esdurmus.github.io/) (`esindurmus@cs.stanford.edu`), [Faisal Ladhak](https://www.cs.columbia.edu/~faisal/) (`faisal@cs.columbia.edu`), [Joon Sung Park](http://www.joonsungpark.com/) (`joonspk@stanford.edu`)
* **Question Answering**: [Megha Srivastava](https://cs.stanford.edu/~megha) (`megha@cs.stanford.edu`), [John Thickstun](https://johnthickstun.com/) (`jthickstun@stanford.edu`), [Rose Wang](https://rosewang2008.github.io/) (`rewang@cs.stanford.edu`), [Minae Kwon](https://stanford.edu/~mnkwon/)  (`mnkwon@cs.stanford.edu`)
* **Crossword Puzzles**: [Megha Srivastava](https://cs.stanford.edu/~megha) (`megha@cs.stanford.edu`)
* **Text Summarization**: [Esin Durmus](https://esdurmus.github.io/) (`esindurmus@cs.stanford.edu`), [Faisal Ladhak](https://www.cs.columbia.edu/~faisal/) (`faisal@cs.columbia.edu`)
* **Metaphor Generation**: [Frieda Rong](https://friedeggs.github.io/) (`rongf@cs.stanford.edu`), [Xiang Lisa Li](https://xiangli1999.github.io/) (`xlisali@stanford.edu`)

---

## Contents
- [Data](#Data)
- [Analysis](#Analysis)
- [Interfaces](#Interfaces)

---

## Data

See [README](./data/README.md) for a more comprehensieve overview of data in HALIE.

**Standardized data.** If you simply want to take a look at our data or use it to perform your own analysis, you can find the standardized data for the five tasks in `./data/std`. 

**Raw data.** On the other hand, if you want to standardize data from raw data we collected (`./data/raw`), you can follow the steps below to convert the raw data.

First, install the required packages:
```
pip3 install -r requirements.txt
```

Then, run the following command to standardize the logs (e.g., for question answering):
```
python3 ./src/run_question.py
```

The above command reads the raw data at `./data/raw/question ` and saves the standardized data at `./data/std/question`. For the other four tasks, replace `question` with the name of the task you want to standardize in the path as well as command.

**Visualizations.** Static and dynamic visualizations of our data, which allows for an easier way for looking at raw interaction traces, is included at `./data/visualizations`.

**Your data.** If you are interested in extending HALIE to support a new task, please create a PR or contact [Mina Lee](https://minalee.info/) at `minalee@stanford.edu`.

---

## Analysis

We provide Jupyter Notebook files for analyzing the data collected for HALIE. The files are stored in `./notebook`.

---

## Interfaces

Code for the interface used to collect interaction traces for crossword puzzles in HALIE is located in `./interfaces`. 

The interfaces for question answering, text summarization, and metaphor generation are built based on CoAuthor, whose code is available [here](https://github.com/minalee-research/coauthor-interface). The interface for dialogue is based on Chirpy Cardinal, whose code is available [here](https://stanfordnlp.github.io/chirpycardinal/).

