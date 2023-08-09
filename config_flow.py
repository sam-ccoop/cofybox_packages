"""Config flow for cofybox_packages integration."""
import logging
import re

from typing import Any, Optional, Dict

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.helpers import selector
import homeassistant.helpers.config_validation as cv

from . import const
from .services import move_package, append_secret, find_and_replace_shelly

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required("name"): selector.TextSelector(),
    }
)

DEVICES = [
    const.SUNNYBOY_PV,
    const.SUNNYBOY_BATTERY,
    const.EMONCMS,
    const.EMONEVSE,
    const.SONNEN,
    const.VIESSMANN,
    const.VICTRON,
    const.NIBE,
    const.SGREADY,
    const.SHELLY_METER,
    const.SHELLY_HEATER
]

DEVICES_SCHEMA = vol.Schema({vol.Required("selected_device"): vol.In(DEVICES)})

SECRETS_SCHEMA_SUNNYBOY_BATTERY = vol.Schema(
    {vol.Required("sbs_host"): cv.string, vol.Optional("add_another"): cv.boolean}
)

SECRETS_SCHEMA_SUNNYBOY_PV = vol.Schema(
    {vol.Required("sb_host"): cv.string, vol.Optional("add_another"): cv.boolean}
)

SECRETS_SCHEMA_EMON = vol.Schema(
    {
        vol.Required("emoncms_api"): cv.string,
        vol.Required("emoncms_url"): cv.string,
        vol.Optional("add_another"): cv.boolean,
    }
)

SECRETS_SCHEMA_VICTRON = vol.Schema(
    {vol.Required("victron_host"): cv.string, vol.Optional("add_another"): cv.boolean}
)

SB_AUTO_REQUIRED_SCHEMA = vol.Schema(
    {vol.Required("login_known"): vol.In(("Yes", "No"))}
)


def hass_entity_ids(hass: HomeAssistant) -> list[str]:
    """Return all entity IDs in Home Assistant."""
    return list(hass.states.async_entity_ids())


class ConfigFlowHandler(config_entries.ConfigFlow, domain=const.DOMAIN):
    """Handle a config or options flow for cofybox_packages."""

    data: Optional[Dict[str, Any]]

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None):
        """First step in in the config flow - get the devices."""
        errors: Optional[Dict[str, Any]] = {}
        if user_input is not None:
            if not errors:
                self.data = user_input
                if user_input.get("selected_device"):
                    match user_input["selected_device"]:
                        case const.SHELLY_METER:
                            return await self.async_step_shelly_selector_meter()
                        case const.SHELLY_HEATER:
                            return await self.async_step_shelly_selector_heater()
                        case const.EMONEVSE:
                            move_package(const.EMONEVSE)
                            return self.async_create_entry(
                                title="EmonEVSE", data={"config_worked": "yes"}
                            )
                        case const.VICTRON:
                            return await self.async_step_secrets_victron()
                        case const.EMONCMS:
                            return await self.async_step_secrets_emon()
                        case const.SUNNYBOY_BATTERY:
                            return await self.async_step_sb_auto_required()
                        case const.SUNNYBOY_PV:
                            return await self.async_step_sb_auto_required()
                        case const.SONNEN:
                            move_package(const.SONNEN)
                            return self.async_create_entry(
                                title="sonnen", data={"config_worked": "yes"}
                            )
                        case const.VIESSMANN:
                            move_package(const.VIESSMANN)
                            return self.async_create_entry(
                                title="viessmann", data={"config_worked": "yes"}
                            )
                        case const.NIBE:
                            move_package(const.NIBE)
                            return self.async_create_entry(
                                title="nibe", data={"config_worked": "yes"}
                            )
                        case const.SGREADY:
                            move_package(const.SGREADY)
                            return self.async_create_entry(
                                title="sgready", data={"config_worked": "yes"}
                            )

        return self.async_show_form(
            step_id="user", data_schema=DEVICES_SCHEMA, errors=errors
        )
    
    async def async_step_shelly_selector_meter(
        self, user_input: Optional[Dict[str, Any]] = None
    ):
        """Second step in config flow to select which shelly."""
        SCHEMA_SHELLY = vol.Schema({vol.Required("entity_id"): vol.In(hass_entity_ids(self.hass))})
        errors: Dict[str, str] = {}

        if user_input is not None:
            if not errors:
                pattern = r'^sensor\.shelly_em_([a-zA-Z0-9]+)_'
                shelly_entity = user_input['entity_id']
                match = re.match(pattern, shelly_entity)
                if match:
                        shelly_id = match.group(1)
                        self.data["shelly_id"] = shelly_id
                        find_and_replace_shelly(const.SHELLY_METER_PATH, shelly_id)
                        move_package(const.SHELLY_METER)
                        return self.async_create_entry(
                                title=const.SHELLY_METER, data={"config_worked": "yes"}
                            )
                else:
                    _LOGGER.info("No shelly ID found")
                        

        return self.async_show_form(
            step_id="shelly_selector_meter", data_schema=SCHEMA_SHELLY, errors=errors
        )
    
    async def async_step_shelly_selector_heater(
        self, user_input: Optional[Dict[str, Any]] = None
    ):
        """Second step in config flow to select which shelly."""
        SCHEMA_SHELLY = vol.Schema({vol.Required("entity_id"): vol.In(hass_entity_ids(self.hass))})
        errors: Dict[str, str] = {}

        if user_input is not None:
            if not errors:
                pattern = r'^sensor\.shelly_em_([a-zA-Z0-9]+)_'
                shelly_entity = user_input['entity_id']
                match = re.match(pattern, shelly_entity)
                if match:
                        shelly_id = match.group(1)
                        self.data["shelly_id"] = shelly_id
                        _LOGGER.info(f"Shelly ID found: {shelly_id}")
                        find_and_replace_shelly(const.SHELLY_HEATER_PATH, shelly_id)
                        move_package(const.SHELLY_HEATER)
                        return self.async_create_entry(
                                title=const.SHELLY_HEATER, data={"config_worked": "yes"}
                            )
                else:
                    _LOGGER.info("No shelly ID found")
                        

        return self.async_show_form(
            step_id="shelly_selector_heater", data_schema=SCHEMA_SHELLY, errors=errors
        )

    async def async_step_secrets_victron(
        self, user_input: Optional[Dict[str, Any]] = None
    ):
        """Second step in config flow to add secrets for the victron."""
        errors: Dict[str, str] = {}
        if user_input is not None:
            if not errors:
                append_secret(user_input)
                move_package(const.VICTRON)
                if user_input.get("add_another", False):
                    return await self.async_step_user()
                else:
                    return self.async_create_entry(
                        title="secrets_victron", data=self.data
                    )

        return self.async_show_form(
            step_id="secrets_victron", data_schema=SECRETS_SCHEMA_VICTRON, errors=errors
        )

    async def async_step_secrets_emon(
        self, user_input: Optional[Dict[str, Any]] = None
    ):
        """Second step in config flow to add secrets for the emon."""
        errors: Dict[str, str] = {}
        if user_input is not None:
            if not errors:
                append_secret(user_input)
                move_package(const.EMONCMS)
                if user_input.get("add_another", False):
                    return await self.async_step_user()
                else:
                    return self.async_create_entry(title="emoncms", data=self.data)

        return self.async_show_form(
            step_id="secrets_emon", data_schema=SECRETS_SCHEMA_EMON, errors=errors
        )

    async def async_step_sb_auto_required(
        self, user_input: Optional[Dict[str, Any]] = None
    ):
        """
        Find out whether we need to use the auto/manual version of the SB package.
        Login known means we use the automatic variation. For the auto PV, we don't need secret.
        """
        errors: Dict[str, str] = {}
        if user_input is not None:
            if not errors:
                self.data.update(user_input)
                if self.data["selected_device"] == const.SUNNYBOY_BATTERY:
                    return await self.async_step_secrets_sunnyboy_battery()
                if self.data["selected_device"] == const.SUNNYBOY_PV:
                    return await self.async_step_secrets_sunnyboy_pv()

        return self.async_show_form(
            step_id="sb_auto_required",
            data_schema=SB_AUTO_REQUIRED_SCHEMA,
            errors=errors,
        )

    async def async_step_secrets_sunnyboy_battery(
        self, user_input: Optional[Dict[str, Any]] = None
    ):
        """Second step in config flow to add secrets for the sunnyboy battery."""
        errors: Dict[str, str] = {}
        if user_input is not None:
            if not errors:
                if self.data["login_known"] == "Yes":
                    move_package(const.SUNNYBOY_BATTERY_AUTO)
                    append_secret(user_input)
                elif self.data["login_known"] == "No":
                    move_package(const.SUNNYBOY_BATTERY_MANUAL)
                    append_secret(user_input)
                if user_input.get("add_another", False):
                    return await self.async_step_user()
                else:
                    return self.async_create_entry(
                        title="sunnyboy_battery", data=self.data
                    )

        return self.async_show_form(
            step_id="secrets_sunnyboy_battery",
            data_schema=SECRETS_SCHEMA_SUNNYBOY_BATTERY,
            errors=errors,
        )

    async def async_step_secrets_sunnyboy_pv(
        self, user_input: Optional[Dict[str, Any]] = None
    ):
        """Second step in config flow to add secrets for the sunnyboy PV."""
        errors: Dict[str, str] = {}
        if user_input is not None:
            if not errors:
                if self.data["login_known"] == "Yes":
                    move_package(const.SUNNYBOY_PV_AUTO)
                    append_secret(user_input)
                elif self.data["login_known"] == "No":
                    move_package(const.SUNNYBOY_PV_MANUAL)
                    append_secret(user_input)
                if user_input.get("add_another", False):
                    return await self.async_step_user()
                else:
                    return self.async_create_entry(title="sunnyboy_pv", data=self.data)

        return self.async_show_form(
            step_id="secrets_sunnyboy_pv",
            data_schema=SECRETS_SCHEMA_SUNNYBOY_PV,
            errors=errors,
        )
