"""Reusable utilities for the DSPWorks component."""
from __future__ import annotations

import logging
from typing import Any, cast

MAX_REQUESTS = 6

_LOGGER = logging.getLogger(__name__)


class DSPDevice:
    """Helper device class to hold ID and attributes together."""

    def __init__(self, device_id: str, attrs: dict[str, Any]) -> None:
        """Create a helper device from ID and attributes returned by API."""
        self.device_id = device_id
        self._attrs = attrs or {}

    def __repr__(self) -> str:
        """Return readable representation of a bond device."""
        return {
            "device_id": self.device_id,
            "attrs": self._attrs,
        }.__repr__()

    @property
    def name(self) -> str:
        """Get the name of this device."""
        return cast(str, self._attrs["device_name"])

    @property
    def type(self) -> str:
        """Get the type of this device."""
        return cast(str, self._attrs["type"])

    @property
    def location(self) -> str | None:
        """Get the location of this device."""
        return self._attrs.get("location")

    @property
    def template(self) -> str | None:
        """Return this model template."""
        return self._attrs.get("template")

    @property
    def branding_profile(self) -> str | None:
        """Return this branding profile."""
        return "DSPWorks"

    @property
    def trust_state(self) -> bool:
        """Check if Trust State is turned on."""
        return True

    def has_action(self, action: str) -> bool:
        """Check to see if the device supports an actions."""
        return action in self._supported_actions

    def _has_any_action(self, actions: set[str]) -> bool:
        """Check to see if the device supports any of the actions."""
        return bool(self._supported_actions.intersection(actions))

    def supports_speed(self) -> bool:
        """Return True if this device supports any of the speed related commands."""
        return True

    def supports_direction(self) -> bool:
        """Return True if this device supports any of the direction related commands."""
        return True

    def supports_light(self) -> bool:
        """Return True if this device supports any of the light related commands."""
        return True

    def supports_up_light(self) -> bool:
        """Return true if the device has an up light."""
        return True

    def supports_down_light(self) -> bool:
        """Return true if the device has a down light."""
        return True

    def supports_set_brightness(self) -> bool:
        """Return True if this device supports setting a light brightness."""
        return True
