"""The DSPWorks Automation Devices integration."""
from __future__ import annotations

from datetime import timedelta
from homeassistant.helpers.typing import ConfigType
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
    Platform,
)
from homeassistant.core import HomeAssistant

from homeassistant.helpers import (
    config_entry_oauth2_flow,
    config_validation as cv,
    device_registry as dr,
)

from .utils import Utils
from .const import *

import logging, json
import voluptuous as vol
from . import config_flow

# The DSPWorks only updates every 5-8 minutes as per the API spec so there's
# in polling the API more frequently
MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=300)


_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Inclusive(
                    CONF_CLIENT_ID, "oauth", default=OAUTH_CLIENT_ID
                ): cv.string,
                vol.Inclusive(
                    CONF_CLIENT_SECRET, "oauth", default=OAUTH_CLIENT_SECRET
                ): cv.string,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

PLATFORMS = [
    Platform.FAN,
]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the DSPWorks component."""
    _LOGGER.warning("SETUP [START]: %s", json.dumps(config[DOMAIN]))
    hass.data[DOMAIN] = {}

    config_flow.DSPWorksFlowHandler.async_register_implementation(
        hass,
        config_entry_oauth2_flow.LocalOAuth2Implementation(
            hass,
            DOMAIN,
            config[DOMAIN][CONF_CLIENT_ID],
            config[DOMAIN][CONF_CLIENT_SECRET],
            f"{DOMAIN_URL}{OAUTH_LOGIN_URL}",
            f"{DOMAIN_URL}{OAUTH_TOKEN_URL}",
        ),
    )

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up DSPWorks Automation Devices from a config entry."""
    _LOGGER.warning("SETUP [ENTRY]: %s", entry.data['auth_implementation'])

    hass.data[DOMAIN][entry.entry_id] = {}
    hass.data[DOMAIN]["token"] = entry.data['token']['access_token']
    devices = {}

    response = await Utils.async_dsp_api(hass, f"{DOMAIN_API_URL}{DISCOVERY_DEVICES}")
    devices.update({device["device_id"]: device for device in response["devices"]})
    hass.data[DOMAIN][entry.entry_id]["devices"] = devices    

    # Backwards compat
    if "auth_implementation" not in entry.data:
        hass.config_entries.async_update_entry(
            entry, data={**entry.data, "auth_implementation": DOMAIN}
        )

    implementation = (
        await config_entry_oauth2_flow.async_get_config_entry_implementation(
            hass, entry
        )
    )
    
    session = config_entry_oauth2_flow.OAuth2Session(hass, entry, implementation)
    await session.async_ensure_token_valid()
    
    device_registry = dr.async_get(hass)

    hass.config_entries.async_setup_platforms(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(config_entry_update_listener))

    return True


async def config_entry_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update listener, called when the config entry options are changed."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
