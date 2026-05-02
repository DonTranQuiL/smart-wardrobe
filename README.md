# 👔 Smart Wardrobe: The Style Engine
**A Proactive Closet Management & Schedule-Aware Integration for Home Assistant**  
Created by **Don TranQUiL**

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Maintained](https://img.shields.io/badge/Maintained%3F-yes-green.svg)
![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2024.5+-blue.svg)

---

## 📖 The Philosophy
Most smart home setups are **reactive**—they turn on lights when you enter a room. **Smart Wardrobe** is **proactive**. It treats your clothing like critical inventory. By linking your physical closet to your digital life, the **Style Engine** ensures you always have the right clothes ready for the right moment. 

Stop checking your hamper every morning; let Home Assistant do the thinking for you.

---

## 📅 The Calendar Connection (The Brains)
The magic of the Smart Wardrobe relies entirely on your Home Assistant calendar. The integration doesn't just know *what* clothes you have; it knows *when* you need them.

**Supported Calendars:** Smart Wardrobe works with ANY calendar integrated into Home Assistant (e.g., Google Calendar, CalDAV, Apple Calendar, or the HA Local Calendar). 

### How the "Style Engine" Reads Your Schedule:
1. **The Hourly Scan:** Every hour, the engine scans your selected calendar entity for any events scheduled in the next 24 hours.
2. **Event Title Mapping:** It looks at the *Summary/Title* of your calendar events and runs them through a keyword filter to determine what kind of day you have ahead:
    *   **Gym:** workout, training, exercise, gym. *(e.g., "Morning Workout" triggers the Gym category)*
    *   **Office:** meeting, work, presentation, office.
    *   **Wedding:** formal, wedding.
    *   **Pyjama:** sleep, bed, pjs, overnight.
    *   **Spicy:** date, anniversary, romance, sexy. *(e.g., "Date Night with Sarah" triggers the Spicy category)*
3. **The "Critical Fail" Alert:** The system checks the wardrobe category required for your upcoming event. If **100%** of the items in that specific category are currently marked as `Dirty`, it fires a notification. This gives you a "heads up" to start a wash cycle *before* you actually need to get dressed.

---

## 🛠 Features & Services

### 📂 Master Category Sensors
Say goodbye to entity clutter. For every custom category you create during setup (e.g., *Spicy*, *Pyjama*, *Office*), the integration automatically generates a **Master Sensor** (e.g., `sensor.office_category_status`). 
*   **State `Ready`:** You have at least one clean option available for this category.
*   **State `Not Ready`:** All items in this category are dirty. Laundry day is no longer optional!

### 💾 Bulletproof Persistence
Powered by `RestoreEntity`, all garment states are saved directly to the Home Assistant database. Your closet status survives server reboots, system updates, and power outages.

### ⚡ The `set_garment_state` Service
This is the heart of the manual control. You can find it under **Developer Tools > Actions**.
*   **Target by Entity:** Update a single specific shirt (e.g., `sensor.smart_wardrobe_blue_suit`).
*   **Target by Category:** Update an **entire group** at once (e.g., set all "Gym" clothes to `Clean`).
*   **States:** Choose between `Clean`, `Worn`, `Dirty`, or `Washing`.

---

## 🚀 Installation & Setup

**Prerequisite:** Ensure you have at least one working Calendar integration (like Google Calendar or HA Local Calendar) set up in Home Assistant.

1.  Download the `smart_wardrobe` folder from this repository.
2.  Place it inside your Home Assistant `custom_components` directory.
3.  Restart Home Assistant.
4.  Go to **Settings > Devices & Services > Add Integration** and search for **Smart Wardrobe**.
5.  **The Config Flow:** 
    *   Select your primary schedule **Calendar** from the dropdown.
    *   (Optional) Select a **Notification Device** (like your mobile phone) to receive alerts. If left blank, alerts will default to the Home Assistant persistent notifications sidebar.
6.  Click "Configure" on the integration card to start adding your individual clothing items and assigning them to categories!

---

## 🤖 Real-World Automations

### 1. The NFC "Hamper" Workflow (Manual Tagging)
Stick an NFC tag inside your laundry hamper. When you drop a specific garment in, tap the tag with your phone to mark it dirty without opening the app:
```yaml
alias: "Wardrobe: Blue Jeans in Hamper"
trigger:
  - platform: tag
    tag_id: your_nfc_tag_id_here
action:
  - service: smart_wardrobe.set_garment_state
    data:
      entity_id: sensor.smart_wardrobe_blue_jeans
      state: Dirty
```

### 2. Automatic "Dirty" State (Post-Event)
Mark your gym clothes as dirty automatically when your calendar workout event ends:
```yaml
alias: "Wardrobe: Mark Gym Dirty"
trigger:
  - platform: calendar
    event: end
    entity_id: calendar.your_schedule
condition:
  - condition: template
    value_template: "{{ 'gym' in trigger.calendar_event.summary.lower() }}"
action:
  - service: smart_wardrobe.set_garment_state
    data:
      category: Gym
      state: Dirty
```

### 3. The "Laundry Day" Bulk Reset
When your smart washing machine finishes a cycle, reset the entire category to clean:
```yaml
alias: "Wardrobe: Laundry Reset"
trigger:
  - platform: state
    entity_id: sensor.washing_machine_status
    from: "Running"
    to: "Finished"
action:
  - service: smart_wardrobe.set_garment_state
    data:
      category: Gym
      state: Clean
```

---

## 🎨 Recommended Dashboard
Use the **Auto-Entities** card (HACS) to create a dynamic "Laundry List" that only appears when items actually need to be washed:
```yaml
type: custom:auto-entities
card:
  type: entities
  title: 🧺 Pending Laundry
filter:
  include:
    - integration: smart_wardrobe
      state: "Dirty"
show_empty: false
```

---

## 🤝 Support & Contribution
Developed and maintained by **Don TranQUiL**  

If this integration saved your morning or helped you look your best for a "Spicy" date night, please consider giving the repo a ⭐!

[GitHub Repository](https://github.com/DonTranQuiL/smart-wardrobe) | [Report a Bug](https://github.com/DonTranQuiL/smart-wardrobe/issues)
