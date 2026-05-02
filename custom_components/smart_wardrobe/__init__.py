import asyncio
import logging
import voluptuous as vol
from datetime import datetime, timedelta
from homeassistant.helpers import config_validation as cv
from .const import DOMAIN, CONF_CALENDAR, CONF_NOTIFY_DEVICE, STATE_DIRTY

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["sensor"]

SERVICE_SET_STATE = "set_garment_state"
SET_STATE_SCHEMA = vol.Schema({
    vol.Required("entity_id"): cv.entity_id,
    vol.Required("state"): vol.In(["Clean", "Worn", "Dirty", "Washing"]),
})

async def async_setup_entry(hass, entry):
    """Set up Smart Wardrobe and register services."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {"entities": {}}
    
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    async def handle_set_state(call):
        entity_id = call.data.get("entity_id")
        new_state = call.data.get("state")
        for entry_id in hass.data[DOMAIN]:
            entities = hass.data[DOMAIN][entry_id].get("entities", {})
            if entity_id in entities:
                await entities[entity_id].async_update_state(new_state)
                return

    hass.services.async_register(DOMAIN, SERVICE_SET_STATE, handle_set_state, schema=SET_STATE_SCHEMA)
    entry.async_on_unload(entry.add_update_listener(update_listener))
    entry.async_create_background_task(hass, style_engine_loop(hass, entry), "wardrobe_engine")
    return True

async def style_engine_loop(hass, entry):
    """Wait for HA to start, then monitor schedule hourly."""
    await asyncio.sleep(15) 
    while True:
        try:
            await check_wardrobe_readiness(hass, entry)
        except Exception as err:
            _LOGGER.error("Style Engine loop error: %s", err)
        await asyncio.sleep(3600)

async def check_wardrobe_readiness(hass, entry):
    """Fetch calendar events and analyze availability."""
    calendar_id = entry.data.get(CONF_CALENDAR)
    if not calendar_id or not hass.states.get(calendar_id):
        return

    start_time = datetime.now()
    end_time = start_time + timedelta(days=1)

    try:
        response = await hass.services.async_call(
            "calendar", "get_events",
            {"entity_id": calendar_id, "start_date_time": start_time.isoformat(), "end_date_time": end_time.isoformat()},
            blocking=True, return_response=True,
        )
        events = response.get(calendar_id, {}).get("events", [])
        for event in events:
            summary = event.get("summary", "").lower()
            cat = None
            if "wedding" in summary: cat = "Wedding"
            elif "gym" in summary or "workout" in summary: cat = "Gym"
            elif "office" in summary: cat = "Office"
            
            if cat:
                await analyze_availability(hass, entry, cat, summary)
    except Exception as e:
        _LOGGER.debug("Calendar check skipped: %s", e)

async def analyze_availability(hass, entry, category, event_name):
    """Fire alert to the selected notification device."""
    all_sensors = hass.states.async_all("sensor")
    clothes = [s for s in all_sensors if s.attributes.get("category") == category and s.attributes.get("integration") == DOMAIN]
    
    if clothes and all(s.state == "Dirty" for s in clothes):
        notify_service = entry.data.get(CONF_NOTIFY_DEVICE)
        title = "Wardrobe Warning"
        msg = f"All {category} clothes are dirty for '{event_name}' tomorrow!"

        if notify_service:
            domain, service = notify_service.split(".")
            await hass.services.async_call(domain, service, {"title": title, "message": msg})
        else:
            await hass.services.async_call("persistent_notification", "create", {
                "title": title, "message": msg, "notification_id": f"wardrobe_{category.lower()}"
            })

async def update_listener(hass, entry):
    await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass, entry):
    hass.data[DOMAIN].pop(entry.entry_id)
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)