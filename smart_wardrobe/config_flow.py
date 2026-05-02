import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector
from .const import DOMAIN, CONF_CALENDAR, CONF_GARMENTS, CONF_NOTIFY_DEVICE, ATTR_CATEGORY, ATTR_MAX_WEARS

class WardrobeOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            options = dict(self._config_entry.options)
            garments = list(options.get(CONF_GARMENTS, []))
            garments.append({
                "name": user_input["name"],
                ATTR_CATEGORY: user_input[ATTR_CATEGORY],
                ATTR_MAX_WEARS: user_input[ATTR_MAX_WEARS]
            })
            options[CONF_GARMENTS] = garments
            return self.async_create_entry(title="", data=options)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required("name"): str,
                vol.Required(ATTR_CATEGORY): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=["Gym", "Wedding", "Office", "Casual", "Date Night"],
                        mode=selector.SelectSelectorMode.DROPDOWN
                    )
                ),
                vol.Required(ATTR_MAX_WEARS, default=1): int,
            })
        )

class WardrobeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="Smart Wardrobe", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_CALENDAR): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="calendar")
                ),
                vol.Optional(CONF_NOTIFY_DEVICE): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="notify")
                ),
            })
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return WardrobeOptionsFlowHandler(config_entry)