import logging
import time
from threading import Timer

import logging
import ipaddress


from homeassistant import core
from homeassistant.components.http import ban

#from homeassistant.components.http import ban

from homeassistant.components.http.ban import (
        NOTIFICATION_ID_BAN, NOTIFICATION_ID_LOGIN, 
        KEY_BANNED_IPS, KEY_FAILED_LOGIN_ATTEMPTS, KEY_LOGIN_THRESHOLD)
#from homeassistant.components.http import ban 


#from .mod_view import setup_view
#from .connection import setup_connection
#from .service import setup_service
#from .const import DOMAIN, DATA_DEVICES, DATA_ALIASES, DATA_ADDERS, CONFIG_DEVICES, DATA_CONFIG

from homeassistant.const import (
    EVENT_HOMEASSISTANT_START, EVENT_HOMEASSISTANT_STOP,
    SERVICE_HOMEASSISTANT_STOP, EVENT_TIME_CHANGED, EVENT_STATE_CHANGED,
    EVENT_CALL_SERVICE, ATTR_NOW, ATTR_DOMAIN, ATTR_SERVICE, MATCH_ALL,
    EVENT_SERVICE_REGISTERED)

DOMAIN = "unban"


_LOGGER = logging.getLogger(__name__)
myhass = None
never_ban_ips_list = []
never_ban_networks_list = []

#async def async_setup(hass, config):
def setup(hass, config):
    global myhass
    global never_ban_ips_list, never_ban_networks_list
    myhass = hass

    _LOGGER.info("auto_unban Setup.  Config: %s", config)

    domainconfig = config.get(DOMAIN)
    for entry in domainconfig['never_ban']:
        if "/" in entry:
            # Network CIDR
            network = ipaddress.IPv4Network(entry)
            never_ban_networks_list.append(network)
        else:
            # Single IP
            ip = ipaddress.IPv4Address(entry)
            never_ban_ips_list.append(ip)


        _LOGGER.info("auto_unban config entry: %s", entry)


    _LOGGER.info("auto_unban hass: %s", str(hass))
    _LOGGER.info("auto_unban hass.http: %s", str(hass.http))
    _LOGGER.info("auto_unban hass.http.app: %s", str(hass.http.app))

    if 'ha_banned_ips' in hass.http.app:
        _LOGGER.info("auto_unban hass.http.app[ha_banned_ips]: %s", str(hass.http.app["ha_banned_ips"]))
    else:
        _LOGGER.info("auto_unban no ha_banned_ips in app obj")

        timer = Timer(60.0, logInfo, [hass]) 
        timer.start() 


    #NOTIFICATION_ID_LOGIN = ban.NOTIFICATION_ID_LOGIN
    #NOTIFICATION_ID_BAN = ban.NOTIFICATION_ID_BAN

    # hass.bus.async_listen(NOTIFICATION_ID_LOGIN, _handle_event)
    # hass.bus.async_listen(NOTIFICATION_ID_BAN, _handle_event)

    #hass.bus.listen(NOTIFICATION_ID_LOGIN, _handle_event)
    #hass.bus.listen(NOTIFICATION_ID_BAN, _handle_event)

    #hass.bus.listen(MATCH_ALL, _handle_event)

    #hass.bus.listen("persistent_notification", _handle_event)
    hass.bus.listen("call_service", _handle_event)

    
    
    # aliases = {}
    # for d in config[DOMAIN].get(CONFIG_DEVICES, {}):
    #     name = config[DOMAIN][CONFIG_DEVICES][d].get("name", None)
    #     if name:
    #         aliases[name] = d.replace('_','-')

    # hass.data[DOMAIN] = {
    #     DATA_DEVICES: {},
    #     DATA_ALIASES: aliases,
    #     DATA_ADDERS: {},
    #     DATA_CONFIG: config[DOMAIN],
    #     }


    # hass.bus.async_listen(EVENT_STATE_CHANGED, elastic_event_listener)

    # hass.services.async_register(
    #     DOMAIN, 'publish_events', service_handler.publish_events)

    # await hass.helpers.discovery.async_load_platform("media_player", DOMAIN, {}, config)
    # await hass.helpers.discovery.async_load_platform("sensor", DOMAIN, {}, config)
    # await hass.helpers.discovery.async_load_platform("binary_sensor", DOMAIN, {}, config)
    # await hass.helpers.discovery.async_load_platform("light", DOMAIN, {}, config)
    # await hass.helpers.discovery.async_load_platform("camera", DOMAIN, {}, config)

    # await setup_connection(hass, config)

    # setup_service(hass)

    _LOGGER.info("auto_unban component fully initialized")
    return True

#async def _handle_event(self, call):
#async def _handle_event(event: core.Event):
def _handle_event(event):
    _LOGGER.info("auto_unban Event received event_type: %s", event.event_type)
    _LOGGER.info("auto_unban Event received origin: %s", event.origin)
    _LOGGER.info("auto_unban Event received context: %s", event.context)
    _LOGGER.info("auto_unban Event received data: %s", event.data)

    if 'domain' in event.data and "persistent_notification" == event.data["domain"] and event.data["service"] == "create":
        _LOGGER.info("auto_unban found persistent_notification")
        if 'service_data' in event.data and 'notification_id' in event.data["service_data"]:
          _LOGGER.info("auto_unban found notification_id")
          if NOTIFICATION_ID_LOGIN == event.data["service_data"]["notification_id"]:
              _handle_http_login_error(event)


def _handle_http_login_error(event):
    global myhass
    global never_ban_ips_list, never_ban_networks_list

    ip_address = _extract_ip_address(event)
    if 'ha_banned_ips' in myhass.http.app:
        _LOGGER.info("auto_unban logInfo hass.http.app[ha_banned_ips]: %s", str(myhass.http.app["ha_banned_ips"]))
        #hass.http.app["ha_banned_ips"]
        failed_count = myhass.http.app[KEY_FAILED_LOGIN_ATTEMPTS][ip_address]
        _LOGGER.info("auto_unban logInfo ip: %s failed_count: %d", ip_address, failed_count)
        _LOGGER.info("auto_unban logInfo map: %s", myhass.http.app[KEY_FAILED_LOGIN_ATTEMPTS])

        if _check_if_on_auto_unban_list(ip_address):
            # Reset to zero
            _LOGGER.info("auto_unban logInfo ip: %s on auto-unban list.  Resetting failed login attempts", ip_address)
            myhass.http.app[KEY_FAILED_LOGIN_ATTEMPTS][ip_address] = 0
            myhass.components.persistent_notification.dismiss(NOTIFICATION_ID_LOGIN)
        else:
            _LOGGER.info("auto_unban logInfo ip: %s not on auto-unban list. failed_count: %d", ip_address, failed_count)
  

def _check_if_on_auto_unban_list(ip_address: ipaddress.IPv4Address) -> bool:
    global never_ban_ips_list, never_ban_networks_list
    if ip_address in never_ban_ips_list:
        return True
    for network in never_ban_networks_list:
        if ip_address in network:
            return True
    return False


def _extract_ip_address(event) -> str:
    msg = event.data['service_data']['message']
    words = msg.split()
    ip_address = words[-1]
    _LOGGER.info("auto_unban Found http-login event ip_address: %s", ip_address)
    return ipaddress.ip_address(ip_address)


# async def async_setup_entry(hass, config_entry):
#     """Set up this integration using UI."""
#     return True


def logInfo(hass): 
    if 'ha_banned_ips' in hass.http.app:
        _LOGGER.info("auto_unban logInfo hass.http.app[ha_banned_ips]: %s", str(hass.http.app["ha_banned_ips"]))
    else:
        _LOGGER.info("auto_unban logInfo no ha_banned_ips in app obj")

    # hass.http.app["ha_failed_login_attempts"][remote_addr]
