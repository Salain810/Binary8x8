"""The Binary Matrix 8x8 HDMI Switcher integration."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_USERNAME,
    Platform,
)
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    ATTR_INPUT,
    ATTR_OUTPUT,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    ERROR_CANNOT_CONNECT,
    ERROR_INVALID_AUTH,
    SERVICE_SWITCH_INPUT,
)
from .matrix_controller import (
    MatrixController,
    MatrixConnectionError,
    MatrixAuthError,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.NUMBER]

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Binary Matrix 8x8 HDMI Switcher component."""
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Binary Matrix 8x8 HDMI Switcher from a config entry."""
    _LOGGER.debug("Setting up Binary Matrix integration for %s", entry.data[CONF_HOST])
    
    try:
        matrix = MatrixController(
            host=entry.data[CONF_HOST],
            port=entry.data.get(CONF_PORT, 23),
            username=entry.data.get(CONF_USERNAME, "admin"),
            password=entry.data[CONF_PASSWORD],
        )

        try:
            await matrix.connect()
        except MatrixConnectionError as err:
            _LOGGER.error("Failed to connect to %s: %s", entry.data[CONF_HOST], err)
            raise ConfigEntryNotReady(f"Cannot connect to {entry.data[CONF_HOST]}") from err
        except MatrixAuthError as err:
            _LOGGER.error("Authentication failed for %s: %s", entry.data[CONF_HOST], err)
            raise ConfigEntryNotReady("Invalid authentication") from err
        except Exception as err:
            _LOGGER.exception("Unexpected error setting up matrix %s", entry.data[CONF_HOST])
            raise ConfigEntryNotReady("Unknown error occurred") from err

        async def async_update_data():
            """Fetch data from the Matrix."""
            try:
                return await matrix.update_state()
            except MatrixConnectionError as err:
                raise UpdateFailed(f"Connection failed: {err}") from err
            except MatrixAuthError as err:
                raise UpdateFailed(f"Authentication failed: {err}") from err
            except Exception as err:
                _LOGGER.exception("Error updating matrix state")
                raise UpdateFailed(f"Unknown error: {err}") from err

        coordinator = DataUpdateCoordinator(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_method=async_update_data,
            update_interval=entry.options.get("scan_interval", DEFAULT_SCAN_INTERVAL),
        )

        # Fetch initial data
        await coordinator.async_config_entry_first_refresh()

        hass.data[DOMAIN][entry.entry_id] = {
            "coordinator": coordinator,
            "matrix": matrix,
        }

        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

        async def switch_input(call: ServiceCall) -> None:
            """Handle switching input service call."""
            try:
                output = call.data[ATTR_OUTPUT]
                input_num = call.data[ATTR_INPUT]

                if not (1 <= output <= 8 and 1 <= input_num <= 8):
                    _LOGGER.error(
                        "Invalid output/input numbers. Both must be between 1 and 8"
                    )
                    return

                await matrix.switch_input(output, input_num)
                await coordinator.async_request_refresh()
            except (MatrixConnectionError, MatrixAuthError) as err:
                _LOGGER.error("Failed to switch input: %s", err)
                raise
            except Exception as err:
                _LOGGER.exception("Unexpected error switching input")
                raise

        # Register our services with Home Assistant
        hass.services.async_register(
            DOMAIN,
            SERVICE_SWITCH_INPUT,
            switch_input,
        )

        return True

    except Exception as err:
        _LOGGER.exception("Error setting up matrix integration")
        raise ConfigEntryNotReady from err

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    try:
        unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
        if unload_ok:
            matrix_data = hass.data[DOMAIN].pop(entry.entry_id)
            matrix: MatrixController = matrix_data["matrix"]
            await matrix.disconnect()
        return unload_ok
    except Exception as err:
        _LOGGER.exception("Error unloading matrix integration")
        return False