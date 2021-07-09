# [owntone API](https://github.com/owntone/owntone-server/blob/master/README_JSON_API.md) hass.io custom component 
This provides a media player component for sending announcements to an [OwnTone](https://github.com/owntone/owntone-server) server.
In addition to controlling owntone, your available AirPlay endpoints will be added as media players as well. You can then individually address them and turn them on, turn them off or adjust their volume.

## Installation
1) Set up a owntone server in your system. Either:
   - Add my [repo](https://github.com/johnpdowling/hassio-addons) to hass.io and install the OwnTone add-on from there
   - Manually set up an OwnTone server on your system. Configure a library folder for %config%/owntone/ and use mkfifo to create a named pipe %config%/owntone/music/HomeAssistantAnnounce with generous rw permissions
2) Install component to %config%/custom_components/owntone/

## Configuration
To add owntone to your HA installation, add the following to your `configuration.yaml` file:

```yaml
# Example configuration.yaml entry
media_player:
  - platform: owntone
    host: 192.168.1.50
    port: 3689
```
```
host:
  description: The IP of the owntone API, e.g., 192.168.1.50.
  required: true
  type: string
port:
  description: The port where owntone is accessible, e.g., 3689.
  required: false
  default: 3689
  type: integer
```

## Thanks
A big thanks to [/u/sretalla](https://github.com/sretalla) for settings bugfixes
Patient users as I get to bug fixes
