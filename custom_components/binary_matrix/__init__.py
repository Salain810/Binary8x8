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
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

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


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Binary Matrix 8x8 HDMI Switcher from a config entry."""
    matrix = MatrixController(
        host=entry.data[CONF_HOST],
        port=entry.data.get(CONF_PORT),
        username=entry.data.get(CONF_USERNAME),
        password=entry.data[CONF_PASSWORD],
    )

    try:
        await matrix.connect()
    except MatrixConnectionError as err:
        raise ConfigEntryNotReady(ERROR_CANNOT_CONNECT) from err
    except MatrixAuthError as err:
        raise ConfigEntryNotReady(ERROR_INVALID_AUTH) from err

    async def async_update_data():
        """Fetch data from the Matrix."""
        try:
            return await matrix.update_state()
        except (MatrixConnectionError, MatrixAuthError) as err:
            # Signal to HA that we need to retry
            raise ConfigEntryNotReady from err

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
        update_method=async_update_data,
        update_interval=entry.options.get("scan_interval", DEFAULT_SCAN_INTERVAL),
    )

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "matrix": matrix,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    async def switch_input(call: ServiceCall) -> None:
        """Handle switching input service call."""
        output = call.data[ATTR_OUTPUT]
        input_num = call.data[ATTR_INPUT]

        try:
            await matrix.switch_input(output, input_num)
            await coordinator.async_refresh()
        except (MatrixConnectionError, MatrixAuthError) as err:
            _LOGGER.error("Failed to switch input: %s", err)
            raise

    # Register our services with Home Assistant
    hass.services.async_register(
        DOMAIN,
        SERVICE_SWITCH_INPUT,
        switch_input,
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        matrix_data = hass.data[DOMAIN].pop(entry.entry_id)
        matrix: MatrixController = matrix_data["matrix"]
        await matrix.disconnect()

    return unload_ok