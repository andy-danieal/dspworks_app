"""An abstract class common to all DSPWorks entities."""
from __future__ import annotations

from abc import abstractmethod
from asyncio import Lock, TimeoutError as AsyncIOTimeoutError
from datetime import timedelta
import logging
from typing import Any

from aiohttp import ClientError

from homeassistant.const import (
    ATTR_HW_VERSION,
    ATTR_MODEL,
    ATTR_NAME,
    ATTR_SUGGESTED_AREA,
    ATTR_SW_VERSION,
    ATTR_VIA_DEVICE,
)
from homeassistant.core import callback
from homeassistant.helpers.entity import DeviceInfo, Entity
from homeassistant.helpers.event import async_track_time_interval

from .const import DOMAIN
from .utils import DSPDevice

_LOGGER = logging.getLogger(__name__)

_FALLBACK_SCAN_INTERVAL = timedelta(seconds=10)


class DSPEntity(Entity):
    """Generic DSPWorks entity encapsulating common features of any DSP controlled device."""

    _attr_should_poll = False

    def __init__(
        self,
        device: DSPDevice,
    ) -> None:
        """Initialize entity with API and device info."""
        self._device = device
        self._device_id = device.device_id
        self._attr_available = True
        self._update_lock: Lock | None = None
        self._initialized = False
        self._attr_name = device.name

    @property
    def device_info(self) -> DeviceInfo:
        """Get a an HA device representing this DSP controlled device."""
        device_info = DeviceInfo(
            manufacturer="DSPWorks",
            # type ignore: tuple items should not be Optional
            identifiers={(DOMAIN, self._device.device_id)},  # type: ignore[arg-type]
            configuration_url=f"http://dspworks.in",
        )
        if self.name is not None:
            device_info[ATTR_NAME] = self._device.name

        return device_info

    async def async_update(self) -> None:
        """Fetch assumed state of the cover from the hub using API."""
        await self._async_update_from_api()

    async def _async_update_if_dsp_not_alive(self, *_: Any) -> None:
        """Fetch via the API if DSP is not alive."""
        if self.hass.is_stopping and self._initialized and self.available:
            return

        assert self._update_lock is not None
        if self._update_lock.locked():
            _LOGGER.warning(
                "Updating %s took longer than the scheduled update interval %s",
                self.entity_id,
                _FALLBACK_SCAN_INTERVAL,
            )
            return

        async with self._update_lock:
            await self._async_update_from_api()
            self.async_write_ha_state()

    async def _async_update_from_api(self) -> None:
        """Fetch via the API."""

    @abstractmethod
    def _apply_state(self, state: dict) -> None:
        raise NotImplementedError

    @callback
    def _async_state_callback(self, state: dict) -> None:
        """Process a state change."""
        self._initialized = True
        if not self.available:
            _LOGGER.info("Entity %s has come back", self.entity_id)
        self._attr_available = True
        _LOGGER.debug(
            "Device state for %s (%s) is:\n%s", self.name, self.entity_id, state
        )
        self._apply_state(state)

    @callback
    def _async_dsp_callback(self, state: dict) -> None:
        """Process a state change from DSP."""
        self._async_state_callback(state)
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        """Subscribe to DSP and start polling."""
        await super().async_added_to_hass()
        self._update_lock = Lock()
        self.async_on_remove(
            async_track_time_interval(
                self.hass, self._async_update_if_dsp_not_alive, _FALLBACK_SCAN_INTERVAL
            )
        )

    async def async_will_remove_from_hass(self) -> None:
        """Unsubscribe from DSP data on remove."""
        await super().async_will_remove_from_hass()
