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

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: Dict[str, str] = {}

        if user_input is not None:
            try:
                matrix = MatrixController(
                    host=user_input[CONF_HOST],
                    port=user_input.get(CONF_PORT, DEFAULT_PORT),
                    username=user_input.get(CONF_USERNAME, DEFAULT_USERNAME),
                    password=user_input[CONF_PASSWORD],
                )

                try:
                    await matrix.connect()
                    await matrix.disconnect()
                except Exception as err:
                    _LOGGER.error("Connection test failed: %s", err)
                    if isinstance(err, MatrixAuthError):
                        errors["base"] = ERROR_INVALID_AUTH
                    elif isinstance(err, MatrixConnectionError):
                        errors["base"] = ERROR_CANNOT_CONNECT
                    else:
                        errors["base"] = ERROR_UNKNOWN
                    raise

                await self.async_set_unique_id(user_input[CONF_HOST])
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=user_input[CONF_NAME],
                    data=user_input,
                )

            except Exception as err:
                _LOGGER.exception("Unexpected error: %s", err)
                if not errors:
                    errors["base"] = ERROR_UNKNOWN

        # Show configuration form
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