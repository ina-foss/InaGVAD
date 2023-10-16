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


from os.path import basename, splitext

dchan = {'FBL': ('France Bleu', 'music_radio'),
         'FCR': ('France Culture', 'generalist_radio'),
         'FIF': ('France Info', 'generalist_radio'),
         'FIP': ('FIP', 'music_radio'),
         'FIT': ('France Inter', 'generalist_radio'),
         'FMU': ('France Musique', 'music_radio'),
         'FUN': ('Fun Radio', 'music_radio'),
         'MUV': ("Mouv'", 'music_radio'),
         'RMC': ('RMC', 'generalist_radio'),
         'RTL': ('RTL', 'generalist_radio'),
         'SKY': ('Skyrock', 'music_radio'),
         'ART': ('Arte', 'generalist_tv'),
         'BFT': ('BFM TV', 'news_tv'),
         'C+_': ('Canal+', 'generalist_tv'),
         'C+N': ('CNEWS', 'news_tv'),
         'C25': ('Chérie 25', 'generalist_tv'),  # thematic
         'F24': ('France 24', 'news_tv'),
         'FR2': ('France 2', 'generalist_tv'),
         'FR3': ('France 3', 'generalist_tv'),
         # officially : generalist, in practice : kids/music
         'FR4': ('France 4', 'generalist_tv'),
         'FR5': ('France 5', 'generalist_tv'),
         'GUL': ('Gulli', 'generalist_tv'),  # kids thematic
         'LCI': ('LCI', 'news_tv'),
         'M6_': ('M6', 'generalist_tv'),
         'N12': ('NRJ 12', 'generalist_tv'),
         'PP_': ('Paris Première', 'generalist_tv'),
         'T5M': ('TV5 Monde', 'generalist_tv'),
         'TF1': ('TF1', 'generalist_tv'),
         'TFX': ('TFX', 'generalist_tv')}


def fileid2metadata(fileid):
    bn = basename(splitext(fileid)[0])
    media, chancode, tc = bn.split('-')
    channame, chancat = dchan[chancode]
    return {'fileid': bn,
            'media': media,
            'channel_code': chancode,
            'channel_name': channame,
            'channel_category': chancat,
            'broadcast_hour': int(tc[:2])}
    # tv-TF1-190336.wav
