from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.restore_state import RestoreEntity
from .const import DOMAIN, STATE_CLEAN, CONF_GARMENTS, ATTR_CATEGORY, ATTR_MAX_WEARS


async def async_setup_entry(hass, entry, async_add_entities):
    """Setup entities from the config entry."""
    garment_list = entry.options.get(CONF_GARMENTS, [])
    entities = []

    for garment in garment_list:
        entities.append(
            GarmentEntity(
                entry, garment["name"], garment[ATTR_CATEGORY], garment[ATTR_MAX_WEARS]
            )
        )

    entities.append(WardrobeStatusSensor(entry, len(garment_list)))
    async_add_entities(entities)


class GarmentEntity(RestoreEntity, SensorEntity):
    """A garment that remembers its state."""

    def __init__(self, entry, name, category, max_wears):
        self._entry = entry
        self._attr_name = name
        self._attr_unique_id = f"{entry.entry_id}_{name.replace(' ', '_').lower()}"
        self._state = STATE_CLEAN
        self._category = category
        self._max_wears = max_wears

    async def async_added_to_hass(self):
        """Restore state and register for service calls."""
        await super().async_added_to_hass()

        # Register this specific object in the global storage
        self.hass.data[DOMAIN][self._entry.entry_id]["entities"][self.entity_id] = self

        if (old_state := await self.async_get_last_state()) is not None:
            self._state = old_state.state
            self.async_write_ha_state()

    async def async_update_state(self, new_state):
        """Update the internal state so it stays changed."""
        self._state = new_state
        self.async_write_ha_state()

    @property
    def native_value(self):
        return self._state

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": "Smart Wardrobe",
        }

    @property
    def extra_state_attributes(self):
        return {
            ATTR_CATEGORY: self._category,
            "max_wears": self._max_wears,
            "integration": DOMAIN,
        }


class WardrobeStatusSensor(SensorEntity):
    """Total items sensor."""

    def __init__(self, entry, count):
        self._entry = entry
        self._attr_name = "Wardrobe Total Items"
        self._attr_native_value = count
        self._attr_unique_id = f"{entry.entry_id}_total_count"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": "Smart Wardrobe",
        }
