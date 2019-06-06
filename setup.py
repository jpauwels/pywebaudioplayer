import setuptools
from os import path
from io import open

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
    name="pywebaudioplayer",
    version="0.0.3",
    author="Johan Pauwels",
    author_email="johan.pauwels@gmail.com",
    description="Create HTML+JS code snippets for the waversurfer.js, waveform-playlist and trackswitch.js audio players from Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jpauwels/pywebaudioplayer",
    packages=setuptools.find_packages(),
    install_requires=['Pillow'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Multimedia :: Sound/Audio :: Players",
    ],
    package_data={
        'pywebaudioplayer': ['wavesurfer.js/src/wavesurfer.js', 'waveform-playlist/dist/waveform-playlist/css/main.css', 'waveform-playlist/dist/waveform-playlist/js/waveform-playlist.var.js', 'trackswitch.js/js/trackswitch.js', 'trackswitch.js/css/trackswitch.css'],
    },
    project_urls={
        'Bug Reports': 'https://github.com/jpauwels/pywebaudioplayer/issues',
        'Source': 'https://github.com/jpauwels/pywebaudioplayer/',
    },
)
