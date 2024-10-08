import json

import openhasp as hasp
import openhasp.themes as themes

# plate initialization
plate = hasp.Plate(name="frontplate", w=240, h=320)
plate.set_theme(themes.Dracula())
plate.page(layout=hasp.GridLayout(12, 16), title="Page Zero")
plate.page(layout=hasp.GridLayout(12, 16), title="Page One")
plate.set_font("md_24", "#FFFFFF")
tabs = hasp.TabView(btn_pos=hasp.TabButtonPosition.TOP, val=1)
plate.add(tabs, c=0, r=0)

# home tab
plate.set_font("md_24", "#FFFFFF")
tab = hasp.Tab(text=hasp.icons.get("house"), parentid=tabs.id)
plate.add(tab, c=0, r=0)

# main lights
plate.set_font(16, "#FFFFFF")
plate.add(hasp.Label(text="Main Lights", parentid=tab.id), c=0.5, r=0.25, w=5, h=1.5)

plate.set_font("md_24", "#FFFFFF")
main_light_controls = hasp.ButtonMatrix(
    options=[
        "\ue5db",  # dining - minus (turn down)
        "\uE56C",  # dining - food (toggle)
        "\ue5d8",  # dining - plus (turn up)
        "\n",
        "\ue5db",  # path - minus (turn down)
        "\uf87d",  # path - feet (toggle)
        "\ue5d8",  # path - plus (turn up)
        "\n",
        "\ue5db",  # bar - minus (turn down)
        "\ue540",  # bar - cocktail (toggle)
        "\ue5d8",  # bar - plus (turn up)
    ],
    parentid=tab.id,
    align="center",
)
plate.add(main_light_controls, c=0.5, r=1.5, w=7.25, h=5.25)
main_light_controls.styles.use_profile("small-control-matrix")

plate.add_automation(
    hasp.automation.ButtonMatrixAutomation(
        "Front Room Main Lights",
        f"p{main_light_controls.page}b{main_light_controls.id}",
        [
            (
                "light.turn_on",
                "light.living_room_dining_table_lights",
                {"brightness_step": -10},
            ),
            ("light.toggle", "light.living_room_dining_table_lights", {}),
            (
                "light.turn_on",
                "light.living_room_dining_table_lights",
                {"brightness_step": 10},
            ),
            ("light.turn_on", "light.kitchen_main_lights", {"brightness_step": -10}),
            ("light.toggle", "light.kitchen_main_lights", {}),
            ("light.turn_on", "light.kitchen_main_lights", {"brightness_step": 10}),
            ("light.turn_on", "light.kitchen_island_lights", {"brightness_step": -10}),
            ("light.toggle", "light.kitchen_island_lights", {}),
            ("light.turn_on", "light.kitchen_island_lights", {"brightness_step": 10}),
        ],
    )
)

# lamps
plate.set_font(16, "#FFFFFF")
plate.add(hasp.Label(text="Lamps", parentid=tab.id), c=8, r=0.25, w=3.5, h=2)

color_panel = plate.add(
    hasp.Object(hidden=True).styles.use_profile("floating-panel"),
    c=1,
    r=1,
    w=10,
    h=12.75,
)

color_panel_close = plate.add(
    hasp.Button(parentid=color_panel.id, text="Close", toggle=True),
    c=1,
    r=10,
    w=8,
    h=2,
)
color_panel_close.hass.on_down(
    "input_boolean.toggle", "input_boolean.front_plate_color_panel_open", {}
)

color_panel_close.hass.inherit_value_from_template(
    "val", "{{ int(states.input_button.front_plate_color_panel_open == 'on') }}"
)

color_picker = plate.add(hasp.ColorPicker(parentid=color_panel.id), c=1, r=1, w=8, h=8)
color_picker.hass.inherit_value_from_template(
    "color",
    (
        "{{"
        + "    '#%02x%02x%02x' | format("
        + "        state_attr('light.floor_lamp_left', 'rgb_color')[0],"
        + "        state_attr('light.floor_lamp_left', 'rgb_color')[1],"
        + "        state_attr('light.floor_lamp_left', 'rgb_color')[2]"
        + "    )"
        + "}}"
    ),
)

color_picker.hass.on_change(
    "light.turn_on",
    ("light.floor_lamp_left", "light.floor_lamp_right"),
    {"rgb_color": "".join(("[", "{{ r }},", "{{ g }},", "{{ b }}]"))},
)
color_picker.hass.on_up(
    "light.turn_on",
    ("light.floor_lamp_left", "light.floor_lamp_right"),
    {"rgb_color": "".join(("[", "{{ r }},", "{{ g }},", "{{ b }}"))},
)


def color_panel_automation(name, from_state, to_state, panel_hidden):
    return hasp.automation.OpenHASPConfigAutomation(
        title=f"Front Plate - Lamp Color Picker Panel_{name}",
        identifier=f"front_plate_toggle_color_panel_{name}",
        trigger={
            "platform": "state",
            "entity_id": ["input_boolean.front_plate_color_panel_open"],
            "from": from_state,
            "to": to_state,
        },
        action={
            "service": "openhasp.command",
            "target": {"entity_id": "openhasp.frontplate"},
            "data": {
                "keyword": "jsonl",
                "parameters": json.dumps(
                    {"id": color_panel.id, "page": 1, "hidden": panel_hidden}
                ),
            },
        },
    )


plate.add_automation(color_panel_automation("OFF", "on", "off", True))
plate.add_automation(color_panel_automation("ON", "off", "on", False))

plate.set_font("md_24", "#FFFFFF")
lamps_controls = hasp.ButtonMatrix(
    options=[
        "\ue8ac",  # power (toggle)
        "\n",
        "\ue5db",  # down (turn down)
        "\ue5d8",  # up (turn up)
        "\n",
        "\ue40a",  # palette (color picker)
    ],
    parentid=tab.id,
    align="center",
)
lamps_controls.styles.use_profile("small-control-matrix")
plate.add(lamps_controls, c=8, r=1.5, w=3.5, h=5.25)
plate.add_automation(
    hasp.automation.ButtonMatrixAutomation(
        "Front Room Lamps",
        f"p{lamps_controls.page}b{lamps_controls.id}",
        [
            ("light.toggle", ("light.floor_lamp_left", "light.floor_lamp_right"), {}),
            (
                "light.turn_on",
                ("light.floor_lamp_left", "light.floor_lamp_right"),
                {"brightness_step": -10},
            ),
            (
                "light.turn_on",
                ("light.floor_lamp_left", "light.floor_lamp_right"),
                {"brightness_step": 10},
            ),
            ("input_boolean.toggle", "input_boolean.front_plate_color_panel_open", {}),
        ],
    )
)

# cabinets
plate.set_font(16, "#FFFFFF")
plate.add(
    hasp.Label(text="Cabinet", parentid=tab.id).styles.set(
        bg_color=hasp.styling.color("#FFFFFF")
    ),
    c=0.5,
    r=7.5,
    w=5,
    h=1.4,
)
cabinets = plate.add(
    hasp.Switch(parentid=tab.id)
    .styles.set(bg_color=hasp.styling.color("#ffffff"))
    .styles.set(
        part=hasp.styling.ObjectStylePart.KNOB, bg_color=hasp.styling.color("#1DA3EC")
    ),
    c=3.5,
    r=7.6,
    w=4.0,
    h=0.9,
)
cabinets.hass.inherit_value_from_template(
    "val", "{{ int(states.switch.kitchen_cabinet_lights.state == 'on') }}"
)
cabinets.hass.on_down("switch.toggle", "switch.kitchen_cabinet_lights", {})

# outside
plate.add(
    hasp.Label(text="Outside", parentid=tab.id).styles.set(
        bg_color=hasp.styling.color("#FFFFFF")
    ),
    c=0.5,
    r=9.0,
    w=5,
    h=1.5,
)
outside = plate.add(
    hasp.Switch(parentid=tab.id, groupid=1)
    .styles.set(bg_color=hasp.styling.color("#ffffff"))
    .styles.set(
        part=hasp.styling.ObjectStylePart.KNOB, bg_color=hasp.styling.color("#1DA3EC")
    ),
    c=3.5,
    r=9.1,
    w=4.0,
    h=1,
)

# front door lock
plate.set_font("md_24", "#FFFFFF")
lock = plate.add(
    hasp.Button(parentid=tab.id, text="\uE897", align="center"),
    c=8,
    r=7.6,
    w=3.5,
    h=2.5,
).styles.set(radius=5)
lock.hass.inherit_value_from_template(
    "text",
    "{{ '\uE898' if states.lock.front_door_lock.state == 'unlocked' else '\uE897' }}",
)
lock.hass.on_down("lock.lock", "lock.front_door_lock", {})

# blinds
plate.set_font("md_24", "#FFFFFF")

dining_blinds = hasp.ButtonMatrix(
    options=[
        "\uf72a",  # blinds - close
        "\ueac6",  # blinds - midpoint
        "\uf733",  # blinds - open
    ],
    parentid=tab.id,
    align="center",
).styles.use_profile("small-control-matrix")
plate.add(dining_blinds, c=0.5, r=11, w=5.25, h=1.66)

plate.add_automation(
    hasp.automation.ButtonMatrixAutomation(
        "Front Room Blind Controls - Dining",
        f"p{dining_blinds.page}b{dining_blinds.id}",
        [
            ("cover.close_cover", "cover.dining_room_blind_cover", {}),
            (
                "cover.set_cover_position",
                "cover.dining_room_blind_cover",
                {"position": 50},
            ),
            ("cover.open_cover", "cover.dining_room_blind_cover", {}),
        ],
    )
)

front_blinds = hasp.ButtonMatrix(
    options=[
        "\uf72a",  # blinds - close
        "\ue991",  # blinds - midpoint
        "\uf733",  # blinds - open
    ],
    parentid=tab.id,
    align="center",
).styles.use_profile("small-control-matrix")
plate.add(front_blinds, c=6.25, r=11, w=5.25, h=1.66)

plate.add_automation(
    hasp.automation.ButtonMatrixAutomation(
        "Front Room Blind Controls - Front",
        f"p{front_blinds.page}b{front_blinds.id}",
        [
            (
                "cover.close_cover",
                "cover.living_room_blind_window_covering",
                {},
            ),
            (
                "cover.set_cover_position",
                "cover.living_room_blind_window_covering",
                {"position": 50},
            ),
            (
                "cover.open_cover",
                "cover.living_room_blind_window_covering",
                {},
            ),
        ],
    )
)


# climate tab
plate.set_font("md_24", "#FFFFFF")
tab = hasp.Tab(text="\ueb3b", parentid=tabs.id)
plate.add(tab, c=0, r=0)

plate.set_font(16, "#D6763D")
plate.add(
    hasp.Label(parentid=tab.id, text="CURRENT", align="center"),
    r=0.5,
    c=0,
    w=8,
    h=1,
)

temp_arc = plate.add(
    hasp.Arc(
        parentid=tab.id, type=0, min=50, max=100, val=75, start_angle=180, end_angle=0
    ).styles.set(
        bg_opa=0,
        border_side=0,
        line_color=hasp.styling.color("#ffffff"),
    ),
    w=8,
    h=8,
    r=1.5,
    c=0,
)
temp_arc.hass.inherit_value_from("val", "climate.front_room", "current_temperature")

plate.set_font(30, "#FFFFFF")
temp = plate.add(
    hasp.Label(parentid=tab.id, text="78 °F", align="center"), r=4.25, c=0, w=8, h=3
)
temp.hass.inherit_value_from(
    "text", "climate.front_room", "current_temperature", after="°F"
)

plate.set_font(16, "#D6763D")
plate.add(
    hasp.Label(parentid=tab.id, text="TARGET", align="center"),
    r=0.5,
    c=8.5,
    w=3,
    h=1,
)

plate.set_font(16, "#FFFFFF")
temp_range = [f"{x} °F" for x in range(60, 81)]
target_roller = plate.add(
    hasp.Roller(options=temp_range, rows=2, val=10, parentid=tab.id),
    r=1.95,
    c=8.5,
    w=3,
    h=1,
)

template = (
    "[60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, "
    + "78, 79, 80][int(val)]"
)
target_roller.hass.on_change(
    "climate.set_temperature",
    "climate.front_room",
    {"temperature": "{{ " + template + " }}"},
)

template = (
    "{{ "
    + "[60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74,"
    + "75, 76, 77, 78, 79, 80].index(state_attr('climate.front_room'"
    + ", 'temperature')) }}"
)
target_roller.hass.inherit_value_from_template("val", template)

plate.set_font("md_24", "#FFFFFF")
hvac_mode = plate.add(
    hasp.ButtonMatrix(
        parentid=tab.id,
        options=["\ue8ac", "\uf16a", "\uf166", "\uf557"],  # off, heat, cool, auto
        toggle=True,
        one_check=True,
        val=0,
    ),
    r=7,
    c=0.5,
    w=11,
    h=2.5,
)
plate.add_automation(
    hasp.automation.ButtonMatrixAutomation(
        "Front Plate Air Con State Controls",
        f"p{hvac_mode.page}b{hvac_mode.id}",
        [
            ("climate.toggle", "climate.front_room", {}),
            ("climate.set_hvac_mode", "climate.front_room", {"hvac_mode": "heat"}),
            ("climate.set_hvac_mode", "climate.front_room", {"hvac_mode": "cool"}),
            ("climate.set_hvac_mode", "climate.front_room", {"hvac_mode": "auto"}),
        ],
    )
)

oscillation_mode = plate.add(
    hasp.ButtonMatrix(
        parentid=tab.id,
        options=[
            "\ue5c9",  # no oscillation
            "\ue8d5",  # vertical
            "\ue8d4",  # horizontal
            "\uf854",  # 3D
        ],
        toggle=True,
        one_check=True,
        val=0,
    ),
    r=10,
    c=0.5,
    w=11,
    h=2.5,
)
plate.add_automation(
    hasp.automation.ButtonMatrixAutomation(
        "Front Plate Air Con Oscillation Controls",
        f"p{oscillation_mode.page}b{oscillation_mode.id}",
        [
            ("climate.set_swing_mode", "climate.front_room", {"swing_mode": "Off"}),
            (
                "climate.set_swing_mode",
                "climate.front_room",
                {"swing_mode": "Vertical"},
            ),
            (
                "climate.set_swing_mode",
                "climate.front_room",
                {"swing_mode": "Horizontal"},
            ),
            ("climate.set_swing_mode", "climate.front_room", {"swing_mode": "3D"}),
        ],
    )
)

# scenes tab
plate.set_font("md_24", "#FFFFFF")
tab = hasp.Tab(text="\uE743", parentid=tabs.id)
plate.add(tab, c=0, r=0)

plate.set_font(18, "#FFFFFF")
plate.add(hasp.Label(text="Scenes", parentid=tab.id), c=0.5, r=0.5, w=11, h=1.5)

plate.set_font("md_48", "#FFFFFF")

scenes = hasp.ButtonMatrix(
    options=[
        "\uE88A",  # we're home
        "\uF150",  # we're away,
        "\n",
        "\uE91D",  # doggy duty
        "\uE2E6",  # doggies done,
        "\n",
        "\uF1F1",  # goodnight
    ],
    parentid=tab.id,
    align="center",
)
plate.add(scenes, c=0.5, r=1.75, w=11, h=10.5)
plate.add_automation(
    hasp.automation.ButtonMatrixAutomation(
        "Front Plate Scene Controls",
        f"p{scenes.page}b{scenes.id}",
        [
            ("scene.turn_on", "scene.we_re_home", {}),
            ("scene.turn_on", "scene.we_re_away", {}),
            ("scene.turn_on", "scene.doggy_duty", {}),
            ("scene.turn_on", "scene.doggies_done", {}),
            ("scene.turn_on", "scene.good_night", {}),
        ],
    )
)
