# [owntone API](https://github.com/owntone/owntone-server/blob/master/README_JSON_API.md) hass.io custom integration 
This provides a media player component for sending announcements to an [OwnTone](https://github.com/owntone/owntone-server) server.
In addition to controlling owntone, your available AirPlay endpoints will be added as media players as well. You can then individually address them and turn them on, turn them off or adjust their volume.

## Installation
1) Set up a owntone server in your system. Either:
   - Add my [repo](https://github.com/johnpdowling/hassio-addons) to hass.io and install the OwnTone add-on from there
   - Manually set up an OwnTone server on your system. Configure a library folder for %config%/owntone/ and use mkfifo to create a named pipe %config%/owntone/music/HomeAssistantAnnounce with generous rw permissions
2) Install component to %config%/custom_components/owntone/

## Configuration
You should see an OwnTone integration pop up with your OwnTone server in Integrations, possibly next to forked-daapd and Apple integrations as well. I ignored the other integrations for my server and configured for the OwnTone one.

## Thanks
Patient users as I get to bug fixes
