"""Number platform for Binary Matrix 8x8 HDMI Switcher."""
from __future__ import annotations

import logging
from typing import Any, Final

from homeassistant.components.number import (
    NumberEntity,
    NumberEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN, MATRIX_SIZE
from .matrix_controller import MatrixController

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the matrix number entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    matrix = hass.data[DOMAIN][entry.entry_id]["matrix"]

    entities = []
    for output in range(1, MATRIX_SIZE + 1):
        entities.append(
            MatrixOutputNumber(
                coordinator,
                matrix,
                output,
                entry,
            )
        )

    async_add_entities(entities)


class MatrixOutputNumber(CoordinatorEntity, NumberEntity):
    """Representation of a matrix output."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        matrix: MatrixController,
        output: int,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the matrix output."""
        super().__init__(coordinator)
        self._matrix = matrix
        self._output = output
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=f"Binary Matrix 8x8 ({entry.data[CONF_HOST]})",
            manufacturer="Binary",
            model="8x8 HDMI Matrix",
            sw_version="1.0.0",
        )
        self._attr_unique_id = f"{entry.entry_id}_output_{output}"
        self._attr_native_min_value = 1
        self._attr_native_max_value = MATRIX_SIZE
        self._attr_native_step = 1
        self._attr_mode = "slider"
        self._attr_icon = "mdi:video-input-hdmi"
        self._attr_has_entity_name = True
        self._attr_translation_key = "output"

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return f"Output {self._output}"

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self._matrix.connected and super().available

    @property
    def native_value(self) -> float | None:
        """Return the current input for this output."""
        if self.coordinator.data is None:
            return None
        return float(self.coordinator.data.get(self._output, 1))

    async def async_set_native_value(self, value: float) -> None:
        """Set the input for this output."""
        await self._matrix.switch_input(self._output, int(value))
        await self.coordinator.async_request_refresh()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()