"""Config flow for Binary Matrix 8x8 HDMI Switcher."""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT, CONF_USERNAME, CONF_PASSWORD
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
    DEFAULT_PORT,
    DEFAULT_USERNAME,
    ERROR_CANNOT_CONNECT,
    ERROR_INVALID_AUTH,
    ERROR_UNKNOWN,
)
from .matrix_controller import MatrixController, MatrixConnectionError, MatrixAuthError

_LOGGER = logging.getLogger(__name__)

class MatrixConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Binary Matrix 8x8 HDMI Switcher."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._reauth_entry: Optional[config_entries.ConfigEntry] = None

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: Dict[str, str] = {}

        if user_input is not None:
            try:
                # Validate connection and authentication
                matrix = MatrixController(
                    host=user_input[CONF_HOST],
                    port=user_input.get(CONF_PORT, DEFAULT_PORT),
                    username=user_input.get(CONF_USERNAME, DEFAULT_USERNAME),
                    password=user_input[CONF_PASSWORD],
                )

                await matrix.connect()
                await matrix.disconnect()

                # Create unique ID from host
                await self.async_set_unique_id(user_input[CONF_HOST])
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=user_input[CONF_NAME],
                    data=user_input,
                )

            except MatrixConnectionError:
                errors["base"] = ERROR_CANNOT_CONNECT
                _LOGGER.exception("Connection failed")
            except MatrixAuthError:
                errors["base"] = ERROR_INVALID_AUTH
                _LOGGER.exception("Authentication failed")
            except Exception as ex:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected error: %s", ex)
                errors["base"] = ERROR_UNKNOWN

        # Show initial configuration form
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME): str,
                    vol.Required(CONF_HOST): str,
                    vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
                    vol.Optional(CONF_USERNAME, default=DEFAULT_USERNAME): str,
                    vol.Required(CONF_PASSWORD): str,
                }
            ),
            errors=errors,
        )

    async def async_step_reauth(self, entry_data: Dict[str, Any]) -> FlowResult:
        """Handle reauth if authentication fails."""
        self._reauth_entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle reauthorization step."""
        errors: Dict[str, str] = {}

        if user_input is not None and self._reauth_entry:
            try:
                matrix = MatrixController(
                    host=self._reauth_entry.data[CONF_HOST],
                    port=self._reauth_entry.data.get(CONF_PORT, DEFAULT_PORT),
                    username=self._reauth_entry.data.get(CONF_USERNAME, DEFAULT_USERNAME),
                    password=user_input[CONF_PASSWORD],
                )

                await matrix.connect()
                await matrix.disconnect()

                entry_data = {
                    **self._reauth_entry.data,
                    CONF_PASSWORD: user_input[CONF_PASSWORD],
                }
                
                self.hass.config_entries.async_update_entry(
                    self._reauth_entry, data=entry_data
                )
                
                await self.hass.config_entries.async_reload(self._reauth_entry.entry_id)
                return self.async_abort(reason="reauth_successful")

            except MatrixAuthError:
                errors["base"] = ERROR_INVALID_AUTH
                _LOGGER.exception("Authentication failed during reauth")
            except MatrixConnectionError:
                errors["base"] = ERROR_CANNOT_CONNECT
                _LOGGER.exception("Connection failed during reauth")
            except Exception as ex:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected error during reauth: %s", ex)
                errors["base"] = ERROR_UNKNOWN

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema({vol.Required(CONF_PASSWORD): str}),
            errors=errors,
        )