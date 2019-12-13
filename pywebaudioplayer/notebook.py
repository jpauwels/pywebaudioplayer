# coding: utf-8
from .core import Image, _id, _js, _figure_margins, _write_samples, waveform_playlist


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
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">
    <!--<script>$.fn.modal || document.write('<link href="static/css/bootstrap.min.css" rel="stylesheet" />')</script>-->'''

    html_code += '''
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

    html_code += '''
    <script type="text/javascript">
    requirejs.config({{paths: {{wavesurfer: "https://cdnjs.cloudflare.com/ajax/libs/wavesurfer.js/1.4.0/wavesurfer.min"}}}});
    <!--require.config({{paths: {{wavesurfer: "static/wavesurfer.js/wavesurfer.min"}}}});-->
    requirejs(["wavesurfer"], function(WaveSurfer) {{
        wavesurfer{id} = WaveSurfer.create({{
            container: '#waveform{id}',
            cursorColor: "{cursor}",
            progressColor: "{progress}",
            waveColor: "{wave}",
            splitChannels: {split},
            height: {height},
            normalize: {norm}{bar_width}
        }});
        wavesurfer{id}.load("{path}");
    }});
    </script>'''.format(
        id=unique_id, path=audio_path, cursor=display['cursor_colour'], progress=display['played_wave_colour'], wave=display['unplayed_wave_colour'], split=_js(not behaviour['mono']), height=display['height'], norm=_js(behaviour['normalize']),
        bar_width=', barWidth: {}'.format(display['bar_width']) if display['bar_width'] else '')
    return html_code


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
    <link href="https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css" rel="stylesheet" integrity="sha384-wvfXpqpZZVQGK6TAh5PVlGOfQNHSoD2xbE+QkPxCAFlNEevoEH3Sl0sibVcOQVnN" crossorigin="anonymous" />
    <link rel="stylesheet" href="https://audiolabs.github.io/trackswitch.js/css/trackswitch.min.css" />

    <div class="player{}"{}>'''.format(unique_id, ' style="width:{}px"'.format(image_width) if seekable_image else '')
    if text:
        html_code += '''
        <p>
            {}
        </p>'''.format(text)
    if seekable_image:
        html_code += '''
        <img src="{}#{}" data-style="width: {}px;" class="seekable"{}/>'''.format(seekable_image_path, unique_id, image_width, ' data-seek-margin-left="{}" data-seek-margin-right="{}"'.format(*seek_margin) if seek_margin else '')
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
    </div>

    <script src="https://audiolabs.github.io/trackswitch.js/js/trackswitch.min.js"></script>
    <script type="text/javascript">
        jQuery(document).ready(function() {{
            jQuery(".player{}").trackSwitch({{mute: {}, solo: {}, globalsolo: {}, repeat: {}, radiosolo: {}, onlyradiosolo: {}, spacebar: {}, tabview: {}}});
        }});
    </script>
    '''.format(unique_id, _js(mute), _js(solo), _js(globalsolo), _js(repeat), _js(radiosolo), _js(onlyradiosolo), _js(spacebar), _js(tabview))

    return html_code
