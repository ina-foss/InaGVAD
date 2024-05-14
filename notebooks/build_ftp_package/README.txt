# inaGVAD : a Challenging French TV and Radio Corpus annotated for Speech Activity Detection and Speaker Gender Segmentation
Last update : 2024/05/14

## IMPORTANT ACRONYMS
VAD : Voice Activity Detection
SGS : Speaker Gender Segmentation
IER : Identification Error Rate
WSTP : Women Speaking Time Percentage
UEM : NIST Unpartitioned Evaluation Map (UEM) format define audio regions that systems must process

## Detailed Corpus description

inaGVAD corpus has been fully described in the following paper :

@inproceedings{inagvad2024,
title={InaGVAD : a Challenging French TV and Radio Corpus annotated for Speech Activity Detection and Speaker Gender Segmentation},
author={David Doukhan and Christine Maertens and William {Le Personnic} and Ludovic Speroni and Reda Dehak},
booktitle={Joint International Conference on Computational Linguistics, Language Resources and Evaluation (LREC-COLING)},
year={2024},
}


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
* .vad.csv : Voice Activity Detection annotations in csv with fields start time (seconds), stop time (seconds) and label in {"speech", "non speech"}
* .sgs.csv : Speaker Gender Segmentation annotations in csv with fields start time (seconds), stop time (seconds) and label in {"male", "female"}. To be used for training speaker gender prediction systems or obtaining IER SGS evaluation metrics. Warning : several phenomena are discared from these annotation exports : non speech events, speakers with unknown gender, overlapped speech involving speakers with different perceived gender.
* .sgs.uem : portions of annotated files to be used for obtaining IER SGS evaluation metrics : excluding speakers with unknown percieved gender or overlapped speech involving speakers with different genders.
* detailed.csv : detailed CSV annotations used to obtain WSTP evaluation metrics and corpus description statistics with fields :
    * label (full annotated label)
    * start time (seconds)
    * stop time (seconds)
    * voice_activity (True if spoken voice, else False)
    * overlap (True if speech overlap, else False)
    * gender in {"male", "female", "undefgender" (no percieved gender or speech overlap between speakers of different gender)}
    * age in {"adult", "senior", "child", "undefage" (no percieved age or speech overlap between speakers of different ages)}
    * speech_quality in {"standard", "onomatopoeia", "atypical", "undefquality" (speech overlap between different speech qualities)}

## Citing

Please cite this work if using this corpus in a publication :

@inproceedings{inagvad2024,
title={InaGVAD : a Challenging French TV and Radio Corpus annotated for Speech Activity Detection and Speaker Gender Segmentation},
author={David Doukhan and Christine Maertens and William {Le Personnic} and Ludovic Speroni and Reda Dehak},
booktitle={Joint International Conference on Computational Linguistics, Language Resources and Evaluation (LREC-COLING)},
year={2024},
}

## Questions or issues

Questions or issues related to this corpus could be asked from the github repository (best): https://github.com/ina-foss/InaGVAD/issues
Another option is to contact David Doukhan : ddoukhan@ina.fr

## Acknowledgements
This work has been partially funded by the French National Research Agency (project Gender Equality Monitor - ANR-19-CE38-0012).
