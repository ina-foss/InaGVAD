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

from pyannote.metrics.base import BaseMetric
from pyannote.metrics.identification import IdentificationErrorRate
from pyannote.metrics.errors.identification import IdentificationErrorAnalysis


class WstpErr(BaseMetric):
    @classmethod
    def metric_name(cls):
        # Return human-readable name of the metric
        return 'women speaking time percentage error'

    @classmethod
    def metric_components(cls):
        # Return component names from which the metric is computed
        return ['rmale', 'rfemale', 'hmale', 'hfemale']

    def compute_components(self, reference, hypothesis, **kwargs):
        # Actually compute the value of each component
        uem = kwargs['uem']
        if uem is not None:
            reference = reference.crop(uem)
            hypothesis = hypothesis.crop(uem)

        components = {'rmale': 0., 'rfemale': 0., 'hmale' : 0., 'hfemale' : 0}

        #print(reference.crop(uem))
        for segment, _, gender in reference.itertracks(yield_label=True):
            if gender == 'undefgender':
                components['rmale'] += .5 * segment.duration
                components['rfemale'] += .5 * segment.duration
            else:
                components['r' + gender] += segment.duration

        for segment, _, gender in hypothesis.itertracks(yield_label=True):
            components['h' + gender] += segment.duration
        return components

    def compute_metric(self, components):
        # Actually compute the metric based on the component values
        r = components['rfemale'] / (components['rfemale'] + components['rmale'])
        h = components['hfemale'] / (components['hfemale'] + components['hmale'])
        return (r - h)

class IdentificationErrorRateLabel(IdentificationErrorRate):
    def __init__(self, label, **kwargs):
        super(IdentificationErrorRateLabel, self).__init__(**kwargs)
        self.label = label
        self.iea  = IdentificationErrorAnalysis(**kwargs)
    def compute_components(self, reference, hypothesis, **kwargs):
        print('compute components', self.label)
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