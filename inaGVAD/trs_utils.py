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


import warnings
from xml.dom.minidom import parse
import pandas as pd


GENDER_SYMB = 'HFI'
AGE_SYMB = 'AES'
QUALITY_SYMB = '-*'
DGENDER = {'H' : 'male', 'F' : 'female', 'I' : 'undefgender'}
DAGE = {'A' : 'adult', 'E' : 'child', 'S' : 'senior'}
DQUAL = {'-' : 'onomatopoeia', '*' : 'atypical', 'S' : 'standard'}
NONSPEECH_LABELS = ['AP', 'BR', 'BH', 'JI', 'MU1', 'MU2', 'RE', 'RI', 'AU']


# Convert transcriber file to raw dataframe
def trs2df_raw(fname):
    # convert transcriber to pandas dataframe
    doc = parse(fname)
    turn = doc.getElementsByTagName('Turn')
    assert len(turn) == 1, len(turn)
    turn = turn[0]
    end = float(turn.getAttribute('endTime'))

    lrec = [[None]]


    for e in turn.childNodes:
        if e.nodeName == '#text':
            txt = e.data.strip()
            lrec[-1].append(txt)
        elif e.nodeName == 'Sync':
            time = float(e.getAttribute('time'))
            lrec[-1].append(time)
            lrec.append([time])
        else:
            raise(NotImplementedError(e.nodeName))

    lrec[-1].append(end)
    lrec.pop(0)

    df = pd.DataFrame.from_records(lrec, columns=['start', 'label', 'stop'])
    df = df[['start', 'stop', 'label']]
    df['dur'] = df.stop - df.start

    return df

# Checking syntax

def seg2str(t):
    return '<segment start=%.1f stop=%.1f label=%s>' % (t.start, t.stop, t.label)

def unknownsymbol(symb, seg):
    raise ValueError('unknown symbol %s in segment %s' % (symb, seg2str(seg)))

def check_dur(seg, dur=0.3):
    if seg.dur <= 0:
        raise ValueError('duration %.3f smaller or equal to 0 seconds for segment %s' % (seg.dur, seg2str(seg)))
    elif seg.dur < dur:
        warnings.warn('duration %.3f smaller than %.3f seconds for segment %s' % (seg.dur, dur, seg2str(seg)))


def check_label(t):
    speech = False
    nonSpeech = False

    for e in t.label.split('+'):
        if e == '':
            continue
        elif len(e) < 2 or len(e) > 3:
            unknownsymbol(e, t)
        elif e[0] in GENDER_SYMB:
            #speech
            if (e[1] not in AGE_SYMB) or (len(e) == 3 and e[2] not in QUALITY_SYMB):
                unknownsymbol(e, t)
            else:
                speech = True
        else:
            if e not in NONSPEECH_LABELS:
                unknownsymbol(e, t)
            else:
                nonSpeech = True
    if speech and nonSpeech:
        raise ValueError('mixing speech and non speech in segment %s' % seg2str(t))


def parse_label(s):
    if s == '':
        return {'EMPT' : True}

    ret = {}
    if '+' in s:
        ret['overlap'] = True
    else:
        ret['overlap'] = False


    if s[0] in GENDER_SYMB:
        ret['voice_activity'] = True

        if len(s) == 2:
            s += 'S'

        for i, (key, dmap) in enumerate([('speaker_gender', DGENDER), ('speaker_age', DAGE), ('speech_quality', DQUAL)]):
            vals = list(set([e[i] for e in s.split('+')]))
            if len(vals) == 1:
                ret[key] = dmap[vals[0]]

    else:
        ret = {}
        for symb in s.split('+'):
            ret[symb] = True

    return ret


def check_df(df):

    ldict = []

    last = None

    for t in df.itertuples():
        # check duration is ok
        check_dur(t)

        # check if 2 adjacent segments have different labels
        if last is not None and last.label == t.label:
            warnings.warn('same label in segments  %s and %s' % (seg2str(last), seg2str(t)))

        #check label syntax
        check_label(t)

        last = t

        ldict.append(parse_label(t.label))
    return pd.DataFrame.from_dict(ldict)





















#def insertimg(fname):
#    return '<img src="{{url_for('static', filename='Hermes.png')}}" align="middle" />'


### CONVERSION TO PYANNOTE ANNOTATIONS

# def trsdf2annotation(df):
#     ### TODO : OVERLAP MANAGEMENT
#     an = Annotation()
#     for t in df.itertuples():
#         if len(t.label) == 0:
#             label = 'noEnergy'
#         elif t.label[0]== 'H':
#             label = 'male'
#         elif t.label[0]== 'F':
#             label = 'female'
#         elif t.label[0] == 'I':
#             label = 'sexe inconnu'
#         elif t.label[:2] == 'MU':
#             label = 'music'
#         else:
#             label = 'noise'

#         an[Segment(t.start, t.stop), 'transcriber'] = label
#     return an.support()




# #### ANNOTATION METRICS

# #def annot2vad(annotation):
# #    tl = Timeline()


# header = """
# <!DOCTYPE html>
# <html>
# <header>
# </header>
# <body>
# """

# footer = """
# </body>
# </html>
# """

# def file_analysis(fname, segmenter):
#     base = os.path.basename(fname)
#     ret = '<H1>%s</H1>' % html.escape(base)
#     try:
#         df = trs2df(fname)
#     except:
#         return ret + colorize('Fichier trs invalide (vide, non trs)', 'red')

#     # + df.to_html()
#     ret += parsedf(df)

#     if '[ER]' in ret:
#         return ret + colorize('*** error in file, skipping automatic analysis ***', 'red')

#     issdf = getiss(base, segmenter)
#     print('issdf', issdf)

#     issannot = iss2annotation(issdf)
#     trsannot = trsdf2annotation(df)

#     ret += dispvid(base)
#     ret += disp(issannot.update(trsannot, copy=True))

#     ret += disp_vad_perf(trsannot, issannot)

#     mfmetric = MFmetric()
#     ret += mfmetric.to_html(trsannot, issannot)

#     return ret
