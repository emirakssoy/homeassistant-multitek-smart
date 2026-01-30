"""Switch platform for Multitek Smart Home integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    CONF_TABLET_IP,
    CONF_TABLET_PORT,
    RELAY_TYPE_LIGHT,
    RELAY_TYPE_ON_OFF,
    RELAY_TYPE_GAS,
    RELAY_TYPE_ELECTRIC,
    RELAY_TYPE_WATER,
    DEVICE_TYPE_ICONS,
    DEVICE_TYPE_NAMES,
    ATTR_DEVICE_TYPE,
    ATTR_ROOM_NAME,
    ATTR_FLAT_NAME,
    ATTR_FAVOURITE,
)
from .coordinator import MultitekDataCoordinator

_LOGGER = logging.getLogger(__name__)

# Device types that should be represented as switches
SWITCH_DEVICE_TYPES = [
    RELAY_TYPE_LIGHT,
    RELAY_TYPE_ON_OFF,
    RELAY_TYPE_GAS,
    RELAY_TYPE_ELECTRIC,
    RELAY_TYPE_WATER,
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Multitek switches from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    
    # Create switch entities for all devices
    entities = []
    for device_id, device_data in coordinator.data.items():
        device_type = device_data.get("type", RELAY_TYPE_ON_OFF)
        
        if device_type in SWITCH_DEVICE_TYPES:
            entities.append(
                MultitekRelaySwitch(
                    coordinator,
                    entry,
                    device_id,
                    device_data,
                )
            )
    
    async_add_entities(entities)
    
    # Listen for new devices
    @callback
    def handle_coordinator_update() -> None:
        """Handle updated data from the coordinator."""
        # Check for new devices
        current_devices = hass.data[DOMAIN][entry.entry_id].get("devices", {})
        new_entities = []
        
        for device_id, device_data in coordinator.data.items():
            if device_id not in current_devices:
                device_type = device_data.get("type", RELAY_TYPE_ON_OFF)
                
                if device_type in SWITCH_DEVICE_TYPES:
                    new_entities.append(
                        MultitekRelaySwitch(
                            coordinator,
                            entry,
                            device_id,
                            device_data,
                        )
                    )
                    current_devices[device_id] = True
        
        if new_entities:
            async_add_entities(new_entities)
            hass.data[DOMAIN][entry.entry_id]["devices"] = current_devices

    # Subscribe to coordinator updates
    coordinator.async_add_listener(handle_coordinator_update)


class MultitekRelaySwitch(CoordinatorEntity[MultitekDataCoordinator], SwitchEntity):
    """Representation of a Multitek relay switch."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: MultitekDataCoordinator,
        entry: ConfigEntry,
        device_id: str,
        device_data: dict[str, Any],
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_{device_id}"
        
        # Set initial device data
        self._update_from_data(device_data)

    def _update_from_data(self, device_data: dict[str, Any]) -> None:
        """Update entity attributes from device data."""
        device_type = device_data.get("type", RELAY_TYPE_ON_OFF)
        
        # Set name
        self._attr_name = device_data.get("name", f"Relay {self._device_id}")
        
        # Set icon based on device type
        self._attr_icon = DEVICE_TYPE_ICONS.get(device_type, "mdi:toggle-switch")
        
        # Set extra state attributes
        self._attr_extra_state_attributes = {
            ATTR_DEVICE_TYPE: device_data.get("type_name", DEVICE_TYPE_NAMES.get(device_type, "Unknown")),
            ATTR_ROOM_NAME: device_data.get("room_name", ""),
            ATTR_FLAT_NAME: device_data.get("flat_name", ""),
            ATTR_FAVOURITE: device_data.get("favourite", False),
        }
        
        # Set state
        self._attr_is_on = device_data.get("state", False)

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

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        device_data = self.coordinator.data.get(self._device_id)
        if device_data:
            self._update_from_data(device_data)
            self.async_write_ha_state()

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        await self.coordinator.send_relay_command(
            self._device_id, "set_state", True
        )
        
        # Optimistically update state
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        await self.coordinator.send_relay_command(
            self._device_id, "set_state", False
        )
        
        # Optimistically update state
        self._attr_is_on = False
        self.async_write_ha_state()

    async def async_toggle(self, **kwargs: Any) -> None:
        """Toggle the switch."""
        await self.coordinator.send_relay_command(
            self._device_id, "toggle", None
        )
        
        # Optimistically update state
        self._attr_is_on = not self._attr_is_on
        self.async_write_ha_state()
