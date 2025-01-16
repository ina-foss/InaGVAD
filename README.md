# InaGVAD : a Challenging French TV and Radio Corpus annotated for Speech Activity Detection and Speaker Gender Segmentation

## About
InaGVAD is a Voice Activity Detection (VAD) and Speaker Gender Segmentation (SGS) dataset designed for representing the acoustic diversity of French TV and Radio programs.
This corpus is freely available for research purposes and can be downloaded on [French National Institute of Audivisual website](https://www.ina.fr/institut-national-audiovisuel/research/dataset-project).
InaGVAD detailed description, together with a benchmark of 6 freely available VAD systems and 3 SGS systems, is provided in [a paper](#citing) presented in LREC-COLING 2024.



InaGVAD contains 277 1-minute-long annotated recordings, partitioned into a 1h development and 3h37 test subset, allowing fair and reproducible system evaluation.
Evaluation scripts provided with the corpus provide performance estimates in the same conditions as the 6 VAD and 3 SGS systems presented [in the associated paper](#citing).
Recordings were collected from 10 French radio and 18 TV channels categorized into 4 groups associated to diverse acoustic conditions : generalist radio, music radio, news TV, and generalist TV.



InaGVAD provides an extended VAD and SGS annotation scheme, allowing to describe systems diverse abilities based on :
* Speaker Traits categories
  * 3 Genders : Female, Male, I Don't Know (IDK)
  * 3 Age groups : Young (prepubescent), Adult, Ederly (Senior)
  * 3 Speech Qualities : standard, interjections (ah, oh, eg, aie), atypical (crying, laughing or shouted speech, ill person voice, artificially distorted voices, vocal performance, monster voice...)
* 10 Non-Speech event categories : Applause, environmental noise, hubbub, jingle, foreground music, background music, respiration, non-intelligible laughers, other, empty


The entire inaGVAD package; including corpus, annotations, evaluation scripts, and baseline training code; is made freely accessible, fostering future advancement in the domain.



[comment]: <> (Keywords, Voice Activity Detection, Speaker Gender Segmentation, Audiovisual Speech Resource, Speaker Traits, Speech Overlap, Benchmark, X-vector, Gender Representation in the Media)

## Statement of need

Over the past few years, a growing amount of digital humanity studies, as well as French audiovisual regulation authorities reports, have used automatic Voice Activity Detection (VAD) and Speaker Gender Segmentation (SGS) for estimating women's and men's speaking time in massive amounts of audiovisual media ([Dou18](https://doi.org/10.18146/2213-0969.2018.jethc156), [ARC24](https://www.arcom.fr/sites/default/files/2024-03/Arcom%20-%20Rapport%20repr%C3%A9sentation%20femmes%202023.pdf)).
If these studies are associated to high social impact and mediatic coverage, the lack of appropriate annotated speech resources makes it difficult to estimate the reliability of SGS systems on the diversity of audiovisual materials.

* Speech corpora designed for ASR (ESTER, REPERE) tend to favor the quantity of lexical terms to the accurate timing of non-speech events. Their programs are mostly composed of news or debates, excluding documentaries, movies, cartoons, musical programs and advertisments.
* Speech resources suited to VAD (AVA-Speech, DI-HARD 2, RATS, LibriParty) do provide more accurate timings but lacks speaker traits (gender, age), speech quality (timbre, ellocution) and non-speech event annotation.
* Speaker recognition corpora provide isolated speaker segments not allowing to evaluate speaker changes, and are generally obtained from interviews using automatic methods (diarization, VAD, active speaker detection) discarding atypical vocal performances or noise conditions (Voxceleb, INA speaker dictionnary, INA diachronic speaker dicionnary).

InaGVAD is aimed at closing the gap between ASR, VAD and speaker corpora and provides :
* fine-grained time-coded speech and non-speech events annotations
* speaker traits (gender, age) and speech quality annotations
* materials representing the diversity of contents that can be found in French TV and radio
* freely available corpus and evaluation code allowing to train and evaluate models

A Voice Activity Detection benchmark based on 6 open-source systems (inaSpeechSegmenter, LIUM_SpkDiarization, Pyannote, Rvad, Silero, SpeechBrain) show InaGVAD generalist TV and music radio categories are more challenging than estimates obtained on AMI, VoxConverse and DIHARD 3 VAD corpora.
A baseline X-vector transfer learning strategy, trained on inaGVAD 1h development set, show that models trained on a single - but diverse - hour of data can achieve competitive SGS results.


## Downloading Audio files

Downloading inaGVAD audio files requires to fill accept its genral term and conditions of use (GCU) and to fill the form available on https://www.ina.fr/institut-national-audiovisuel/research/dataset-project


## Installation

Installing dependencies:
```bash
pip install .
```

## Evaluating Voice Activity Detection (VAD) systems

```
from inaGVAD.vad_metrics import VadEval

vad.evaluation(reference_path, predictions_path, eval_set, eval_type)
```

with :
* `reference_path` : path to inaGVAD github repository local copy (ex: './')
* `destination_path' : directortory containing VAD predictions in csv (severals examples can be found in ./automatic_baselines/*_vad
* `eval_set` : use `dev` or `test` for chosing the evaluation set
* eval_type : use 'global' for obtaining results similar to table 9, 'channel_type' to table 7

The function returns 2 arguments :
* 1st argument is the detailed result per file
* 2nd argument is an aggregate corresponding to inaGVAD's paper tables

## Evaluating Speaker Gender Segmentation (SGS) systems

## Training a new system


## Citing

inaGVAD has been fully described in [a paper](https://aclanthology.org/2024.lrec-main.785) presented at LREC-COLING 2024.
If using this corpus in your research, please cite the following study.

```
@inproceedings{inagvad2024,
    title = "{I}na{GVAD} : A Challenging {F}rench {TV} and Radio Corpus Annotated for Speech Activity Detection and Speaker Gender Segmentation",
    author = "Doukhan, David  and
      Maertens, Christine  and
      Le Personnic, William  and
      Speroni, Ludovic  and
      Dehak, Reda",
    booktitle = "Proceedings of the 2024 Joint International Conference on Computational Linguistics, Language Resources and Evaluation (LREC-COLING 2024)",
    month = may,
    year = "2024",
    address = "Torino, Italia",
    publisher = "ELRA and ICCL",
    url = "https://aclanthology.org/2024.lrec-main.785",
    pages = "8963--8974"
}

```

## CREDITS
Audiovisual archives were provided with the support of French National Audiovisual Institute (INA).
This work has been partially funded by the French National Research Agency (project GEM : Gender Equality Monitor : ANR-19-CE38-0012).
