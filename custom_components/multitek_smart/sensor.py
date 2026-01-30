"""Sensor platform for Multitek Smart Home integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CONF_TABLET_IP, CONF_TABLET_PORT
from .coordinator import MultitekDataCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Multitek sensors from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    
    # Add status sensors
    entities = [
        MultitekDeviceCountSensor(coordinator, entry),
        MultitekConnectionStatusSensor(coordinator, entry),
    ]
    
    async_add_entities(entities)


class MultitekDeviceCountSensor(CoordinatorEntity[MultitekDataCoordinator], SensorEntity):
    """Sensor showing the count of connected devices."""

    _attr_has_entity_name = True
    _attr_name = "Connected Devices"
    _attr_icon = "mdi:devices"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: MultitekDataCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_device_count"

    @property
    def native_value(self) -> int:
        """Return the number of connected devices."""
        return len(self.coordinator.data)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        device_types = {}
        for device in self.coordinator.data.values():
            device_type = device.get("type_name", "unknown")
            device_types[device_type] = device_types.get(device_type, 0) + 1
        
        return {
            "device_types": device_types,
            "tablet_ip": self._entry.data[CONF_TABLET_IP],
            "tablet_port": self._entry.data[CONF_TABLET_PORT],
        }

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, f"{self._entry.data[CONF_TABLET_IP]}:{self._entry.data[CONF_TABLET_PORT]}")},
            name=f"Multitek Tablet {self._entry.data[CONF_TABLET_IP]}",
            manufacturer="Multitek",
            model="Smart Tablet",
            configuration_url=f"http://{self._entry.data[CONF_TABLET_IP]}:{self._entry.data[CONF_TABLET_PORT]}",
        )


class MultitekConnectionStatusSensor(CoordinatorEntity[MultitekDataCoordinator], SensorEntity):
    """Sensor showing the connection status to the tablet."""

    _attr_has_entity_name = True
    _attr_name = "Connection Status"
    _attr_icon = "mdi:connection"

    def __init__(
        self,
        coordinator: MultitekDataCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_connection_status"

    @property
    def native_value(self) -> str:
        """Return the connection status."""
        if self.coordinator.last_update_success:
            return "Connected"
        return "Disconnected"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        attrs = {
            "tablet_ip": self._entry.data[CONF_TABLET_IP],
            "tablet_port": self._entry.data[CONF_TABLET_PORT],
        }
        
        if self.coordinator.last_update_success and self.coordinator.last_update:
            attrs["last_update"] = self.coordinator.last_update.isoformat()
            
        return attrs

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, f"{self._entry.data[CONF_TABLET_IP]}:{self._entry.data[CONF_TABLET_PORT]}")},
            name=f"Multitek Tablet {self._entry.data[CONF_TABLET_IP]}",
            manufacturer="Multitek",
            model="Smart Tablet",
            configuration_url=f"http://{self._entry.data[CONF_TABLET_IP]}:{self._entry.data[CONF_TABLET_PORT]}",
        )
