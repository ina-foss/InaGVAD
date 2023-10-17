#!/usr/bin/python3

import os
import sys
import torch
import logging
import pickle
import json
import glob
import shutil
import sklearn
import numpy as np
import speechbrain as sb
from tqdm.contrib import tqdm
import pandas as pd
from hyperpyyaml import load_hyperpyyaml
from speechbrain.utils.distributed import run_on_main
from speechbrain.processing.PLDA_LDA import StatObject_SB
from speechbrain.processing import diarization as diar
from speechbrain.utils.DER import DER
from speechbrain.dataio.dataio import read_audio
from speechbrain.dataio.dataio import read_audio_multichannel
from data import DATA_split
from speechbrain.processing.diarization import merge_ssegs_same_speaker, distribute_overlap

# Logger setup
logger = logging.getLogger(__name__)
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(current_dir))

SAMPLERATE = 16000

def get_subsegments(seg, max_subseg_dur=3.0, overlap=1.5):
    """Divides bigger segments into smaller sub-segments
    """

    shift = max_subseg_dur - overlap
    subsegments = []

    seg_dur = seg.stop - seg.start
    if seg_dur > max_subseg_dur:
        num_subsegs = int(seg_dur / shift)
        # Now divide this segment in smaller subsegments
        for i in range(num_subsegs):
            subseg_start = seg.start + i * shift
            subseg_end = min(subseg_start + max_subseg_dur - 0.01, seg.stop)
            subseg_dur = subseg_end - subseg_start
            
            subsegments.append([subseg_start, subseg_end])
            # Break if exceeding the boundary
            if subseg_end >= seg.stop:
                break
    else:
        subsegments.append([seg.start, seg.stop])

    return subsegments


def vadreadcsv(fname):
    """
    read csv with fields start, stop, label
    """
    df = pd.read_csv(fname)
    
    return df

def prepare_metadata(vadfname, fname, max_subseg_dur, overlap):
        
    # For each speech segments and perform subsegmentation
    # Create JSON from subsegments
    json_dict = {}
    for seg in vadreadcsv(vadfname).itertuples():
        if seg.label != "nospeech":
            subsegs = get_subsegments(seg, max_subseg_dur, overlap)
            for r in subsegs:
                strt = str(round(float(r[0]), 4))
                end  = str(round(float(r[1]), 4))
                subsegment_ID = fname + "_" + seg.label + "_" + strt + "_" + end
                dur = float(end) - float(strt)
                start_sample = int(float(strt) * SAMPLERATE)
                end_sample = int(float(end) * SAMPLERATE)
                json_dict[subsegment_ID] = {
                    "wav": {
                        "file_name": fname,
                        "label" : seg.label,
                        "duration": float(dur),
                        "start": int(start_sample),
                        "stop": int(end_sample),
                    },
                }
        
    return json_dict

def prepare_data(
    data_folder,
    segdevDATA_folder,
    vad_folder,
    save_folder,
    max_subseg_dur=3.0,
    overlap=1.5,
):
    # JSON files
    jsonfiles = [
        os.path.join(save_folder, "dev.subsegs.json"),
        os.path.join(save_folder, "eval.subsegs.json"),
    ]
    
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
    
    msg = "\tCreating json-data files."
    logger.debug(msg)
    
    # Get the split
    splits = ["dev", "eval"]
    dev_set, eval_set = DATA_split()
    
    # process dev dataset
    json_dict = {}
    for file in dev_set:
        fname = file
        vadfname = segdevDATA_folder + "/" + file + '.csv'
        json_dict.update(prepare_metadata(vadfname, fname, max_subseg_dur, overlap))
    
    with open(jsonfiles[0], mode="w") as json_f:
        json.dump(json_dict, json_f, indent=2)
        
    print("eval json ids:", len(json_dict))
    
    # process test dataset
    json_dict = {}
    for file in eval_set:
        fname = file
        vadfname = vad_folder + "/" + file + '.csv'
        json_dict.update(prepare_metadata(vadfname, fname, max_subseg_dur, overlap))
    
    with open(jsonfiles[1], mode="w") as json_f:
        json.dump(json_dict, json_f, indent=2)
    
    print("test json ids:", len(json_dict))

def dataio_prep(hparams, json_file):
    """Creates the datasets and their data processing pipelines.
    """

    # 1. Datasets
    data_folder = hparams["data_folder"]
    dataset = sb.dataio.dataset.DynamicItemDataset.from_json(
        json_path=json_file, replacements={"data_root": data_folder},
    )

    # 2. Read Audio files
    @sb.utils.data_pipeline.takes("wav")
    @sb.utils.data_pipeline.provides("sig")
    def audio_pipeline(wav):
        sig = read_audio(params["wav_folder"] + "/" + wav["file_name"] + ".wav")
        return sig[wav["start"]:wav["stop"]]

    sb.dataio.dataset.add_dynamic_item([dataset], audio_pipeline)

    # 3. Set output:
    sb.dataio.dataset.set_output_keys([dataset], ["id", "sig"])

    # 4. Create dataloader:
    dataloader = sb.dataio.dataloader.make_dataloader(
        dataset, **params["dataloader_opts"]
    )

    return dataloader

def compute_embeddings(wavs, lens):
    """Definition of the steps for computation of embeddings from the waveforms."""
    with torch.no_grad():
        wavs = wavs.to(run_opts["device"])
        feats = params["compute_features"](wavs)
        feats = params["mean_var_norm"](feats, lens)
        emb = params["embedding_model"](feats, lens)
        emb = params["mean_var_norm_emb"](
            emb, torch.ones(emb.shape[0], device=run_opts["device"])
        )

    return emb

def embedding_computation_loop(data_loader, emb_fname):
    """Extracts embeddings for a given dataset loader."""

    # Note: We use speechbrain.processing.PLDA_LDA.StatObject_SB type to store embeddings.
    # Extract embeddings (skip if already done).
    if not os.path.isfile(emb_fname):
        logger.debug("Extracting embeddings")
        embeddings = np.empty(shape=[0, params["emb_dim"]], dtype=np.float64)
        modelset = []
        segset = []

        # Different data may have different statistics.
        params["mean_var_norm_emb"].count = 0

        for batch in data_loader:
            ids = batch.id
            wavs, lens = batch.sig

            mod = [x for x in ids]
            seg = [x for x in ids]
            modelset = modelset + mod
            segset = segset + seg

            # Embedding computation.
            emb = (
                compute_embeddings(wavs, lens)
                .contiguous()
                .squeeze(1)
                .cpu()
                .numpy()
            )
            embeddings = np.concatenate((embeddings, emb), axis=0)

        modelset = np.array(modelset, dtype="|O")
        segset = np.array(segset, dtype="|O")

        # Intialize variables for start, stop and stat0.
        s = np.array([None] * embeddings.shape[0])
        b = np.array([[1.0]] * embeddings.shape[0])

        stat_obj = StatObject_SB(
            modelset=modelset,
            segset=segset,
            start=s,
            stop=s,
            stat0=b,
            stat1=embeddings,
        )
        logger.debug("Saving Embeddings...")
        stat_obj.save_stat_object(emb_fname)
        print(embeddings.shape)

    else:
        logger.debug("Skipping embedding extraction (as already present).")
        logger.debug("Loading previously saved embeddings.")

        with open(emb_fname, "rb") as in_file:
            stat_obj = pickle.load(in_file)

    return stat_obj
    
def extract_embeddings(output_dir):
    params["embedding_model"].eval()
           
    # Putting modules on the device.
    params["compute_features"].to(run_opts["device"])
    params["mean_var_norm"].to(run_opts["device"])
    params["embedding_model"].to(run_opts["device"])
    params["mean_var_norm_emb"].to(run_opts["device"])
    
    ## DEV dataset
    # File to store embeddings.
    emb_fname = os.path.join(output_dir, "embedding_devset.stat")
    devdata_loader = dataio_prep(params, os.path.join(params['output_folder'], "dev.subsegs.json"))
    # Compute Embeddings.
    embDevSet_obj = embedding_computation_loop(devdata_loader, emb_fname)
    
    ## TEST dataset
    # File to store embeddings.
    emb_fname = os.path.join(output_dir, "embedding_testset.stat")
    evaldata_loader = dataio_prep(params, os.path.join(params['output_folder'], "eval.subsegs.json"))
    # Compute Embeddings.
    embEvalSet_obj = embedding_computation_loop(evaldata_loader, emb_fname)
    return embDevSet_obj, embEvalSet_obj, devdata_loader, evaldata_loader

from sklearn.svm import SVC
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

def extractlabelsstartstop(listid):
    files = []
    labels = []
    segs = []
    for id in listid:
        splitted = id.rsplit("_", 3)
        files.append(str(splitted[0]))
        labels.append(str(splitted[1]))
        segs.append((float(splitted[2]),float(splitted[3])))
        
    return files, labels, segs

def write_csv_segmentation(ll, filename):
    with open(filename, "w") as f:
        f.write("label,start,stop\n")
        for row in ll:
            line_str = ",".join([str(row[3]), str(row[1]), str(row[2])])
            f.write("%s\n" % line_str)

def perform_SVM_clustering(devembs, tstembs, output_dir):

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    clf = make_pipeline(StandardScaler(), SVC(gamma='auto'))
    _, devlabels, _ = extractlabelsstartstop(devembs.modelset)
    clf.fit(devembs.stat1, devlabels)
    
    # Perform SVM Classification on test data embeddings
    labels = clf.predict(tstembs.stat1)
    files, _, segs = extractlabelsstartstop(tstembs.modelset)
    
    lol = []

    for i in range(labels.shape[0]):
        subseg = segs[i]
        a = [files[i], subseg[0], subseg[1], labels[i]]
        lol.append(a)
    
        
    _, eval_set = DATA_split()
    for f in eval_set:
        lol1 = list(filter(lambda x : x[0] == f, lol))
    
        if len(lol1) != 0:
            # Sorting based on start time of sub-segment
            lol1.sort(key=lambda x: float(x[1]))
    
            # Merge and split in 2 simple steps: (i) Merge sseg of same speakers then (ii) split different speakers
            # Step 1: Merge adjacent sub-segments that belong to same speaker (or cluster)
            lol1 = merge_ssegs_same_speaker(lol1)

            # Step 2: Distribute duration of adjacent overlapping sub-segments belonging to different speakers (or cluster)
            # Taking mid-point as the splitting time location.
            if len(lol1) > 1:
                lol1 = distribute_overlap(lol1)
    
        #write segmentation
        write_csv_segmentation(lol1, output_dir + "/" + f + ".csv")
    
# Begin experiment!
if __name__ == "__main__":
    # Load hyperparameters file with command-line overrides.
    params_file, run_opts, overrides = sb.core.parse_arguments(sys.argv[1:])

    with open(params_file) as fin:
        params = load_hyperpyyaml(fin, overrides)
        
    # Create experiment directory.
    sb.core.create_experiment_directory(
        experiment_directory=params["output_folder"],
        hyperparams_to_save=params_file,
        overrides=overrides,
    )

    # Few more experiment directories inside results/ (to maintain cleaner structure).
    exp_dirs = [
        params["embedding_dir"],
        params["seg_dir"],
    ]
    for dir_ in exp_dirs:
        if not os.path.exists(dir_):
            os.makedirs(dir_)
            
    # We download the pretrained Model from HuggingFace (or elsewhere depending on
    # the path given in the YAML file).
    run_on_main(params["pretrainer"].collect_files)
    params["pretrainer"].load_collected(device=run_opts["device"])
    params["embedding_model"].eval()
    params["embedding_model"].to(run_opts["device"])
    
    # Prepare Dev and Test Json file the DATA
    prepare_data(params['wav_folder'], params['segdev_folder'], params['vad_folder'], params['output_folder'])
    
    embDevSet_obj, embEvalSet_obj, _, _ = extract_embeddings(params['embedding_dir'])
    
    perform_SVM_clustering(embDevSet_obj, embEvalSet_obj, params['seg_dir'])
