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


from xml.dom.minidom import parse
import pandas as pd


import html
# import os
# import re

# from  pyannote.core import Segment, Annotation
# from pyannote.core.notebook import Notebook

# #import pylab as plt
# from matplotlib.figure import Figure
# import base64
# from io import BytesIO

# #from flask import url_for

# from metrics import disp_vad_perf, MFmetric



def trs2df(fname):
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

def seg2str(t):
    return html.escape('<segment début=%.3f fin=%.3f texte=%s>' % (t.start, t.stop, t.label))

def colorize(s, color):
    return '<p style="color:%s;">%s</p>' % (color, s)

def unknownsymbolmsg(symb, seg):
    msg = '[ER] : symbole inconnu %s dans segment %s' % (symb, seg)
    return colorize(msg, 'red')

def checklabel(t):    
    
    lerr = []
    speech = False
    nonSpeech = False
    
    for e in t.label.split('+'):
        if e == '':
            continue
        elif len(e) < 2 or len(e) > 3:
            lerr.append(unknownsymbolmsg(e, seg2str(t)))
        elif e[0] in 'HFI':
            #speech
            if (e[1] not in 'AES') or (len(e) == 3 and e[2] not in '-*'):
                lerr.append(unknownsymbolmsg(e, seg2str(t)))
            else:
                speech = True
        else:
            if e not in ['AP', 'BR', 'BH', 'JI', 'MU1', 'MU2', 'RE', 'RI', 'AU']:
                lerr.append(unknownsymbolmsg(e, seg2str(t)))
            else:
                nonSpeech = True
    if speech and nonSpeech:
        msg = '[ER] : mélange parole et non parole dans segment %s' % (seg2str(t))
        lerr.append(colorize(msg, 'red'))
    return lerr

def check_dur(seg, dur=0.3):
    ret = []
    if seg.dur <= 0:
        msg = '[ER] durée %.3f inférieure à 0 s pour %s' % (seg.dur, seg2str(seg))
        ret  = [colorize(msg, 'red')]
    elif seg.dur < dur:
        msg = '[WD] durée %.3f inférieure à %.3f s pour %s' % (seg.dur, dur, seg2str(seg))
        ret  = [colorize(msg, 'green')]
    return ret

def cmp2last(last, cur):
    if last is not None and last.label == cur.label:
        msg = '[WM] même texte pour segments %s et %s' % (seg2str(last), seg2str(cur))
        return [colorize(msg, 'blue')]
    return []
    
    

def parsedf(df):
    lmsg = []
#    error = False
    last = None
    
    for t in df.itertuples():
        lmsg += check_dur(t)
        lmsg += cmp2last(last, t)
        errs = checklabel(t)
        lmsg += errs
#        if len(errs) != 0:
#            error = True
        last = t
    return ''.join(lmsg)

#segmenter = None

# def validfname(fname):
#     msg = colorize("MAUVAIS NOM DE FICHIER %s. L'avez-vous renommé ?" % fname, 'red')
#     try:
#         base, ext = os.path.splitext(fname)
#         media, chan, tc, dur = base.split('-')
#     except:
#         return msg
#     #print(ext, chan, media,tc, dur)
#     if ext != '.trs' or (media not in ['tv', 'radio']) or len(chan) != 3 or dur != '60':
#         return msg
#     #print('re')
#     if not re.match('^[0-9]{8}T[0-9]{6}$', tc):
#         return msg
#     return ''


# def trs2wav(trsname, outdir):
#     base = os.path.splitext(os.path.basename(trsname))[0]
#     dst = '%s/%s.wav' % (outdir, base)
#     if os.path.exists(dst):
#         return 0
#     url = "http://collgate.ina.fr:81/collgate.dlweb/get/%s/%s/%s/%s/?download&format=ts_audio" % tuple(base.split('-'))
#     ret = os.system("ffmpeg -i '%s' -ar 16000 -ac 1 '%s'" % (url, dst))
#     return ret
    

# def getiss(fname, segmenter):

#     base = os.path.splitext(fname)[0]
        
#     dst = './iss/%s.csv' % base
#     url = "http://collgate.ina.fr:81/collgate.dlweb/get/%s/%s/%s/%s/?download&format=ts_audio" % tuple(base.split('-'))
        
#     if not os.path.exists(dst):
#         try:
#             print('iss url', url)
#             seg = segmenter(url)
#             print('seg', seg)
#             print('dst', dst)
#             seg2csv(seg, dst)
#             print('csvexport')
#         except:
#             return 'INASPEECHSEGMENTER EXCEPTION'
        
#     return pd.read_csv(dst, sep='\t')

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


# def iss2annotation(df):
#     an = Annotation()
#     for t in df.itertuples():
#         an[Segment(t.start, t.stop), 'ISS'] = t.labels
#     return an


# def disp(annotation):#base, issdf, manualdf):
# #    an = Annotation()
# #    for t in issdf.itertuples():
# #        an[Segment(t.start, t.stop), 'iss'] = t.labels
# #    for t in issdf.itertuples():
# #        an[Segment(t.start, t.stop), 'manual'] = t.labels

#     fig = Figure(figsize = (15, 3.5))
#     ax = fig.subplots()
#     n = Notebook()
#     ax = n.setup(ax=ax)
#     n.plot_annotation(annotation, ax=ax)
    
#     buf = BytesIO()
#     fig.savefig(buf, format='png')
#     #fig.savefig(buf, format='svg')
#     data = base64.b64encode(buf.getbuffer()).decode("ascii")
#     #data = buf.read() #getbuffer()
#     return f"<img src='data:image/png;base64,{data}'/>"
#     #return f"<img src='data:image/svg+xml;utf8,{data}'/>"

    
#    fig.savefig('./plots/%s.svg' % base)
#    return '<IMG SRC=./img/%s.svg>' % base


#### COMMENTAIRES JEROME
##
## <head>
##  <!-- load CollgateIFrameAPI -->
## <script src="http://collgate.ina.fr/collplay.dlweb/ina/js/video.iframe.api.js" type="text/javascript"></script>
## <script>
    
# window.addEventListener("load", function() {
    
#    let items = document.querySelectorAll("div.video-collgate");
   
#    items.foreach(item => {
#        let src = item.attr("data-src");
#        let item_id = item.id(); // attr("id");
#         CollgateIFrameAPI.insertPlayer("#"+item_id, {
#             src : src
#         });
#    });

# });


## </script>
## </head>
##
## dispvid doit inserer : 
## <div id="player-%s" class="video-collgate" data-src="http://collgate.ina.fr/collgate.dlweb/info/tv/fr2/2023-03-30T19:58:00Z/2700">
## </div>
##

# def dispvid(fname):

#     base = os.path.splitext(fname)[0]
        
#     url = "http://collgate.ina.fr/collgate.dlweb/get/%s/%s/%s/%s" % tuple(base.split('-'))
#     return """<video controls width="250">
#         <source src="%s" type="video/mp4">
#         </video>
#         """ % url

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
