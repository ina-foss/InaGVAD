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


#import os
from setuptools import setup, find_packages

KEYWORDS = '''
speech-segmentation
audio-analysis
speech-detection
gender-classification
speaker-gender
speech
voice-activity-detection
speech-activity-detection'''.strip().split('\n')

CLASSIFIERS=[
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Intended Audience :: Education',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3 :: Only',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Topic :: Multimedia :: Sound/Audio',
    'Topic :: Multimedia :: Sound/Audio :: Analysis',
    'Topic :: Multimedia :: Sound/Audio :: Speech',
    'Topic :: Scientific/Engineering',
    'Topic :: Scientific/Engineering :: Artificial Intelligence',
    'Topic :: Software Development',
    'Topic :: Software Development :: Libraries',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Sociology',
]

DESCRIPTION='InaGVAD : a French TV and radio corpus for Speech Activity Detection and Gender Segmentation'
LONGDESCRIPTION='''InaGVAD : a French TV and radio corpus for Speech Activity Detection and Gender Segmentation.
This project contains the code necessary to generate corpus annotations from transcriber files.
It also contains code allowing to evaluate a VAD or gender segmentation system on the corpus in paper's conditions'
'''

setup(
    name = "inaGVAD",
    version = 0.1,
#    cmdclass = versioneer.get_cmdclass(),
    author = "David Doukhan",
    author_email = "david.doukhan@gmail.com",
#    test_suite="run_test.py",
    description = DESCRIPTION,
    license = "MIT",
    install_requires=['numpy', 'pandas', 'pyannote.core', 'pyannote.metrics'], # 'matplotlib', ],
#    url = "https://github.com/ina-foss/inaSpeechSegmenter",
    keywords = KEYWORDS,
    packages = find_packages(),
#    include_package_data = True,
#    data_files = ['LICENSE'],
    long_description=LONGDESCRIPTION,
    long_description_content_type='text/markdown',
#    scripts=[os.path.join('scripts', script) for script in \
#             ['ina_speech_segmenter.py', 'ina_speech_segmenter_pyro_client.py', 'ina_speech_segmenter_pyro_server.py', 'ina_speech_segmenter_pyro_client_setjobs.py']],
    classifiers=CLASSIFIERS,
    python_requires='>=3.7',
)
