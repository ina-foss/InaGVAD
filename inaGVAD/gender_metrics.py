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

import os
import numpy as np
import pandas as pd
from pyannote.metrics.base import BaseMetric
from pyannote.metrics.identification import IdentificationErrorRate
from pyannote.metrics.errors.identification import IdentificationErrorAnalysis
from pyannote.core import Annotation, Timeline, Segment



class WstpErr(BaseMetric):
    @classmethod
    def metric_name(cls):
        # Return human-readable name of the metric
        return 'WSTP error'

    @classmethod
    def metric_components(cls):
        # Return component names from which the metric is computed
        return ['ref_male_dur', 'ref_female_dur', 'hyp_male_dur', 'hyp_female_dur']

    def compute_components(self, reference, hypothesis, **kwargs):
        # Actually compute the value of each component
        uem = kwargs['uem']
        if uem is not None:
            reference = reference.crop(uem)
            hypothesis = hypothesis.crop(uem)

        components = self.init_components()
        #components = {'rmale': 0., 'rfemale': 0., 'hmale' : 0., 'hfemale' : 0}

        #print(reference.crop(uem))
        for segment, _, gender in reference.itertracks(yield_label=True):
            if gender == 'undefgender':
                components['ref_male_dur'] += .5 * segment.duration
                components['ref_female_dur'] += .5 * segment.duration
            else:
                components['ref_' + gender + '_dur'] += segment.duration

        for segment, _, gender in hypothesis.itertracks(yield_label=True):
            components['hyp_' + gender + '_dur'] += segment.duration
        return components

    def compute_metric(self, components):
        # Actually compute the metric based on the component values
        tot_ref = components['ref_female_dur'] + components['ref_male_dur']
        tot_hyp = components['hyp_female_dur'] + components['hyp_male_dur']

        if tot_ref == 0 and tot_hyp == 0:
            return 0

        if tot_ref > 0:
            r = components['ref_female_dur'] / tot_ref
        else:
            r = .5
        if tot_hyp > 0:
            h = components['hyp_female_dur'] / tot_hyp
        else:
            h = .5
        return (r - h)

class IdentificationErrorRateLabel(IdentificationErrorRate):
    def __init__(self, label, **kwargs):
        super(IdentificationErrorRateLabel, self).__init__(**kwargs)
        self.label = label
        self.iea  = IdentificationErrorAnalysis(**kwargs)
    def compute_components(self, reference, hypothesis, **kwargs):
        uem = kwargs['uem']
        andiff = self.iea.difference(reference, hypothesis, uem=uem)

        # ['total', 'correct', 'false alarm', 'missed detection', 'confusion']
        components = self.init_components()
        #dict([(e, 0.) for e in self.metric_components()])

        for segment, _, label in andiff.itertracks(yield_label=True):
            status, ref, hyp = label
            dur = segment.duration
            if status in ['correct', 'missed detection', 'confusion'] and ref == self.label:
                components['total'] += dur
            if status in ['correct', 'missed detection'] and ref == self.label:
                components[status] += dur
            elif status in ['false alarm', 'confusion'] and hyp == self.label:
                components[status] += dur

        return components


global_metrics_map = [
  (('IER', 'identification error rate', '%'), ('Global Metrics', 'IER')),
  ('WSTP_RMSE',  ('Global Metrics', 'Wrms')),
  (('WSTP', 'WSTP error', '%'),  ('Global Metrics', 'Werr'))]

genderdetail_metrics_map = global_metrics_map + [
  (('IER Female', 'identification error rate', '%'), ('Female Metrics', 'IER')),
  (('IER Female', 'correct', '%'), ('Female Metrics', 'recall')),
  (('IER Female', 'false alarm', '%'), ('Female Metrics', 'false alarms')),
  (('IER Female', 'missed detection', '%'), ('Female Metrics', 'missed detections')),
  (('IER Female', 'confusion', '%'), ('Female Metrics', 'confusion')),
  (('IER Male', 'identification error rate', '%'), ('Male Metrics', 'IER')),
  (('IER Male', 'correct', '%'), ('Male Metrics', 'recall')),
  (('IER Male', 'false alarm', '%'), ('Male Metrics', 'false alarms')),
  (('IER Male', 'missed detection', '%'), ('Male Metrics', 'missed detections')),
  (('IER Male', 'confusion', '%'), ('Male Metrics', 'confusion'))]

def df2annot(df, col, rmnan=True, uri=None):
    an = Annotation(uri=uri)
#    print('df2annot', df)
    for start, stop, val in zip(df.start, df.stop, df[col]):
        if rmnan and val != val:
            continue
        seg = Segment(start, stop)
        an[seg] = val
    return an.support()


def init_uem(df):
    uem = Timeline()
    uem.add(Segment(df.start[0], df.stop[len(df) - 1]))
    return uem


def rm_uem(uem, df, col, rmlist):
    for start, stop, val in zip(df.start, df.stop, df[col]):
        if val in rmlist:
            uem = uem.extrude(Segment(start, stop))
    return uem

def keep_uem(uem, df, col, keeplist):
    for start, stop, val in zip(df.start, df.stop, df[col]):
        if val not in keeplist:
            uem = uem.extrude(Segment(start, stop))
    return uem


class GenderEval:
    def __init__(self, collar=.3):
        #self.annotmapper = AnnotMapper(corpus_path, 'detailed.csv')
        #self.devdf = pd.read_csv('%s/inaGVAD_dev_metadata.csv' % corpus_path)
        #self.testdf = pd.read_csv('%s/inaGVAD_test_metadata.csv' % corpus_path)
        self.wstp = WstpErr()
        self.ier = IdentificationErrorRate(collar=collar)        
        self.ierF = IdentificationErrorRateLabel('female', collar=collar)
        self.ierM = IdentificationErrorRateLabel('male', collar=collar)
        
    def __call__(self, fref, fpred):
        
        uri = os.path.basename(fref).split('.')[0]
        
        # parse reference
        dfref = pd.read_csv(fref)
        anref = df2annot(dfref, 'speaker_gender', uri = uri)
        uem = init_uem(dfref)
        uem = rm_uem(uem, dfref, 'speaker_gender', ['undefgender'])
        #print('main uem', uem)
        #print(uem)
        
        # parse prediction
        dfpred = pd.read_csv(fpred)
        #print('dfpred', dfpred)
        if len(dfpred) > 0:
            dfpred = dfpred[dfpred.label.map(lambda x: x in ['male', 'female'])]
        anpred = df2annot(dfpred, 'label', uri = uri)
            
        wstp = self.wstp(anref, anpred, uem=None)
        
        ier = self.ier(anref, anpred, uem=uem)
        errF = self.ierF(anref,anpred,uem=uem)
        errM = self.ierM(anref,anpred,uem=uem)
        
        return wstp, ier, errF, errM
    
    def reset(self):
        self.wstp.reset()
        self.ier.reset()
        self.ierF.reset()
        self.ierM.reset()
        
    def report(self):
        wstp = self.wstp.report()
        wstp.columns = [('WSTP', e1, e2) for e1, e2 in wstp.columns]
        ier = self.ier.report()
        ier.columns = [('IER', e1, e2) for e1, e2 in ier.columns]
        ierF = self.ierF.report()
        ierF.columns = [('IER Female', e1, e2) for e1, e2 in ierF.columns]
        ierM = self.ierM.report()
        ierM.columns = [('IER Male', e1, e2) for e1, e2 in ierM.columns]
        return wstp.join(ier).join(ierF).join(ierM)
        
#        if onlypercent:
#            ret = ret[[k for k in ret if k[2] == '%']]
#            ret.columns = [(e1, e2) for (e1, e2, e3) in ret]
#        return ret

    def compare_lfiles(self, lref, lhyp, simplify=None):
#        assert(simplify in [None, 'onlypercent', 'genderdetail', 'gender', ''])

        for ref, hyp in zip(lref, lhyp):
            self(ref, hyp)
        ret = self.report()
        self.reset()
        return ret
        
#        if simplify == 'only percent':
#            ret = ret[[k for k in ret if k[2] == '%']]
#            ret.columns = [(e1, e2) for (e1, e2, e3) in ret]

    
    def compare_category(self, ref_dir, pred_dir, criterion, csvfname):
        df = pd.read_csv(csvfname)
        lret = []
        #ldf = []
        #dret = {}
        ltotal = []
        
        for k, sdf in df.groupby(criterion):
            src = sdf.apply(lambda x: '%s/annotations/detailed_csv/%s.csv' % (ref_dir, x['fileid']), axis=1)
            dst = sdf.fileid.map(lambda x: '%s/%s.csv' % (pred_dir, x))
            
            ret = self.compare_lfiles(src, dst)

            # remove total from result
            dtotal = ret.tail(1).to_dict(orient='records')[0]    
            ret = ret[:(len(ret) - 1)]
            lret.append(ret)
  
            if isinstance(criterion, list):
                for i, key in enumerate(criterion):
                    dtotal[key] = k[i]
            else:
                dtotal[criterion] = k

            dtotal['nbfile'] = len(ret)
            wstp = ret[('WSTP', 'WSTP error', '%')]
            dtotal['WSTP_RMSE'] = np.sqrt(np.mean(wstp ** 2))
            
            ltotal.append(dtotal)

        details = df.join(pd.concat(lret), on='fileid')
        return details, pd.DataFrame.from_dict(ltotal).set_index(criterion)
    
    def global_eval(self, ref_dir, pred_dir, csvfname):

        df = pd.read_csv(csvfname)
        src = df.apply(lambda x: '%s/annotations/detailed_csv/%s.csv' % (ref_dir, x['fileid']), axis=1)
        dst = df.fileid.map(lambda x: '%s/%s.csv' % (pred_dir, x))

        ret = self.compare_lfiles(src, dst)
        #print(ret)

        dtotal = ret.tail(1).to_dict(orient='records')[0]
        ret = ret[:(len(ret) - 1)]

        dtotal['nbfile'] = len(ret)
        wstp = ret[('WSTP', 'WSTP error', '%')]
        dtotal['WSTP_RMSE'] = np.sqrt(np.mean(wstp ** 2))

        details = df.join(ret, on='fileid')
        return details, dtotal


    def evaluation(self, reference_path, predictions_path, eval_set, gender_detail, chancategory_detail):
        if eval_set in ['dev', 'test']:
            csvfname = '%s/annotations/filesplit/%sset.csv' % (reference_path, eval_set)
        elif eval_set == 'all':
            csvfname = '%s/annotations/filesplit/all.csv' % (reference_path)
        else:
            raise Exception('eval_set argument must be in {dev, test, all} for chosing evaluation set. Paper results are obtained on test set')
        assert os.path.exists(csvfname), '%s is a bad annotation reference_path : should be of the form <inaGVAD git repos path>' % reference_path

        #assert eval_type in ['global', 'gender_detail', 'channel_type'], '"%s" is not a valid eval_type argument : should be "global", "channel_type", "gender_detail"' % eval_type
        assert gender_detail in [True, False]
        if gender_detail:
            lmetricmap = genderdetail_metrics_map
        else:
            lmetricmap = global_metrics_map

        assert chancategory_detail in [True, False]
        dret = {}
        if chancategory_detail:
            details, categories = self.compare_category(reference_path, predictions_path, ['channel_category'], csvfname)
            for chancat in ['generalist_radio', 'music_radio', 'generalist_tv', 'news_tv']:
                for oldname, newname in lmetricmap:
                    dret[(chancat, *newname)] = categories[oldname][chancat]
        else:
            details, categories = self.global_eval(reference_path, predictions_path, csvfname)
            for oldname, newname in lmetricmap:
                dret[newname] = categories[oldname]
        return details, dret
