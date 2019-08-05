"""Support for USPS packages and mail."""
from datetime import timedelta
import logging

import voluptuous as vol
import os

from homeassistant.const import (
    CONF_NAME, CONF_USERNAME, CONF_PASSWORD)
from homeassistant.helpers import (config_validation as cv, discovery)
from homeassistant.util import Throttle
from homeassistant.util.dt import now

_LOGGER = logging.getLogger(__name__)

#REQUIREMENTS = [ 'https://github.com/johnpdowling/python-myusps/zipball/master#myusps==1.3.3' ]

DOMAIN = 'usps'
DATA_USPS = 'data_usps'
MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=30)
COOKIE = 'usps_cookies.pickle'
CACHE = 'usps_cache'
CONF_DRIVER = 'driver'

USPS_TYPE = ['sensor', 'camera']

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Optional(CONF_NAME, default=DOMAIN): cv.string,
        vol.Optional(CONF_DRIVER): cv.string,
    }),
}, extra=vol.ALLOW_EXTRA)


def setup(hass, config):
    os.system("apk add --no-cache chromium")
    os.system("apk add --no-cache chromium-chromedriver")
    """Use config values to set up a function enabling status retrieval."""
    conf = config[DOMAIN]
    username = conf.get(CONF_USERNAME)
    password = conf.get(CONF_PASSWORD)
    name = conf.get(CONF_NAME)
    driver = conf.get(CONF_DRIVER)

    import myusps
    try:
        cookie = hass.config.path(COOKIE)
        cache = hass.config.path(CACHE)
        session = myusps.get_session(username, password,
                                     cookie_path=cookie, cache_path=cache,
                                     driver=driver)
    except myusps.USPSError:
        _LOGGER.exception('Could not connect to My USPS')
        return False

    hass.data[DATA_USPS] = USPSData(name, username, password, cookie, cache, driver)

    for component in USPS_TYPE:
        discovery.load_platform(hass, component, DOMAIN, {}, config)

    return True


class USPSData:
    """Stores the data retrieved from USPS.

    For each entity to use, acts as the single point responsible for fetching
    updates from the server.
    """

    def __init__(self, name, username, password, cookie, cache, driver):
        """Initialize the data object."""
        import myusps
        self.name = name
        self.username = username
        self.password = password
        self.cookie_path = cookie
        self.cache_path = cache
        self.driver = driver
        import myusps
        self.session = myusps.get_session(self.username, self.password,
                                     cookie_path=self.cookie_path, cache_path=self.cache_path,
                                     driver=self.driver)        
        
        self.packages = []
        self.mail = []
        self.attribution = None

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self, **kwargs):
        """Fetch the latest info from USPS. update the session every time"""
        import myusps
        self.session = myusps.get_session(self.username, self.password,
                                     cookie_path=self.cookie_path, cache_path=self.cache_path,
                                     driver=self.driver)
        self.packages = myusps.get_packages(self.session)
        self.mail = myusps.get_mail(self.session, now().date())
        self.attribution = myusps.ATTRIBUTION
        _LOGGER.debug("Mail, request date: %s, list: %s",
                      now().date(), self.mail)
        _LOGGER.debug("Package list: %s", self.packages)
