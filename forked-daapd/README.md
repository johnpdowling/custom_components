# [forked-daapd API](https://github.com/ejurgensen/forked-daapd/blob/master/README_JSON_API.md) hass.io custom component 
This provides a media player component for sending announcements to a [forked-daapd](https://github.com/ejurgensen/forked-daapd) server.
In addition to controlling forked-daapd, your available AirPlay endpoints will be added as media players as well. You can then individually address them and turn them on, turn them off or adjust their volume.

## Installation
1) Set up a forked-daapd server in your system. Configure a library folder for %config%/forked-daapd/
2) Install component to %config%/custom_components/forked-daapd/
3) Create a named pipe %config%/forked-daapd/HomeAssistantAnnounce

## Configuration
To add forked-daapd to your HA installation, add the following to your `configuration.yaml` file:

```yaml
# Example configuration.yaml entry
media_player:
  - platform: forked-daapd
    host: 192.168.1.50
    port: 3689
```
```
host:
  description: The IP of the forked-daapd API, e.g., 192.168.1.50.
  required: true
  type: string
port:
  description: The port where forked-daapd is accessible, e.g., 3689.
  required: false
  default: 3689
  type: integer
```
