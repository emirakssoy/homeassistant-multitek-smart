"""Data coordinator for Multitek Smart Home integration."""
from __future__ import annotations

import asyncio
from datetime import timedelta
import logging
from typing import Any

import aiohttp
import async_timeout

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    CONF_TABLET_IP,
    CONF_TABLET_PORT,
    CONF_API_KEY,
    CONF_USE_AUTH,
    DEFAULT_UPDATE_INTERVAL,
    API_DEVICES,
    API_RELAY_STATE,
    API_RELAY_TOGGLE,
)

_LOGGER = logging.getLogger(__name__)


class MultitekDataCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching data from Multitek tablet."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        self.entry = entry
        self.base_url = f"http://{entry.data[CONF_TABLET_IP]}:{entry.data[CONF_TABLET_PORT]}"
        self.session = async_get_clientsession(hass)
        self.headers = {}
        
        if entry.data.get(CONF_USE_AUTH, False):
            self.headers["X-HA-Access"] = entry.data.get(CONF_API_KEY, "")

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_UPDATE_INTERVAL),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API endpoint."""
        try:
            async with async_timeout.timeout(10):
                async with self.session.get(
                    f"{self.base_url}{API_DEVICES}",
                    headers=self.headers,
                ) as response:
                    if response.status != 200:
                        raise UpdateFailed(f"API returned status {response.status}")
                    
                    data = await response.json()
                    
                    # Convert list to dict with device ID as key
                    devices = {}
                    for device in data.get("devices", []):
                        device_id = str(device.get("id"))
                        devices[device_id] = device
                    
                    return devices
                    
        except asyncio.TimeoutError as err:
            raise UpdateFailed(f"Timeout fetching data from {self.base_url}") from err
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error fetching data: {err}") from err

    async def send_relay_command(
        self, device_id: str, command: str, value: Any = None
    ) -> dict[str, Any]:
        """Send a command to a relay device."""
        try:
            if command == "toggle":
                # Toggle endpoint
                url = f"{self.base_url}{API_RELAY_TOGGLE.format(device_id=device_id)}"
                method = "POST"
                json_data = {}
            else:
                # State endpoint
                url = f"{self.base_url}{API_RELAY_STATE.format(device_id=device_id)}"
                method = "POST"
                json_data = {"state": value}
            
            async with async_timeout.timeout(10):
                async with self.session.request(
                    method,
                    url,
                    headers=self.headers,
                    json=json_data,
                ) as response:
                    if response.status != 200:
                        error_data = await response.json()
                        raise Exception(
                            f"Command failed: {error_data.get('message', 'Unknown error')}"
                        )
                    
                    result = await response.json()
                    
                    # Update local data
                    if device_id in self.data:
                        self.data[device_id].update(result)
                        self.async_set_updated_data(self.data)
                    
                    return result
                    
        except asyncio.TimeoutError:
            _LOGGER.error("Timeout sending command to device %s", device_id)
            raise
        except Exception as err:
            _LOGGER.error("Error sending command to device %s: %s", device_id, err)
            raise

    async def test_connection(self) -> bool:
        """Test if we can connect to the tablet."""
        try:
            async with async_timeout.timeout(5):
                async with self.session.get(
                    f"{self.base_url}/api/status",
                    headers=self.headers,
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("online", False)
                    return False
        except Exception:
            return False
