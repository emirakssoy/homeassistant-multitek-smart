"""Config flow for Multitek Smart Home integration."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import async_timeout
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    DOMAIN,
    CONF_TABLET_IP,
    CONF_TABLET_PORT,
    CONF_API_KEY,
    CONF_USE_AUTH,
    DEFAULT_PORT,
    API_DISCOVER,
)

_LOGGER = logging.getLogger(__name__)


class MultitekConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Multitek Smart Home."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize."""
        self._discovered_info: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                # Test connection and get discovery info
                info = await self._test_connection(self.hass, user_input)
                
                # Store discovered info for use in next step
                self._discovered_info = info
                
                # Check if authentication is required
                if info.get("api", {}).get("auth_required", False):
                    # Need to get API key
                    return await self.async_step_auth()
                
                # Create unique ID from tablet IP and port
                await self.async_set_unique_id(
                    f"{user_input[CONF_TABLET_IP]}:{user_input[CONF_TABLET_PORT]}"
                )
                self._abort_if_unique_id_configured()

                # No auth required, create entry
                return self.async_create_entry(
                    title=f"Multitek Tablet ({user_input[CONF_TABLET_IP]})",
                    data={
                        **user_input,
                        CONF_USE_AUTH: False,
                        CONF_API_KEY: "",
                    },
                )
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        # Show form
        data_schema = vol.Schema(
            {
                vol.Required(CONF_TABLET_IP): str,
                vol.Optional(CONF_TABLET_PORT, default=DEFAULT_PORT): cv.port,
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    async def async_step_auth(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle authentication step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Test with API key
            full_config = {
                CONF_TABLET_IP: self._discovered_info.get("ip"),
                CONF_TABLET_PORT: self._discovered_info.get("port", DEFAULT_PORT),
                CONF_USE_AUTH: True,
                CONF_API_KEY: user_input[CONF_API_KEY],
            }
            
            try:
                await self._test_auth(self.hass, full_config)
                
                # Create unique ID
                await self.async_set_unique_id(
                    f"{full_config[CONF_TABLET_IP]}:{full_config[CONF_TABLET_PORT]}"
                )
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"Multitek Tablet ({full_config[CONF_TABLET_IP]})",
                    data=full_config,
                )
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:
                errors["base"] = "unknown"

        # Show auth form
        return self.async_show_form(
            step_id="auth",
            data_schema=vol.Schema({vol.Required(CONF_API_KEY): str}),
            errors=errors,
            description_placeholders={
                "tablet_ip": self._discovered_info.get("ip", "unknown"),
            },
        )

    async def _test_connection(
        self, hass: HomeAssistant, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Test if we can connect to the tablet."""
        session = async_get_clientsession(hass)
        base_url = f"http://{data[CONF_TABLET_IP]}:{data[CONF_TABLET_PORT]}"
        
        try:
            async with async_timeout.timeout(10):
                async with session.get(f"{base_url}{API_DISCOVER}") as response:
                    if response.status != 200:
                        raise CannotConnect(f"HTTP {response.status}")
                    
                    discovery_info = await response.json()
                    
                    # Store IP and port in discovery info
                    discovery_info["ip"] = data[CONF_TABLET_IP]
                    discovery_info["port"] = data[CONF_TABLET_PORT]
                    
                    return discovery_info
                    
        except asyncio.TimeoutError as err:
            raise CannotConnect("Timeout") from err
        except aiohttp.ClientError as err:
            raise CannotConnect(str(err)) from err

    async def _test_auth(
        self, hass: HomeAssistant, data: dict[str, Any]
    ) -> None:
        """Test authentication."""
        session = async_get_clientsession(hass)
        base_url = f"http://{data[CONF_TABLET_IP]}:{data[CONF_TABLET_PORT]}"
        headers = {"X-HA-Access": data[CONF_API_KEY]}
        
        try:
            async with async_timeout.timeout(10):
                async with session.get(
                    f"{base_url}/api/status", headers=headers
                ) as response:
                    if response.status == 401:
                        raise InvalidAuth("Invalid API key")
                    elif response.status != 200:
                        raise CannotConnect(f"HTTP {response.status}")
                    
        except asyncio.TimeoutError as err:
            raise CannotConnect("Timeout") from err
        except aiohttp.ClientError as err:
            raise CannotConnect(str(err)) from err

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return MultitekOptionsFlow(config_entry)


class MultitekOptionsFlow(config_entries.OptionsFlow):
    """Multitek config flow options handler."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options_schema = vol.Schema({})
        
        # Add API key option if auth is enabled
        if self.config_entry.data.get(CONF_USE_AUTH, False):
            options_schema = options_schema.extend(
                {
                    vol.Optional(
                        CONF_API_KEY,
                        default=self.config_entry.data.get(CONF_API_KEY, ""),
                    ): str,
                }
            )

        return self.async_show_form(
            step_id="init",
            data_schema=options_schema,
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
