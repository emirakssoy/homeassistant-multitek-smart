"""The Multitek Smart Home integration."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp
import async_timeout

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    DOMAIN,
    CONF_TABLET_IP,
    CONF_TABLET_PORT,
    CONF_API_KEY,
    CONF_USE_AUTH,
    API_STATUS,
)
from .coordinator import MultitekDataCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SWITCH, Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Multitek Smart Home from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Test connection to tablet
    session = async_get_clientsession(hass)
    base_url = f"http://{entry.data[CONF_TABLET_IP]}:{entry.data[CONF_TABLET_PORT]}"
    
    try:
        async with async_timeout.timeout(10):
            headers = {}
            if entry.data.get(CONF_USE_AUTH, False):
                headers["X-HA-Access"] = entry.data.get(CONF_API_KEY, "")
            
            async with session.get(f"{base_url}{API_STATUS}", headers=headers) as response:
                if response.status != 200:
                    raise ConfigEntryNotReady(f"Cannot connect to tablet: {response.status}")
                
                data = await response.json()
                if not data.get("online"):
                    raise ConfigEntryNotReady("Tablet server is not online")
                    
    except asyncio.TimeoutError as err:
        raise ConfigEntryNotReady(f"Timeout connecting to tablet at {base_url}") from err
    except aiohttp.ClientError as err:
        raise ConfigEntryNotReady(f"Error connecting to tablet: {err}") from err

    # Create coordinator for this entry
    coordinator = MultitekDataCoordinator(hass, entry)
    
    # Store coordinator
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "devices": {},
    }

    # Perform initial data fetch
    await coordinator.async_config_entry_first_refresh()

    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register device in device registry
    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, f"{entry.data[CONF_TABLET_IP]}:{entry.data[CONF_TABLET_PORT]}")},
        manufacturer="Multitek",
        model="Smart Tablet",
        name=f"Multitek Tablet {entry.data[CONF_TABLET_IP]}",
        sw_version="1.0.0",
        configuration_url=f"http://{entry.data[CONF_TABLET_IP]}:{entry.data[CONF_TABLET_PORT]}",
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
