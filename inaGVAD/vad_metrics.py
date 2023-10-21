#!/usr/bin/env python
# encoding: utf-8

# The MIT License

# Copyright (c) 2023 Ina (David Doukhan - http://www.ina.fr/)

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import glob
import pandas as pd
from os.path import splitext, basename
from pyannote.core import Annotation, Timeline, Segment
from pyannote.metrics.detection import DetectionAccuracy, DetectionPrecisionRecallFMeasure

def csv2annot(fname):
    """
    Convert a csv with fields start, stop, label to pyannote annotation
    """
    df = pd.read_csv(fname)
    an = Annotation(uri=basename(splitext(fname)[0]))
    for t in df.itertuples():
        an[Segment(t.start, t.stop)] = t.label
    return an

def annot2vad(annot):
    tl = Timeline()
    for seg, track, label in annot.itertracks(yield_label=True):
        if label in ['male', 'female', 'speech']:
            tl.add(seg)
    return tl.support().to_annotation()

class VadEval:
    def __init__(self, collar):
        self.da = DetectionAccuracy(collar=collar)
        self.dprf = DetectionPrecisionRecallFMeasure(collar=collar)

    def reset(self):
        self.da.reset()
        self.dprf.reset()
   
    def __call__(self, ref, pred, uem, fileid='', reset=True):
        comp = self.da.compute_components(ref, pred, uem=uem)
        comp.update(self.dprf.compute_components(ref, pred, uem=uem))
        comp['fileid'] = fileid
        comp['accuracy'] = self.da.compute_metric(comp)
        prf = self.dprf.compute_metrics(comp)
        for i, name in [(0, 'precision'), (1, 'recall'), (2, 'fmeasure')]:
            comp[name] = prf[i]
        if reset:
            self.reset()
        return comp
    
    def compare_csv(self, ref_csv, pred_csv, reset=False):
        base, _ = splitext(basename(ref_csv))
        refannot = csv2annot(ref_csv)
        uem = refannot.get_timeline().support()
        ref = annot2vad(refannot)
        pred = annot2vad(csv2annot(pred_csv))
        return self(ref, pred, uem, base, reset=reset)
    
    def compare_lfiles(self, lref, lpred, reset=True):
        """
        return detailed dataframe + global metrics
        """
        dret = [self.compare_csv(ref, pred, reset=False) for ref, pred in zip(lref, lpred)]
        df = pd.DataFrame.from_dict(dret)
        dfsum = df.sum()
        ret = {'accuracy' : self.da.compute_metric(dfsum)}
        ret['precision'], ret['recall'], ret['fmeasure'] = self.dprf.compute_metrics(dfsum)
        if reset:
            self.reset()
        return df, ret
    
    def compare_directories(self, ref_dir, pred_dir, verbose=False, reset=True):
        lref = sorted(glob.glob(ref_dir + '/*.csv'))
        lpred = ['%s/%s' % (pred_dir, basename(ref)) for ref in lref]
        return self.compare_lfiles(lref, lpred, reset=reset)
    
    def compare_category(self, pred_dir, criterion, csvfname='./VAD_results_extended.csv'):

        df = pd.read_csv(csvfname)
        lret = []
        ldf = []
        
        for k, sdf in df.groupby(criterion):
            src = sdf.fileid.map(lambda x: './annotations/vad/%s.csv' % x)
            dst = sdf.fileid.map(lambda x: '%s/%s.csv' % (pred_dir, x))
            dfdetail, dret = self.compare_lfiles(src, dst)
            d = {'category': k}
            d.update(dret)
            dfdetail['category'] = k
            ldf.append(dfdetail)
            lret.append(d)
            self.reset()
        return pd.concat(ldf), pd.DataFrame.from_dict(lret)

    def compare_csvset(self, pred_dir, csvfname='./VAD_results_extended.csv'):

        df = pd.read_csv(csvfname)
        src = df.fileid.map(lambda x: './annotations/vad/%s.csv' % x)
        dst = df.fileid.map(lambda x: '%s/%s.csv' % (pred_dir, x))
        dfdetail, dret = self.compare_lfiles(src, dst)
        self.reset()
        return dfdetail, dret