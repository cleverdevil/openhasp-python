"""
Theater Plate: Page 0 - Home Controls
=====================================

Home control overlay for page zero. Creates a global toggle button in the bottom right
of the panel and an overlay containing home automation controls that can be toggled
on and off using the toggle button.
"""

import json

import openhasp as hasp

plate = hasp.plates.get("theaterplate")

# toggle button
home_control_toggle = plate.add(
    hasp.Button(text="\uf671", toggle=True).styles.use_profile("floating-button"),
    c=28.5,
    r=16,
    w=3,
    h=3,
)

# overlay panel
home_control_panel = plate.add(
    hasp.Object(hidden=True).styles.use_profile("floating-panel"),
    c=5,
    r=1,
    w=22,
    h=18,
)

# when the toggle button is tapped, toggle an input_boolean helper in Home Assistant
home_control_toggle.hass.on_down(
    "input_boolean.toggle", "input_boolean.theater_plate_home_control_panel_open", {}
)

# set the toggle state of the toggle button to match the state of our helper
home_control_toggle.hass.inherit_value_from_template(
    "val",
    "{{ int(states.input_button.theater_plate_home_control_panel_open == 'on') }}",
)


# automation to display the home control panel when the helper is toggled on
def home_control_panel_automation(name, from_state, to_state, panel_hidden):
    return hasp.automation.OpenHASPConfigAutomation(
        title=f"Theater Plate - Home Control Panel - {name}",
        identifier=f"theater_plate_toggle_home_control_panel_{name}",
        trigger={
            "platform": "state",
            "entity_id": ["input_boolean.theater_plate_home_control_panel_open"],
            "from": from_state,
            "to": to_state,
        },
        action={
            "service": "openhasp.command",
            "target": {"entity_id": "openhasp.theaterplate"},
            "data": {
                "keyword": "jsonl",
                "parameters": json.dumps(
                    {"id": home_control_panel.id, "page": 0, "hidden": panel_hidden}
                ),
            },
        },
    )


plate.add_automation(home_control_panel_automation("OFF", "on", "off", True))
plate.add_automation(home_control_panel_automation("ON", "off", "on", False))

# lighting controls
plate.set_font("30", "#FFFFFF")
plate.add(
    hasp.Label(text="Lighting", mode="expand", parentid=home_control_panel.id),
    c=0.5,
    r=0.5,
    w=22,
    h=1,
)

plate.set_font("md_24", "#FFFFFF")
lighting_buttons = plate.add(
    hasp.ButtonMatrix(
        parentid=home_control_panel.id,
        options=[
            # main lights
            "\ue5c5",
            "\ue42e",
            "\ue5c7",
            "\n",
            # fan lights
            "\ue5c5",
            "\uf168",
            "\ue5c7",
            "\n",
            # stair lights
            "\ue5c5",
            "\uf46c",
            "\ue5c7",
        ],
        pad_top=0,
        pad_bottom=0,
        pad_left=0,
        pad_right=0,
    ).styles.use_profile("control-matrix"),
    c=0.5,
    r=2.5,
    w=10,
    h=9,
)

plate.add_automation(
    hasp.automation.ButtonMatrixAutomation(
        "Theater Plate Lighting Controls",
        f"p{lighting_buttons.page}b{lighting_buttons.id}",
        [
            # main lights
            (
                "light.turn_on",
                "light.home_theater_main_lights",
                {"brightness_step": -10},
            ),
            ("light.toggle", "light.home_theater_main_lights", {}),
            (
                "light.turn_on",
                "light.home_theater_main_lights",
                {"brightness_step": 10},
            ),
            # fan light
            ("light.turn_on", "light.ceiling_fan", {"brightness_step": -10}),
            ("light.toggle", "light.ceiling_fan", {}),
            ("light.turn_on", "light.ceiling_fan", {"brightness_step": 10}),
            # stair lights
            ("light.turn_on", "light.stairs_main_lights", {"brightness_step": -10}),
            ("light.toggle", "light.stairs_main_lights", {}),
            ("light.turn_on", "light.stairs_main_lights", {"brightness_step": 10}),
        ],
    )
)

# fan controls
plate.set_font("30", "#FFFFFF")
plate.add(
    hasp.Label(text="Ceiling Fan", mode="expand", parentid=home_control_panel.id),
    c=0.5,
    r=12,
    w=22,
    h=1,
)

plate.set_font("md_24", "#FFFFFF")
fan_buttons = plate.add(
    hasp.ButtonMatrix(
        parentid=home_control_panel.id,
        options=[
            "\ue5c5",
            "\uf168",
            "\ue5c7",
        ],
        pad_top=0,
        pad_bottom=0,
        pad_left=0,
        pad_right=0,
    ).styles.use_profile("control-matrix"),
    c=0.5,
    r=14,
    w=10,
    h=3,
)

plate.add_automation(
    hasp.automation.ButtonMatrixAutomation(
        "Theater Plate Fan Controls",
        f"p{fan_buttons.page}b{fan_buttons.id}",
        [
            ("fan.decrease_speed", "fan.ceiling_fan"),
            ("fan.toggle", "fan.ceiling_fan"),
            ("fan.increase_speed", "fan.ceiling_fan"),
        ],
    )
)

# scene controls
plate.set_font("30", "#FFFFFF")
plate.add(
    hasp.Label(text="Scenes", mode="expand", parentid=home_control_panel.id),
    c=11.5,
    r=0.5,
    w=8,
    h=1,
)
plate.set_font("24", "#FFFFFF")
scene_buttons = plate.add(
    hasp.ButtonMatrix(
        parentid=home_control_panel.id,
        options=["\uE335 All Off", "\uE6E8 All On"],
        pad_top=0,
        pad_bottom=0,
        pad_left=0,
        pad_right=0,
    ).styles.use_profile("control-matrix"),
    c=11.5,
    r=2.5,
    w=10,
    h=3,
)

plate.add_automation(
    hasp.automation.ButtonMatrixAutomation(
        "Theater Plate 'Scene' Controls",
        f"p{scene_buttons.page}b{scene_buttons.id}",
        [
            (
                "light.turn_off",
                (
                    "light.ceiling_fan",
                    "light.stairs_main_lights",
                    "light.home_theater_main_lights",
                ),
            ),
            (
                "light.turn_on",
                (
                    "light.ceiling_fan",
                    "light.stairs_main_lights",
                    "light.home_theater_main_lights",
                ),
            ),
        ],
    )
)


# magic poster controls
plate.set_font("30", "#FFFFFF")
plate.add(
    hasp.Label(text="Magic Poster", mode="expand", parentid=home_control_panel.id),
    c=11.5,
    r=6,
    w=10,
    h=1,
)
plate.set_font("md_24", "#FFFFFF")
poster_buttons = plate.add(
    hasp.ButtonMatrix(
        parentid=home_control_panel.id,
        options=[
            "\uf45a",  # single poster
            "\ueb85",  # marquee
            "\n",
            "\ue8d7",  # slider
            "\ue9b0",  # flip
            "\n",
            "\ue154",  # next poster,
            "\ue8ac",  # power
        ],
        pad_top=0,
        pad_bottom=0,
        pad_left=0,
        pad_right=0,
    ).styles.use_profile("control-matrix"),
    c=11.5,
    r=8,
    w=10,
    h=9,
)

plate.add_automation(
    hasp.automation.ButtonMatrixAutomation(
        "Theater Plate Magic Poster Controls",
        f"p{poster_buttons.page}b{poster_buttons.id}",
        [
            ("rest_command.arthouse_switch_wall",),
            ("rest_command.arthouse_switch_marquee",),
            ("rest_command.arthouse_switch_slider",),
            ("rest_command.arthouse_switch_flipper",),
            ("rest_command.arthouse_switch_wall_advance",),
            (
                "switch.toggle",
                "switch.magic_poster_switch",
            ),
        ],
    )
)
