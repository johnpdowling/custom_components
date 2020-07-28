"""
Support for interfacing to forked-daapd API.

"""
import logging

import requests
import voluptuous as vol
import os

from homeassistant.components.media_player import (
    MediaPlayerDevice, PLATFORM_SCHEMA)
from homeassistant.components.media_player.const import (
    MEDIA_TYPE_MUSIC, MEDIA_TYPE_PLAYLIST, SUPPORT_NEXT_TRACK,
    SUPPORT_PAUSE, SUPPORT_PLAY, SUPPORT_PLAY_MEDIA, SUPPORT_PREVIOUS_TRACK,
    SUPPORT_SEEK, SUPPORT_TURN_OFF, SUPPORT_TURN_ON, SUPPORT_VOLUME_MUTE,
    SUPPORT_VOLUME_SET)
from homeassistant.const import (
    CONF_HOST, CONF_NAME, CONF_PORT, CONF_SSL, STATE_IDLE, STATE_OFF, STATE_ON,
    STATE_PAUSED, STATE_PLAYING)
import homeassistant.helpers.config_validation as cv

#import mpg123
#from mpg123 import Mpg123

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = 'forked-daapd'
DEFAULT_PORT = 3689
DEFAULT_SSL = False
DEFAULT_TIMEOUT = 10
DOMAIN = 'forked-daapd'

#SUPPORT_FORKEDDAAPD = SUPPORT_PAUSE | SUPPORT_VOLUME_SET | SUPPORT_VOLUME_MUTE | \
#    SUPPORT_PREVIOUS_TRACK | SUPPORT_NEXT_TRACK | SUPPORT_SEEK | \
#    SUPPORT_PLAY_MEDIA | SUPPORT_PLAY | SUPPORT_TURN_OFF
SUPPORT_FORKEDDAAPD = SUPPORT_VOLUME_SET | SUPPORT_VOLUME_MUTE | \
                      SUPPORT_PLAY_MEDIA | SUPPORT_TURN_OFF | SUPPORT_TURN_ON

SUPPORT_AIRPLAY = SUPPORT_VOLUME_SET | SUPPORT_VOLUME_MUTE | SUPPORT_TURN_ON | SUPPORT_TURN_OFF

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
    vol.Optional(CONF_SSL, default=DEFAULT_SSL): cv.boolean,
})


class ForkedDaapd:
    """The forked-daapd API client."""

    def __init__(self, host, port, use_ssl):
        """Initialize the forked-daapd device."""
        self.host = host
        self.port = port
        self.use_ssl = use_ssl
        os.system("apk add --no-cache mpg123")

    @property
    def _base_url(self):
        """Return the base URL for endpoints."""
        if self.use_ssl:
            uri_scheme = 'https://'
        else:
            uri_scheme = 'http://'

        if self.port:
            return '{}{}:{}'.format(uri_scheme, self.host, self.port)

        return '{}{}'.format(uri_scheme, self.host)

    def _request(self, method, path, params=None):
        """Make the actual request and return the parsed response."""
        url = '{}{}'.format(self._base_url, path)

        try:
            if method == 'GET':
                response = requests.get(url, timeout=DEFAULT_TIMEOUT)
            elif method == 'PUT_EMPTY':
                response = requests.put(url, timeout=DEFAULT_TIMEOUT)
            elif method == 'PUT':
                response = requests.put(url, json=dict(params) if params else None, timeout=DEFAULT_TIMEOUT)
            elif method == 'DELETE':
                response = requests.delete(url, timeout=DEFAULT_TIMEOUT)
            try:
                return response.json()
            except:
                return {}
        except requests.exceptions.HTTPError:
            return {'player_state': 'error'}
        except requests.exceptions.RequestException:
            return {'player_state': 'offline'}

    def _command(self, named_command):
        """Make a request for a controlling command."""
        return self._request('PUT', '/api/player/' + named_command)

    def player(self):
        """Return the current state."""
        return self._request('GET', '/api/player')

    def queue(self, item_id = None):
        if item_id is None:
            return self._request('GET', '/api/queue')
        else:
            return self._request('GET', "/api/queue?id=" + str(item_id))

    def set_volume(self, level):
        """Set the volume and returns the current state, level 0-100."""
        return self._request('PUT', '/api/player/volume?volume=' + str(int(level * 100)))

    def set_muted(self, muted):
        """Mute and returns the current state, muted True or False."""
        if muted is True:
            self.set_volume(0)
        else:
            self.set_volume(0.5)

    def play(self):
        """Set playback to play and returns the current state."""
        return self._command('play')

    def pause(self):
        """Set playback to paused and returns the current state."""
        return self._command('pause')

    def next(self):
        """Skip to the next track and returns the current state."""
        return self._command('next')

    def previous(self):
        """Skip back and returns the current state."""
        return self._command('prev')

    def stop(self):
        """Stop playback and return the current state."""
        return self._command('stop')

    def play_music(self, media_id, wholePath=True):
        path = media_id.split('/')
        filename = path[len(path) - 1]
        os.system("mpg123 --encoding s16 --rate 44100 --stereo --stdout /config/tts/" + filename + " > /config/forked-daapd/music/HomeAssistantAnnounce")
        return {}

    def play_playlist(self, playlist_id_or_name):
        """Set a playlist to be current and returns the current state."""
        response = self._request('GET', '/playlists')
        playlists = response.get('playlists', [])

        found_playlists = \
            [playlist for playlist in playlists if
             (playlist_id_or_name in [playlist["name"], playlist["id"]])]

        if found_playlists:
            playlist = found_playlists[0]
            path = '/playlists/' + playlist['id'] + '/play'
            return self._request('PUT', path)

    def artwork_url(self):
        """Return a URL of the current track's album art."""
        return self._base_url + '/artwork'

    def airplay_devices(self):
        """Return a list of AirPlay devices."""
        return self._request('GET', '/api/outputs')

    def airplay_device(self, device_id):
        """Return an AirPlay device."""
        return self._request('GET', '/api/outputs/' + device_id)

    def toggle_airplay_device(self, device_id, toggle):
        """Toggle airplay device on or off, id, toggle True or False."""
        _LOGGER.debug("Toggle id: %s, bool: %s", device_id, str(toggle))
        path = '/api/outputs/' + device_id
        return self._request('PUT', path, {'selected': toggle})

    def set_volume_airplay_device(self, device_id, level):
        """Set volume, returns current state of device, id,level 0-100."""
        path = '/api/outputs/' + device_id
        return self._request('PUT', path, {'volume': int(level *100)})


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the forked-daapd platform."""
    add_entities([
        ForkedDaapdDevice(
            config.get(CONF_NAME),
            config.get(CONF_HOST),
            config.get(CONF_PORT),
            config.get(CONF_SSL),

            add_entities
        )
    ])


class ForkedDaapdDevice(MediaPlayerDevice):
    """Representation of a forked-daapd API instance."""

    def __init__(self, name, host, port, use_ssl, add_entities):
        """Initialize the forked-daapd device."""
        self._name = name
        self._host = host
        self._port = port
        self._use_ssl = use_ssl
        self._add_entities = add_entities

        self.client = ForkedDaapd(self._host, self._port, self._use_ssl)

        self.current_volume = None
        self.muted = None
        self.current_title = None
        self.current_album = None
        self.current_artist = None
        self.current_playlist = None
        self.content_id = None

        self.player_state = None

        self.airplay_devices = {}

        self.update()

    def update_state(self, state_hash):
        """Update all the state properties with the passed in dictionary."""
        if not state_hash:
            state_hash = dict()

        self.player_state = state_hash.get('state', None)

        self.current_volume = float(state_hash.get('volume', 0) /100)
        self.muted = (self.current_volume == 0)
        self.current_playlist = None
        current_item_id = state_hash.get('item_id',0)
        if current_item_id > 0:
            queue_item = self.client.queue(current_item_id)
            if queue_item.get('count', 0) > 0:
                current_item = queue_item.get('items', [])[0]
                self.current_title = current_item.get('title', None)
                self.current_album = current_item.get('album', None)
                self.current_artist = current_item.get('artist', None)
                self.content_id = current_item.get('track_id', None)
                return
        self.current_title = None
        self.current_album = None
        self.current_artist = None
        self.content_id = None

    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    @property
    def state(self):
        """Return the state of the device."""
        if self.player_state == 'play':
            return STATE_PLAYING

        if self.player_state == 'stop':
            return STATE_IDLE

        if self.player_state == 'pause':
            return STATE_PAUSED

        return 'offline'

    def update(self):
        """Retrieve latest state."""
        now_playing = self.client.player()
        self.update_state(now_playing)

        found_devices = self.client.airplay_devices()
        found_devices = found_devices.get('outputs', [])

        new_devices = []

        for device_data in found_devices:
            if device_data.get('type') != "AirPlay":
                continue
            device_id = device_data.get('id')

            if self.airplay_devices.get(device_id):
                # update it
                airplay_device = self.airplay_devices.get(device_id)
                airplay_device.update_state(device_data)
            else:
                # add it
                airplay_device = AirPlayDevice(device_id, self.client)
                airplay_device.update_state(device_data)
                self.airplay_devices[device_id] = airplay_device
                new_devices.append(airplay_device)

        if new_devices:
            self._add_entities(new_devices)

    @property
    def is_volume_muted(self):
        """Boolean if volume is currently muted."""
        return self.muted

    @property
    def volume_level(self):
        """Volume level of the media player (0..1)."""
        return self.current_volume

    @property
    def media_content_id(self):
        """Content ID of current playing media."""
        return self.content_id

    @property
    def media_content_type(self):
        """Content type of current playing media."""
        return MEDIA_TYPE_MUSIC

    @property
    def media_image_url(self):
        """Image url of current playing media."""
        if self.player_state in (STATE_PLAYING, STATE_IDLE, STATE_PAUSED) and \
           self.current_title is not None:
            return self.client.artwork_url() + '?id=' + self.content_id

        return ''
#        return 'https://cloud.githubusercontent.com/assets/260/9829355' \
#            '/33fab972-58cf-11e5-8ea2-2ca74bdaae40.png'

    @property
    def media_title(self):
        """Title of current playing media."""
        return self.current_title

    @property
    def media_artist(self):
        """Artist of current playing media (Music track only)."""
        return self.current_artist

    @property
    def media_album_name(self):
        """Album of current playing media (Music track only)."""
        return self.current_album

    @property
    def media_playlist(self):
        """Title of the currently playing playlist."""
        return self.current_playlist

    @property
    def supported_features(self):
        """Flag media player features that are supported."""
        return SUPPORT_FORKEDDAAPD

    def set_volume_level(self, volume):
        """Set volume level, range 0..1."""
        response = self.client.set_volume(volume)
        if not bool(response):
            self.current_volume = volume
        else:
            self.update_state(response)

    def mute_volume(self, mute):
        """Mute (true) or unmute (false) media player."""
        response = self.client.set_muted(mute)
        self.update_state(response)

    def media_play(self):
        """Send media_play command to media player."""
        response = self.client.play()
        self.update_state(response)

    def media_pause(self):
        """Send media_pause command to media player."""
        response = self.client.pause()
        self.update_state(response)

    def media_next_track(self):
        """Send media_next command to media player."""
        response = self.client.next()
        self.update_state(response)

    def media_previous_track(self):
        """Send media_previous command media player."""
        response = self.client.previous()
        self.update_state(response)

    def play_media(self, media_type, media_id, **kwargs):
        """Send the play_media command to the media player."""
        if media_type == MEDIA_TYPE_MUSIC:
            response = self.client.play_music(media_id, False)
        elif media_type == MEDIA_TYPE_PLAYLIST:
            response = self.client.play_playlist(media_id)
            self.update_state(response)

    def turn_off(self):
        """Turn the media player off."""
        response = self.client.stop()
        self.update_state(response)


class AirPlayDevice(MediaPlayerDevice):
    """Representation an AirPlay device via a forked-daapd API instance."""

    def __init__(self, device_id, client):
        """Initialize the AirPlay device."""
        self._id = device_id
        self.client = client
        self.device_name = "AirPlay"
        self.kind = None
        self.active = False
        self.selected = False
        self.volume = 0
        self.supports_audio = False
        self.supports_video = False
        self.player_state = None

    def update_state(self, state_hash):
        """Update all the state properties with the passed in dictionary."""
        if 'player_state' in state_hash:
            self.player_state = state_hash.get('player_state', None)

        if 'name' in state_hash:
            name = state_hash.get('name', '')
            self.device_name = (name + ' AirTunes Speaker').strip()

        if 'selected' in state_hash:
            self.selected = state_hash.get('selected', None)
            self.active = state_hash.get('selected', None)

        if 'volume' in state_hash:
            self.volume = float(state_hash.get('volume', 0) / 100)

        self.supports_audio = True
        self.supports_video = False

    @property
    def name(self):
        """Return the name of the device."""
        return self.device_name

    @property
    def icon(self):
        """Return the icon to use in the frontend, if any."""
        if self.selected is True:
            return 'mdi:volume-high'

        return 'mdi:volume-off'

    @property
    def state(self):
        """Return the state of the device."""
        if self.selected is True:
            return STATE_ON

        return STATE_OFF

    def update(self):
        """Retrieve latest state."""

    @property
    def volume_level(self):
        """Return the volume."""
        return self.volume

    @property
    def media_content_type(self):
        """Flag of media content that is supported."""
        return MEDIA_TYPE_MUSIC

    @property
    def supported_features(self):
        """Flag media player features that are supported."""
        return SUPPORT_AIRPLAY

    def set_volume_level(self, volume):
        """Set volume level, range 0..1."""
        # volume = volume
        response = self.client.set_volume_airplay_device(self._id, volume)
        self.update_state(response)

    def turn_on(self):
        """Select AirPlay."""
        self.update_state({"selected": True})
        self.schedule_update_ha_state()
        response = self.client.toggle_airplay_device(self._id, True)
        self.update_state(response)

    def turn_off(self):
        """Deselect AirPlay."""
        self.update_state({"selected": False})
        self.schedule_update_ha_state()
        response = self.client.toggle_airplay_device(self._id, False)
        self.update_state(response)
