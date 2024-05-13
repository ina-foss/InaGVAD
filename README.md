# InaGVAD : a Challenging French TV and Radio Corpus annotated for Speech Activity Detection and Speaker Gender Segmentation

## To be released soon

This corpus will be released on May 20th 2024.
Stay in touch!


## About
InaGVAD is an annotated audiovisual corpus designed for Voice Activity Detection (VAD) and Speaker Gender Segmentation (SGS), aimed at representing the acoustic diversity of French TV and Radio programs.
This corpus is freely available for research purposes and can be downloaded on [French National Institute of Audivisual website](https://www.ina.fr/institut-national-audiovisuel/research/dataset-project).
InaGVAD detailed description, together with a benchmark of 6 freely available VAD systems and 3 SGS systems, is provided in [a paper](#citing) presented in LREC-COLING 2024.



InaGVAD contains 277 1-minute-long annotated recordings, partitioned into a 1h development and 3h37 test subset, allowing fair and reproducible system evaluation.
Evaluation scripts provided with the corpus allow to obtain performance estimates in the same conditions as the 6 VAD and 3 SGS systems presented [in the associated paper](#citing).
Recordings were collected from 10 French radio and 18 TV channels categorized into 4 groups associated to diverse acoustic conditions : generalist radio, music radio, news TV, and generalist TV.
The entire inaGVAD package; including corpus, annotations, evaluation scripts, and baseline training code; is made freely accessible, fostering future advancement in the domain.


InaGVAD provides an extended VAD and SGS annotation scheme, allowing to describe systems diverse abilities based on :
* Speaker Traits categories
  * 3 Genders : Female, Male, I Don't Know (IDK)
  * 3 Age groups : Young (prepubescent), Adult, Ederly (Senior)
  * 3 Speech Qualities : standard, interjections (ah, oh, eg, aie), atypical (crying, laughing or shouted speech, ill person voice, artificially distorted voices, vocal performance, monster voice...)
* 10 Non-Speech event categories : Applause, environmental noise, hubbub, jingle, foreground music, background music, respiration, non-intelligible laughers, other, emty


Results demonstrate that our proposal, trained on a single - but diverse - hour of data, achieved competitive SGS results.

\\ \newline \Keywords{Voice Activity Detection (VAD), Speaker Gender Segmentation, Audiovisual Speech Resource, Speaker Traits, Speech Overlap, Benchmark, X-vector, Gender Representation in the Media} 

## Statement of need

inaGVAD was primarily designed to build systems able to monitor men's and women's speaking time in media (see [Doukhan18](https://doi.org/10.18146/2213-0969.2018.jethc156)).

* Speech corpora designed for ASR (ESTER, REPERE) tend to favor the quantity of lexical terms to the accurate timing of non-speech events. Their programs are mostly composed of news ore debates, excluding documentaries, movies, cartoons, musical programs and advertisments.
* Speech resources suited to VAD (AVA-Speech, DI-HARD 2, RATS, LibriParty) do provide more accurate timings but lacks speaker traits (gender, age), speech quality (timbre, ellocution) and non-speech event annotation.
* Speaker recognition corpora provide isolated speaker segments not allowing to evaluate speaker changes, and are generally obtained from interviews using automatic methods (diarization, VAD, active speaker detection) discarding atypical vocal performances or noise conditions (Voxceleb, INA speaker dictionnary, INA diachronic speaker dicionnary).

InaGVAD is aimed at closing the gap between ASR, VAD and speaker corpora and provides :
* fine-grained time-coded speech and non-speech events annotations
* speaker traits (gender, age) and speech quality annotations
* materials representing the diversity of contents that can be found in French TV and radio
* freely available corpus and evaluation code allowing to train and evaluate models

A Voice Activity Detection benchmark based on 6 open-source systems (inaSpeechSegmenter, LIUM_SpkDiarization, Pyannote, Rvad, Silero, SpeechBrain) show InaGVAD generalist TV and music radio categories are more challenging than estimates obtained on AMI, VoxConverse and DIHARD 3 VAD corpora.

## Downloading Audio files

Downloading inaGVAD audio files requires to fill accept its genral term and conditions of use (GCU) and to fill the form available on https://www.ina.fr/institut-national-audiovisuel/research/dataset-project


## Installation

Installing dependencies:
```bash
pip install .
```

## Evaluating Voice Activity Detection (VAD) systems

## Evaluating Speaker Gender Segmentation (SGS) systems

## Training a new system


## Citing

inaGVAD has been fully described in a paper accepted to LREC-COLING 2024 to be published on May 20th 2024 at LREC-COLING.
If using this corpus in your research, please cite the following study.

```
@inproceedings{inagvad2024,
title={InaGVAD : a Challenging French TV and Radio Corpus annotated for Speech Activity Detection and Speaker Gender Segmentation},
author={David Doukhan and Christine Maertens and William {Le Personnic} and Ludovic Speroni and Reda Dehak},
booktitle={Joint International Conference on Computational Linguistics, Language Resources and Evaluation (LREC-COLING)},
year={2024},
}
```
