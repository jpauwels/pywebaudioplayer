#!/usr/bin/env python2.7
from flask import Flask, render_template
import pywebaudioplayer as pwa
import numpy as np
import matplotlib.pyplot as plt

app = Flask(__name__, static_folder='media')

@app.route('/')
def index():
    w1 = pwa.wavesurfer('media/drums.mp3',
                        controls={'text_controls': False, 'backward_button': False, 'forward_button': False, 'mute_button': False},
                        display={'unplayed_wave_colour': 'darkorange', 'played_wave_colour': 'purple', 'height': 128},
                        behaviour={'mono': False})
    w2 = pwa.wavesurfer('media/bass.mp3',
                        controls={'text_controls': True, 'backward_button': True, 'forward_button': True, 'mute_button': True},
                        display={'unplayed_wave_colour': '#999', 'played_wave_colour': 'hsla(200, 100%, 30%, 0.5)', 'cursor_colour': '#fff', 'bar_width': 3, 'height': 256})
    w3 = pwa.wavesurfer('media/bass.mp3')
    p = pwa.waveform_playlist([{'title': 'Drums', 'path': 'media/drums.mp3'},
             {'title': 'Synth', 'path': 'media/synth.mp3'},
             {'title': 'Bass', 'path': 'media/bass.mp3'},
             {'title': 'Violin', 'path': 'media/violins.mp3'},
             ], {'text_controls': True}, {'background_colour': '#E0EFF1', 'played_wave_colour': 'red', 'unplayed_wave_colour': 'yellow'})
    ts1 = pwa.trackswitch([
        {'title': 'Drums', 'image': 'media/drums.png', 'path': 'media/drums.mp3', 'mimetype': 'audio/mpeg'},
        {'title': 'Synth', 'image': 'media/synth.png', 'path': 'media/synth.mp3', 'mimetype': 'audio/mpeg'},
        {'title': 'Bass', 'image': 'media/bass.png', 'path': 'media/bass.mp3', 'mimetype': 'audio/mpeg'},
        {'title': 'Violin', 'image': 'media/violins.png', 'path': 'media/violins.mp3', 'mimetype': 'audio/mpeg'}],
        text='Example trackswitch.js instance.', seekable_image='media/mix.png', seek_margin=(4,4))

    samplerate = 8000
    freq = 440
    duration = 3
    t = np.arange(duration*samplerate)
    f0 = np.sin(2*np.pi*freq*t/samplerate)
    f1 = np.sin(2*np.pi*2*freq*t/samplerate)
    f2 = np.sin(2*np.pi*3*freq*t/samplerate)
    f3 = np.sin(2*np.pi*4*freq*t/samplerate)
    f4 = np.sin(2*np.pi*5*freq*t/samplerate)
    f5 = np.sin(2*np.pi*6*freq*t/samplerate)
    f6 = np.sin(2*np.pi*7*freq*t/samplerate)
    complex_sine = f0+f1+f2+f3+f4+f5+f6

    fig, ax = plt.subplots(ncols=1, figsize=(10,4), dpi=72)
    ax.specgram(complex_sine, Fs=samplerate, detrend='none');
    # fig, ax = plt.subplots(ncols=1, figsize=(16,4), dpi=72)
    # ax.plot(t, sine)
    # ax.grid(False)
    # fig.set_tight_layout(True)
    # ax.set_xlim([t[0], t[-1]])
    ts2 = pwa.trackswitch([{'title': 'Fundamental', 'samples': (f0, samplerate), 'path': 'media/fundamental.wav'},
             {'title': 'First overtone', 'samples': (f1, samplerate), 'path': 'media/first.wav'},
             {'title': 'Second overtone', 'samples': (f2, samplerate), 'path': 'media/second.wav'},
             {'title': 'Third overtone', 'samples': (f3, samplerate), 'path': 'media/third.wav'},
             {'title': 'Fourth overtone', 'samples': (f4, samplerate), 'path': 'media/fourth.wav'},
             {'title': 'Fifth overtone', 'samples': (f5, samplerate), 'path': 'media/fifth.wav'},
             {'title': 'Sixth overtone', 'samples': (f6, samplerate), 'path': 'media/sixth.wav'}],
            seekable_image=(fig, 'media/spectrogram.png'), repeat=True)
    return render_template('page.html', title='pywebaudioplayer', body=[w1, w2, w3, p, ts1, ts2])

@app.route('/ws')
def ws():
    basedir = 'media/trackswitch.js/examples/data'
    # var ctx = document.createElement('canvas').getContext('2d');
    # var linGrad = ctx.createLinearGradient(0, 64, 0, 200);
    # linGrad.addcolourStop(0.5, 'rgba(255, 255, 255, 1.000)');
    # linGrad.addcolourStop(0.5, 'rgba(183, 183, 183, 1.000)');
    #  wavecolour: linGrad,

    # '''
    return render_template('page.html', title='Wavesurfer', body=[w1, w2])

# @app.route('/media/trackswitch.js/<path:path>')
# def static_file(path):
#     print('serving path {}'.format(path))
#     return app.send_static_file(path)
#
# @app.route('/test')
# def test():
#     return send_from_directory('media', 'trackswitch.html')

if __name__ == '__main__':
  app.run(debug=True)
