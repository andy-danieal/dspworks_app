"""Support for DSPWorks fans."""
from __future__ import annotations

import logging
import math
from typing import Any, cast

from aiohttp.client_exceptions import ClientResponseError
import voluptuous as vol

from homeassistant.components.fan import (
    DIRECTION_FORWARD,
    DIRECTION_REVERSE,
    FanEntity,
    FanEntityFeature,
)

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util.percentage import (
    int_states_in_range,
    percentage_to_ranged_value,
    ranged_value_to_percentage,
)

from .const import DEVICE_SET, DOMAIN, DOMAIN_API_URL, SERVICE_SET_FAN_SPEED_TRACKED_STATE
from .entity import DSPEntity
from .utils import DSPDevice, Utils

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up DSP fan devices."""

    devices = hass.data[DOMAIN][entry.entry_id]["devices"]
    platform = entity_platform.async_get_current_platform()

    fans: list[Entity] = []

    for device in devices:
        fans.append(DSPWorksFan(DSPDevice(device, devices[device])))

    platform.async_register_entity_service(
        SERVICE_SET_FAN_SPEED_TRACKED_STATE,
        {vol.Required("speed"): vol.All(vol.Number(scale=0), vol.Range(0, 100))},
        "async_set_speed_belief",
    )

    _LOGGER.warning("Fan Entities Device : %s", fans)
    async_add_entities(fans, True)


class DSPWorksFan(DSPEntity, FanEntity):
    """Representation of a DSP fan."""

    def __init__(self, device: DSPDevice) -> None:
        """Create HA entity representing DSP fan."""
        #_LOGGER.warning("Fan HA Entity : %s", device)
        super().__init__(device)

        self._power: bool | None = None
        self._speed: int | None = None
        self._direction: int | None = None

    def _apply_state(self, state: dict) -> None:
        self._power = state.get("power")
        self._speed = state.get("speed")
        self._direction = state.get("direction")

    @property
    def supported_features(self) -> int:
        """Flag supported features."""
        features = 0
        if self._device.supports_speed():
            features |= FanEntityFeature.SET_SPEED
        if self._device.supports_direction():
            features |= FanEntityFeature.DIRECTION

        return features

    @property
    def _speed_range(self) -> tuple[int, int]:
        """Return the range of speeds."""
        return (1, 100)

    @property
    def percentage(self) -> int:
        """Return the current speed percentage for the fan."""
        if not self._speed or not self._power:
            return 0
        return min(
            100, max(0, ranged_value_to_percentage(self._speed_range, self._speed))
        )

    @property
    def speed_count(self) -> int:
        """Return the number of speeds the fan supports."""
        return int_states_in_range(self._speed_range)

    @property
    def current_direction(self) -> str | None:
        """Return fan rotation direction."""
        direction = None
        if self._direction == True:
            direction = DIRECTION_FORWARD
        elif self._direction == False:
            direction = DIRECTION_REVERSE

        return direction

    async def async_set_percentage(self, percentage: int) -> None:
        """Set the desired speed for the fan."""
        _LOGGER.warning("async_set_percentage called with percentage %s", percentage)

        if percentage == 0:
            await self.async_turn_off()
            return

        dsp_speed = math.ceil(percentage_to_ranged_value(self._speed_range, percentage))
        _LOGGER.warning(
            "async_set_percentage converted percentage %s to dsp speed %s",
            percentage,
            dsp_speed,
        )
        await Utils.async_dsp_api(self.hass, f"{DOMAIN_API_URL}{DEVICE_SET}"
            , {"device_id": self._device_id, "device_percentage_intensity": self._speed if percentage==None else percentage})
        

    async def async_set_power_belief(self, power_state: bool) -> None:
        """Set the believed state to on or off."""
        _LOGGER.warning("Fan State : %s - Default - %s", power_state, self._speed)
        await Utils.async_dsp_api(self.hass, f"{DOMAIN_API_URL}{DEVICE_SET}"
            , {"device_id": self._device_id, "device_percentage_intensity": -1 if power_state==True else 0})

    async def async_set_speed_belief(self, speed: int) -> None:
        """Set the believed speed for the fan."""
        _LOGGER.warning("async_set_speed_belief called with percentage %s", speed)
        await Utils.async_dsp_api(self.hass, f"{DOMAIN_API_URL}{DEVICE_SET}"
            , {"device_id": self._device_id, "device_percentage_intensity": self._speed if speed==None else speed})

    async def async_turn_on(
        self,
        percentage: int | None = None,
    ) -> None:
        """Turn on the fan."""
        _LOGGER.warning("Fan async_turn_on called with percentage %s - Default - %s", percentage, self._speed)
        await Utils.async_dsp_api(self.hass, f"{DOMAIN_API_URL}{DEVICE_SET}"
            , {"device_id": self._device_id, "device_percentage_intensity": -1 if percentage==None else percentage})


    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the fan off."""
        _LOGGER.warning("Fan async_turn_off called")
        await Utils.async_dsp_api(self.hass, f"{DOMAIN_API_URL}{DEVICE_SET}", {"device_id": self._device_id, "device_intensity": 0})
        

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the preset mode of the fan."""
        _LOGGER.warning("Fan Mode : %s", preset_mode)

    async def async_set_direction(self, direction: str) -> None:
        """Set fan rotation direction."""
        _LOGGER.warning("Fan Direction : %s", direction)
        await Utils.async_dsp_api(self.hass, f"{DOMAIN_API_URL}{DEVICE_SET}"
            , {"device_id": self._device_id, "device_direction": False if direction=='reverse' else True})
