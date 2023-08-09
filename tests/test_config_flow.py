import pytest
from homeassistant.const import STATE_UNKNOWN
from homeassistant.core import State, HomeAssistant
from homeassistant.setup import setup_component
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers import device_registry as dr

from cofybox_packages.config_flow import (
    _get_shelly_id
)

# TODO: Make this work!
@pytest.mark.skip
@pytest.mark.parametrize("entity_id,expected_shelly_id", [
    ("sensor.shelly_em_A1B2C3_energy", "A1B2C3"),
    ("sensor.shelly_em_D4E5F6_energy", "D4E5F6"),
    ("sensor.non_shelly_em", None),
    (None, None),
])
def test_get_shelly_id(hass: HomeAssistant, entity_id, expected_shelly_id):
    """Test _get_shelly_id method for different entity_id values."""
    # setup_component(hass, "cofybox_packages", {"cofybox_packages": {}})
    # hass.async_block_till_done()

    if entity_id:
        hass.states.set(entity_id, "test_value")

    assert _get_shelly_id(hass, entity_id) == expected_shelly_id
