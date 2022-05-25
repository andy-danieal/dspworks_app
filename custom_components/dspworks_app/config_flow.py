"""Config flow for DSPWorks Automation Devices integration."""
from __future__ import annotations

import logging
from typing import Any
from homeassistant.components import persistent_notification
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_entry_oauth2_flow

from .const import DOMAIN, DSPWORKS_SCOPES

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

    @property
    def extra_authorize_data(self) -> dict[str, Any]:
        """Extra data that needs to be appended to the authorize url."""
        return {"scope": ",".join(DSPWORKS_SCOPES)}

    async def async_step_user(self, user_input=None):
        """Handle a flow start."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        return await super().async_step_user(user_input)
    
    async def async_oauth_create_entry(self, data: dict[str, Any]) -> FlowResult:
        """Create an entry for DSPWorks."""
        return self.async_create_entry(title="DSPWorks APP", data=data)
    
    async def async_step_reauth(self, entry: dict[str, Any]) -> FlowResult:
        """Perform reauth upon migration of old entries."""
        self.reauth_entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )

        persistent_notification.async_create(
            self.hass,
            f"DSPWorks integration for account needs to be re-authenticated. Please go to the integrations page to re-configure it.",
            "DSPWorks re-authentication",
            "dspworks_reauth",
        )

        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Confirm reauth dialog."""
        if self.reauth_entry is None:
            return self.async_abort(reason="reauth_account_mismatch")

        if user_input is None and self.reauth_entry:
            return self.async_show_form(
                step_id="reauth_confirm",
                description_placeholders={"account": self.context["entry_id"]},
                errors={},
            )

        persistent_notification.async_dismiss(self.hass, "dspworks_reauth")
        return await self.async_step_pick_implementation(
            user_input={"implementation": self.reauth_entry.data["auth_implementation"]}
        )
