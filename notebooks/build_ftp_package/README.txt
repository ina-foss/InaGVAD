# inaGVAD : a Challenging French TV and Radio Corpus annotated for Speech Activity Detection and Speaker Gender Segmentation
Last update : 2024/05/14

## IMPORTANT ACRONYMS
VAD : Voice Activity Detection
SGS : Speaker Gender Segmentation

## Download instructions
* Evaluation code is hosted on github : https://github.com/ina-foss/InaGVAD
* Corpus audio files can be donwloaded through INA's website : https://www.ina.fr/institut-national-audiovisuel/research/dataset-project

## Filetree

inaGVAD
|- inaGVAD_devset.lst : list of 60 file identifiers to be used as dev set
|- inaGVAD_testset.lst : list of 217 file identifiers to be used as test set
|- METADATA.csv : meta data associated to each annotated file:
    * fileid : file identifier with syntax <media>-<channel code>-<broadcast time (HHMMSS)>
    * media : "tv" or "radio" (inferred from fileid)
    * channel_code : 3 characters corresponding to INA's channel code (inferred from fileid)
    * channel_name : full channel name (human friendly)
    * channel_category : 4 options : "music_radio" (challenging), "generalist_radio" (easy), "news_tv" (easy), "generalist_tv" (challenging)
    * broadcast_hour : broadcast time hour (inferred from fileid)
    * set : "dev" if in the dev set, "test" if in the test set
|- dev : audio files and annotations corresponding to dev set
|- test : audio files and annotations corresponding to test set


Files in dev and test directories correspond to 1-minute long recordings, with syntax <fileid>.<extension> .
e.g. : tv-F24-042912.sgs.uem

5 extensions are provided : 
* .wav : 16 000 Hz mono wav audio file
* .vad.csv : Voice Activity Detection annotation in csv with fields start time (seconds), stop time (seconds) and label in {"speech", "non speech"}
*



## Citing

Please cite this work if using this corpus in a publication :

@inproceedings{inagvad2024,
title={InaGVAD : a Challenging French TV and Radio Corpus annotated for Speech Activity Detection and Speaker Gender Segmentation},
author={David Doukhan and Christine Maertens and William {Le Personnic} and Ludovic Speroni and Reda Dehak},
booktitle={Joint International Conference on Computational Linguistics, Language Resources and Evaluation (LREC-COLING)},
year={2024},
}

## Acknowledgements
This work has been partially funded by the French National Research Agency (project Gender Equality Monitor - ANR-19-CE38-0012).
