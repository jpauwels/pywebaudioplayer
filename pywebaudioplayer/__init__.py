# coding: utf-8
import time
import os.path
from io import BytesIO
from PIL import Image
import pkg_resources
import shutil
import errno

path = 'web'

def _js(python_value):
    if isinstance(python_value, bool):
        return str(python_value).lower()
    elif not python_value:
        return 'none'
    else:
        return python_value


def _write_samples(file):
    if 'samples' in file:
        samples, samplerate = file['samples']
        if 'path' in file:
            if os.path.splitext(file['path'])[1] != '.wav':
                file['path'] += '.wav'
            with open(file['path'], 'wb') as wav_file:
                _convert_to_wave(samples, samplerate, wav_file)
            return file['path']
        else:
            file_buffer = BytesIO()
            _convert_to_wave(samples, samplerate, file_buffer)
            return file_buffer.getvalue()


def _convert_to_wave(data, rate, file):
    import struct
    import wave

    try:
        import numpy as np

        data = np.array(data, dtype=float)
        if len(data.shape) == 1:
            nchan = 1
        elif len(data.shape) == 2:
            # In wave files,channels are interleaved. E.g.,
            # "L1R1L2R2..." for stereo. See
            # http://msdn.microsoft.com/en-us/library/windows/hardware/dn653308(v=vs.85).aspx
            # for channel ordering
            nchan = data.shape[0]
            data = data.T.ravel()
        else:
            raise ValueError('Array audio input must be a 1D or 2D array')
        scaled = np.int16(data/np.max(np.abs(data))*32767).tolist()
    except ImportError:
        # check that it is a "1D" list
        idata = iter(data)  # fails if not an iterable
        try:
            iter(idata.next())
            raise TypeError('Only lists of mono audio are supported if numpy is not installed')
        except TypeError:
            # this means it's not a nested list, which is what we want
            pass
        maxabsvalue = float(max([abs(x) for x in data]))
        scaled = [int(x/maxabsvalue*32767) for x in data]
        nchan = 1

    waveobj = wave.open(file, mode='wb')
    waveobj.setnchannels(nchan)
    waveobj.setframerate(rate)
    waveobj.setsampwidth(2)
    waveobj.setcomptype('NONE', 'NONE')
    waveobj.writeframes(b''.join([struct.pack('<h', x) for x in scaled]))
    waveobj.close()


def _id():
    return int(1e7*time.time())


def wavesurfer(audio_path=None, controls={}, display={}, behaviour={}, samples=None):
    # Set defaults
    if 'text_controls' not in controls:
        controls['text_controls'] = True
    if 'backward_button' not in controls:
        controls['backward_button'] = True
    if 'forward_button' not in controls:
        controls['forward_button'] = True
    if 'mute_button' not in controls:
        controls['mute_button'] = True
    if 'height' not in display:
        display['height'] = 128
    if 'cursor_colour' not in display:
        display['cursor_colour'] = '#333'
    if 'played_wave_colour' not in display:
        display['played_wave_colour'] = '#555'
    if 'unplayed_wave_colour' not in display:
        display['unplayed_wave_colour'] = '#999'
    if 'bar_width' not in display:
        display['bar_width'] = None
    if 'normalize' not in behaviour:
        behaviour['normalize'] = False
    if 'mono' not in behaviour:
        behaviour['mono'] = True

    unique_id = _id()
    if not audio_path and not samples:
        raise ValueError('Provide either a path to an audio file or samples')

    html_code = '''
    <div id="waveform{}"></div>
    <p align="center">
    '''.format(unique_id)

    if controls['backward_button']:
        html_code += '''
          <button class="btn btn-primary" onclick="wavesurfer{}.skipBackward()">
            <i class="glyphicon glyphicon-backward"></i>
            {}
          </button>'''.format(unique_id, 'Backward' if controls['text_controls'] else '')

    html_code += '''
      <button class="btn btn-success" onclick="wavesurfer{}.playPause()">
        <i class="glyphicon glyphicon-play"></i>
        {} /
        <i class="glyphicon glyphicon-pause"></i>
        {}
      </button>'''.format(unique_id, 'Play' if controls['text_controls'] else '', 'Pause' if controls['text_controls'] else '')

    if controls['forward_button']:
        html_code += '''
          <button class="btn btn-primary" onclick="wavesurfer{}.skipForward()">
            <i class="glyphicon glyphicon-forward"></i>
            {}
          </button>'''.format(unique_id, 'Forward' if controls['text_controls'] else '')

    if controls['mute_button']:
        html_code += '''
          <button class="btn btn-danger" onclick="wavesurfer{}.toggleMute()">
            <i class="glyphicon glyphicon-volume-off"></i>
            {}
          </button>'''.format(unique_id, 'Toggle Mute' if controls['text_controls'] else '')

    html_code += '\n    </p>'

    link_tags, script_tags = _manage_wavesurfer_files()

    script_tags += '''
    <script type="text/javascript">
    var wavesurfer{id} = WaveSurfer.create({{
      container: '#waveform{id}',
      cursorColor: "{cursor}",
      progressColor: "{progress}",
      waveColor: "{wave}",
      splitChannels: {split},
      height: {height},
      normalize: {norm}{bar_width}
    }});
    wavesurfer{id}.load("{path}");
    </script>'''.format(
        id=unique_id, path=audio_path, cursor=display['cursor_colour'], progress=display['played_wave_colour'], wave=display['unplayed_wave_colour'], split=_js(not behaviour['mono']), height=display['height'], norm=_js(behaviour['normalize']),
        bar_width=', barWidth: {}'.format(display['bar_width']) if display['bar_width'] else '')
    return '\n'.join([link_tags, html_code, script_tags])


def _manage_wavesurfer_files():
    global path
    if not path:
        link_tags = '    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">\n'
        script_tags = '    <script src="{}"></script>\n'.format(pkg_resources.resource_filename(__name__, "wavesurfer.js/src/wavesurfer.js"))
    elif path == 'web':
        link_tags = '    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">\n'
        script_tags = '    <script src="https://cdnjs.cloudflare.com/ajax/libs/wavesurfer.js/1.4.0/wavesurfer.min.js"></script>\n'
    else:
        _force_copy(pkg_resources.resource_filename(__name__, "wavesurfer.js/src"), os.path.join(path, "wavesurfer"))
        # Write relative path
        link_tags = '    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">\n'
        script_tags = '    <script src="{}" type="module"></script>\n'.format(os.path.join(os.path.relpath(path), "wavesurfer/wavesurfer.js"))
    return link_tags, script_tags

def _force_copy(src, dest):
    if os.path.isdir(src):
        try:
            os.makedirs(dest)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        for f in os.listdir(src):
            _force_copy(os.path.join(src, f), os.path.join(dest, f))
    else:
        shutil.copyfile(src, dest)

def waveform_playlist(tracks, controls={}, display={}, behaviour={}):
    # Set defaults
    if 'text_controls' not in controls:
        controls['text_controls'] = False
    if 'backward_button' not in controls:
        controls['backward_button'] = True
    if 'forward_button' not in controls:
        controls['forward_button'] = True
    if 'pause_button' not in controls:
        controls['pause_button'] = True
    if 'stop_button' not in controls:
        controls['stop_button'] = True
    if 'height' not in display:
        display['height'] = 100
    if 'background_colour' not in display:
        display['background_colour'] = 'white'
    if 'cursor_colour' not in display:
        display['cursor_colour'] = '#333'
    if 'played_wave_colour' not in display:
        display['played_wave_colour'] = 'orange'
    if 'unplayed_wave_colour' not in display:
        display['unplayed_wave_colour'] = 'grey'
    if 'normalize' not in behaviour:
        display['normalize'] = False
    if 'mono' not in behaviour:
        display['mono'] = False

    unique_id = _id()
    html_code = '''
    <div id="top-bar" class="playlist-top-bar">
      <div class="playlist-toolbar">
        <div class="btn-group">
    '''

    if controls['backward_button']:
        html_code += '''
        <span class="btn-rewind btn btn-primary"><i class="glyphicon glyphicon-fast-backward"></i>{}</span>'''.format(
        ' Backward' if controls['text_controls'] else '')
    if controls['pause_button']:
        html_code += '''
        <span class="btn-pause btn btn-warning"><i class="glyphicon glyphicon-pause"></i>{}</span>'''.format(
        ' Pause' if controls['text_controls'] else '')
    html_code += '''
    <span class="btn-play btn btn-success"><i class="glyphicon glyphicon-play"></i>{}</span>'''.format(
    ' Play' if controls['text_controls'] else '')
    if controls['stop_button']:
        html_code += '''
        <span class="btn-stop btn btn-danger"><i class="glyphicon glyphicon-stop"></i>{}</span>'''.format(
        ' Stop' if controls['text_controls'] else '')
    if controls['forward_button']:
        html_code += '''
        <span class="btn-fast-forward btn btn-primary"><i class="glyphicon glyphicon-fast-forward"></i>{}</span>'''.format(
        ' Forward' if controls['text_controls'] else '')

    html_code += '''
        </div>
        <span class="audio-pos">00:00:00.0</span>
      </div>
    </div>
    <div id="playlist{}"></div>
    <form class="form-inline">
      <div class="form-group">
        <label for="master-gain">Master Volume</label>
        <input type="range" min="0" max="100" value="100" class="master-gain form-control" id="master-gain">
      </div>
      <div class="checkbox">
        <label>
          <input type="checkbox" class="automatic-scroll"> Automatic Scroll
        </label>
      </div>
    </form>
    <!--<div class="sound-status"></div>
    <div class="loading-data"></div>-->'''.format(
    unique_id
    )

    link_tags, script_tags, post_script_tags = _manage_waveform_playlist_files()

    script_tags += '''
    <script type="text/javascript">
    var playlist = WaveformPlaylist.init({{
      samplesPerPixel: 1000,
      waveHeight: 100,
      container: document.getElementById("playlist{}"),
      timescale: true,
      state: 'cursor',
      colors: {{
        waveOutlineColor: "{}",
        timeColor: "{}",
        fadeColor: "{}"
      }},
      controls: {{
        show: true, //whether or not to include the track controls
        width: 200 //width of controls in pixels
      }},
      zoomLevels: [500, 1000, 3000, 5000]
    }});'''.format(unique_id, display['background_colour'], display['unplayed_wave_colour'], display['played_wave_colour'])

    script_tags += 'playlist.load([\n'
    for track in tracks:
        if 'samples' in track:
            if 'path' in track:
                _write_samples(track)
            else:
                raise ValueError('A path to write the audio to needs to be given when raw samples are passed')

        script_tags += '''
        {{
            "src": "{}",
            "name": "{}",
            "gain": {},
            "muted": {},
            "soloed": {}
        }},'''.format(track['path'], track['title'],
                      track['gain'] if 'gain' in track else 1,
                      _js(track['mute']) if 'mute' in track else 'false',
                      _js(track['solo']) if 'solo' in track else 'false',)
    script_tags += '''
    ]).then(function() {
    });
    </script>
    '''
    script_tags += post_script_tags
    return '\n'.join([link_tags, html_code, script_tags])


def _manage_waveform_playlist_files():
    global path
    if not path:
        link_tags = '    <link rel="stylesheet" href="//maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">\n'
        link_tags += '    <link rel="stylesheet" href="{}">\n'.format(pkg_resources.resource_filename(__name__, "waveform-playlist/dist/waveform-playlist/css/main.css"))
        script_tags = '    <script src="//code.jquery.com/jquery-3.2.1.min.js" integrity="sha256-hwg4gsxgFZhOsEEamdOYGBf13FyQuiTwlAQgxVSNgt4=" crossorigin="anonymous"></script>\n'
        script_tags += '    <script type="text/javascript" src="{}"></script>\n'.format(pkg_resources.resource_filename(__name__, "waveform-playlist/dist/waveform-playlist/js/waveform-playlist.var.js"))
        post_script_tags = '    <script type="text/javascript" src="{}"></script>\n'.format(pkg_resources.resource_filename(__name__, "waveform-playlist/dist/waveform-playlist/js/emitter.js"))
    elif path == 'web':
        link_tags = '    <link rel="stylesheet" href="//maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">\n'
        link_tags += '    <link rel="stylesheet" href="https://naomiaro.github.io/waveform-playlist/css/main.css">\n'
        script_tags = '    <script src="//code.jquery.com/jquery-3.2.1.min.js" integrity="sha256-hwg4gsxgFZhOsEEamdOYGBf13FyQuiTwlAQgxVSNgt4=" crossorigin="anonymous"></script>\n'
        script_tags += '    <script type="text/javascript" src="https://naomiaro.github.io/waveform-playlist/js/waveform-playlist.var.js"></script>\n'
        post_script_tags = '    <script type="text/javascript" src="https://naomiaro.github.io/waveform-playlist/js/emitter.js"></script>\n'
    else:
        shutil.copy(pkg_resources.resource_filename(__name__, "waveform-playlist/dist/waveform-playlist/css/main.css"), path)
        shutil.copy(pkg_resources.resource_filename(__name__, "waveform-playlist/dist/waveform-playlist/js/waveform-playlist.var.js"), path)
        shutil.copy(pkg_resources.resource_filename(__name__, "waveform-playlist/dist/waveform-playlist/js/waveform-playlist.var.js.map"), path)
        shutil.copy(pkg_resources.resource_filename(__name__, "waveform-playlist/dist/waveform-playlist/js/emitter.js"), path)
        link_tags = '    <link rel="stylesheet" href="//maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">\n'
        link_tags += '    <link rel="stylesheet" href="{}">\n'.format(os.path.join(os.path.relpath(path), "main.css"))
        script_tags = '    <script src="//code.jquery.com/jquery-3.2.1.min.js" integrity="sha256-hwg4gsxgFZhOsEEamdOYGBf13FyQuiTwlAQgxVSNgt4=" crossorigin="anonymous"></script>\n'
        script_tags += '    <script type="text/javascript" src="{}"></script>\n'.format(os.path.join(os.path.relpath(path), "waveform-playlist.var.js"))
        post_script_tags = '    <script type="text/javascript" src="{}"></script>\n'.format(os.path.join(os.path.relpath(path), "emitter.js"))
    return link_tags, script_tags, post_script_tags


def _figure_margins(ax):
    xpos_min = ax.get_position().xmin
    xpos_max = ax.get_position().xmax
    if ax.get_lines():
        xpos_range = xpos_max - xpos_min
        xval_min = ax.get_xlim()[0]
        xval_max = ax.get_xlim()[1]
        xval_range = xval_max - xval_min
        xdata_min = ax.get_lines()[0].get_xdata()[0]
        xdata_max = ax.get_lines()[0].get_xdata()[-1]
        left_space = xdata_min - xval_min
        right_space = xval_max - xdata_max
        left_margin = xpos_min+left_space/xval_range*xpos_range
        right_margin = 1-xpos_max+right_space/xval_range*xpos_range
        return 100*left_margin, 100*right_margin
    elif ax.get_images():
        return 100*xpos_min, 100-100*xpos_max


def trackswitch(tracks, text='', seekable_image=None, seek_margin=None, mute=True, solo=True, globalsolo=True, repeat=False, radiosolo=False, onlyradiosolo=False, spacebar=False, tabview=False):
    unique_id = _id()
    if isinstance(seekable_image, str):
        seekable_image_path = seekable_image
        with Image.open(seekable_image) as image_file:
            image_width = image_file.size[0]
    elif seekable_image:
        fig, seekable_image_path = seekable_image
        image_width = fig.get_size_inches()[0] * fig.get_dpi()
        seek_margin = _figure_margins(fig.gca())
        fig.savefig(seekable_image_path, dpi='figure')
    html_code = '''
    <div class="player{}"{}>'''.format(unique_id, ' style="width:{}px"'.format(image_width) if seekable_image else '')
    if text:
        html_code += '''
        <p>
            {}
        </p>'''.format(text)
    if seekable_image:
        html_code += '''
        <img src="{}" data-style="width: {}px;" class="seekable"{}/>'''.format(seekable_image_path, image_width, ' data-seek-margin-left="{}" data-seek-margin-right="{}"'.format(*seek_margin) if seek_margin else '')
    for track in tracks:
        html_code += '''
        <ts-track{}{}>
          <ts-source src='''.format(' title="{}"'.format(track['title']) if 'title' in track else '',
                                     ' data-img="{}"'.format(track['image']) if 'image' in track else '')
        if 'samples' in track:
            path_or_bytestring = _write_samples(track)
            html_code += '"{}" type="audio/wav"'.format(path_or_bytestring)
        elif 'path' in track:
            html_code += '"{}"{}'.format(track['path'], ' type="{}"'.format(track['mimetype']) if 'mimetype' in track else '')
        else:
            raise ValueError('Provide either a path to an audio file or raw samples')
        html_code += '''></ts-source>
        </ts-track>'''

    html_code += '''
    </div>'''

    link_tags, script_tags = _manage_trackswitch_files()

    script_tags += '''
    <script type="text/javascript">
        jQuery(document).ready(function() {{
            jQuery(".player{}").trackSwitch({{mute: {}, solo: {}, globalsolo: {}, repeat: {}, radiosolo: {}, onlyradiosolo: {}, spacebar: {}, tabview: {}}});
        }});
    </script>
    '''.format(unique_id, _js(mute), _js(solo), _js(globalsolo), _js(repeat), _js(radiosolo), _js(onlyradiosolo), _js(spacebar), _js(tabview))

    return '\n'.join([link_tags, html_code, script_tags])


def _manage_trackswitch_files():
    global path
    if not path:
        link_tags = '    <link href="https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css" rel="stylesheet" integrity="sha384-wvfXpqpZZVQGK6TAh5PVlGOfQNHSoD2xbE+QkPxCAFlNEevoEH3Sl0sibVcOQVnN" crossorigin="anonymous" />\n'
        link_tags += '    <link rel="stylesheet" href="{}" />\n'.format(pkg_resources.resource_filename(__name__, "trackswitch.js/css/trackswitch.css"))
        script_tags = '    <script src="https://code.jquery.com/jquery-3.2.1.min.js" integrity="sha256-hwg4gsxgFZhOsEEamdOYGBf13FyQuiTwlAQgxVSNgt4=" crossorigin="anonymous"></script>\n'
        script_tags += '       <script src="{}"></script>'''.format(pkg_resources.resource_filename(__name__, "trackswitch.js/js/trackswitch.js"))
    elif path == 'web':
        link_tags = '''
        <link href="https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css" rel="stylesheet" integrity="sha384-wvfXpqpZZVQGK6TAh5PVlGOfQNHSoD2xbE+QkPxCAFlNEevoEH3Sl0sibVcOQVnN" crossorigin="anonymous" />
        <link rel="stylesheet" href="https://audiolabs.github.io/trackswitch.js/css/trackswitch.min.css" />'''
        script_tags = '''
        <script src="https://code.jquery.com/jquery-3.2.1.min.js" integrity="sha256-hwg4gsxgFZhOsEEamdOYGBf13FyQuiTwlAQgxVSNgt4=" crossorigin="anonymous"></script>
        <script src="https://audiolabs.github.io/trackswitch.js/js/trackswitch.min.js"></script>'''
    else:
        shutil.copy(pkg_resources.resource_filename(__name__, "trackswitch.js/css/trackswitch.css"), path)
        shutil.copy(pkg_resources.resource_filename(__name__, "trackswitch.js/js/trackswitch.js"), path)
        link_tags = '    <link href="https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css" rel="stylesheet" integrity="sha384-wvfXpqpZZVQGK6TAh5PVlGOfQNHSoD2xbE+QkPxCAFlNEevoEH3Sl0sibVcOQVnN" crossorigin="anonymous" />\n'
        link_tags += '    <link rel="stylesheet" href="{}" />\n'.format(os.path.join(os.path.relpath(path), "trackswitch.css"))
        script_tags = '    <script src="https://code.jquery.com/jquery-3.2.1.min.js" integrity="sha256-hwg4gsxgFZhOsEEamdOYGBf13FyQuiTwlAQgxVSNgt4=" crossorigin="anonymous"></script>\n'
        script_tags += '       <script src="{}"></script>'''.format(os.path.join(os.path.relpath(path), "trackswitch.js"))
    return link_tags, script_tags
