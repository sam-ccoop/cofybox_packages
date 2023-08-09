""" This module provides services for addings cofybox packages """

import shutil
import yaml

from . import const


def move_package(device: str):
    """Move cofybox package according to selected device."""
    dest_path = "/config/.storage/packages/"
    src_paths = {
        const.EMONCMS: [
            "/config/library/emoncms.yaml",
        ],
        const.EMONEVSE:[
            "/config/library/emonevse.yaml"
        ],
        const.VICTRON: [
            "/config/library/battery_victron_ess.yaml",
            "/config/library/generic_battery_dispatch.yaml",
            "/config/library/generic_flexibility.yaml",
        ],
        const.VIESSMANN: [
            "/config/library/heatpump_viessmann.yaml",
            "/config/library/generic_heatpump_dispatch.yaml",
            "/config/library/generic_flexibility.yaml",
        ],
        const.NIBE: [
            "/config/library/heatpump_nibe_f_series.yaml",
            "/config/library/generic_heatpump_dispatch.yaml",
            "/config/library/generic_flexibility.yaml",
        ],
        const.SGREADY: [
            "/config/library/heatpump_sgready_cookie.yaml",
            "/config/library/generic_heatpump_dispatch.yaml",
            "/config/library/generic_flexibility.yaml",
        ],
        const.SONNEN: [
            "/config/library/battery_sonnen_publish.yaml",
            "/config/library/generic_battery_dispatch.yaml",
            "/config/library/generic_flexibility.yaml",
        ],
        const.SUNNYBOY_BATTERY_MANUAL: [
            "/config/library/battery_sma_sunnyboy_storage_manual.yaml",
            "/config/library/generic_battery_dispatch.yaml",
            "/config/library/generic_flexibility.yaml",
        ],
        const.SUNNYBOY_BATTERY_AUTO: [
            "/config/library/battery_sma_sunnyboy_storage.yaml",
            "/config/library/generic_battery_dispatch.yaml",
            "/config/library/generic_flexibility.yaml",
        ],
        const.SUNNYBOY_PV_MANUAL: [
            "/config/library/pv_sma_sunnyboy_manual.yaml",
            "/config/library/generic_pv_dispatch.yaml",
            "/config/library/generic_flexibility.yaml",
        ],
        const.SUNNYBOY_PV_AUTO: [
            "/config/library/pv_sma_sunnyboy.yaml",
            "/config/library/generic_pv_dispatch.yaml",
            "/config/library/generic_flexibility.yaml",
        ],
        const.SHELLY_HEATER: ["/config/library/heater_shelly.yaml"],
        const.SHELLY_METER: ["/config/library/meter_shelly.yaml"],
    }

    for path in src_paths[device]:
        shutil.copy(path, dest_path)


def append_secret(user_input: dict):
    """Append inputted secret to secrets.yaml."""
    if "add_another" in user_input:
        secrets = user_input.copy()
        del secrets["add_another"]
    with open("/config/.storage/packages/secrets.yaml", "a", encoding="utf-8") as file:
        document = yaml.dump(secrets, file)


def find_and_replace_shelly(filename: str, shelly_id: str):
    """Replace instances of {SHELLY_ID} in the package."""
    with open(filename, "r", encoding="utf-8") as file:
        filedata = file.read()

    filedata = filedata.replace("{SHELLY_ID}", shelly_id)

    with open(filename, "w", encoding="utf-8") as file:
        file.write(filedata)
