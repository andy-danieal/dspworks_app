"""Config flow for DSPWorks Automation Devices integration."""
from __future__ import annotations

import logging

from homeassistant.helpers import config_entry_oauth2_flow

from .const import DOMAIN

# class ConfigFlowHandler(SchemaConfigFlowHandler, domain=DOMAIN):
#     """Handle a config or options flow for DSPWorks Automation Devices."""

#     def async_config_entry_title(self, options: Mapping[str, Any]) -> str:
#         """Return config entry title."""
#         return cast(str, options["name"]) if "name" in options else ""


class DSPWorksFlowHandler(
    config_entry_oauth2_flow.AbstractOAuth2FlowHandler, domain=DOMAIN
):
    """Config flow to handle DSPWorks OAuth2 authentication."""

    DOMAIN = DOMAIN

    @property
    def logger(self) -> logging.Logger:
        """Return logger."""
        return logging.getLogger(__name__)

    async def async_step_user(self, user_input=None):
        """Handle a flow start."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        return await super().async_step_user(user_input)
