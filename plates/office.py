import openhasp as hasp
import openhasp.themes as themes

# plate initialization
plate = hasp.Plate(name="officeplate", w=240, h=320)
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

# ceiling fan
plate.set_font(18, "#FFFFFF")
plate.add(hasp.Label(text="Ceiling Fan", parentid=tab.id), c=0.5, r=0.25, w=6, h=2)

plate.set_font("24", "#FFFFFF")
fan_controls = hasp.ButtonMatrix(
    options=[
        "\uE374",  # fan light - minus (turn down)
        "\uE6E8",  # fan light - bulb (toggle)
        "\uE415",  # fan light - plus (turn up)
        "\n",
        "\uE374",  # fan speed - minus (turn down)
        "\uE210",  # fan speed - fan (toggle)
        "\uE415",  # fan speed - plus (turn up)
    ],
    parentid=tab.id,
    align="center",
)
plate.add(fan_controls, c=0.5, r=1.5, w=6, h=5)
plate.add_automation(
    hasp.automation.ButtonMatrixAutomation(
        "Office Plate Fan Controls",
        f"p{fan_controls.page}b{fan_controls.id}",
        [
            ("light.turn_on", "light.ceiling_fan_light", {"brightness_step": -10}),
            ("light.toggle", "light.ceiling_fan_light", {}),
            ("light.turn_on", "light.ceiling_fan_light", {"brightness_step": 10}),
            ("fan.decrease_speed", "fan.office_ceiling_fan", {}),
            ("fan.toggle", "fan.office_ceiling_fan", {}),
            ("fan.increase_speed", "fan.office_ceiling_fan", {}),
        ],
    )
)

# lamp
plate.set_font(18, "#FFFFFF")
plate.add(
    hasp.Label(text="Lamp", parentid=tab.id).styles.set(
        bg_color=hasp.styling.color("#FFFFFF")
    ),
    c=7,
    r=0.25,
    w=4.5,
    h=2,
)
lamp = plate.add(
    hasp.Switch(parentid=tab.id)
    .styles.set(bg_color=hasp.styling.color("#ffffff"))
    .styles.set(
        part=hasp.styling.ObjectStylePart.KNOB, bg_color=hasp.styling.color("#1DA3EC")
    ),
    c=7,
    r=1.5,
    w=4.5,
    h=1,
)
lamp.hass.inherit_value_from_template(
    "val", "{{ int(states.switch.office_lamp.state == 'on') }}"
)
lamp.hass.on_down("switch.toggle", "switch.office_lamp", {})

# blinds
plate.add(hasp.Label(text="Blinds", parentid=tab.id), c=7, r=3, w=4.5, h=2)
blind_controls = hasp.ButtonMatrix(
    options=[
        "\uF11C",  # blinds - close
        "\uF11E",  # blinds - open
    ],
    parentid=tab.id,
    align="center",
)
plate.add(blind_controls, c=7, r=4.25, w=4.5, h=2.25)
plate.add_automation(
    hasp.automation.ButtonMatrixAutomation(
        "Office Plate Blind Controls",
        f"p{blind_controls.page}b{blind_controls.id}",
        [
            ("cover.close_cover", "cover.office_blinds_cover", {}),
            ("cover.open_cover", "cover.office_blinds_cover", {}),
        ],
    )
)

# scenes
plate.add(hasp.Label(text="Scenes", parentid=tab.id), c=0.5, r=7, w=11, h=2)
plate.set_font("md_48", "#FFFFFF")
scenes = hasp.ButtonMatrix(
    options=[
        hasp.icons.get("laptop_mac"),
        hasp.icons.get("home"),
        hasp.icons.get("bed"),
    ],
    parentid=tab.id,
    align="center",
)
plate.add(scenes, c=0.5, r=8.25, w=11, h=4)
plate.add_automation(
    hasp.automation.ButtonMatrixAutomation(
        "Office Plate Scene Controls",
        f"p{scenes.page}b{scenes.id}",
        [
            ("scene.turn_on", "scene.office_work", {}),
            ("scene.turn_on", "scene.office_home", {}),
            ("scene.turn_on", "scene.office_sleep", {}),
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
temp_arc.hass.inherit_value_from("val", "climate.office", "current_temperature")


plate.set_font(30, "#FFFFFF")
temp = plate.add(
    hasp.Label(parentid=tab.id, text="78 °F", align="center"), r=4.25, c=0, w=8, h=3
)
temp.hass.inherit_value_from(
    "text", "climate.office", "current_temperature", after="°F"
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

template = "".join(
    (
        "[60, 61, 62, 63, 64, 65, 66, 67, 68, 69,",
        "70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80][int(val)]",
    )
)
target_roller.hass.on_change(
    "climate.set_temperature",
    "climate.office",
    {"temperature": "{{ " + template + " }}"},
)

template = "".join(
    (
        "{{ ",
        "[60, 61, 62, 63, 64, 65, 66, 67, 68, 69,",
        " 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80",
        "].index(state_attr('climate.office', 'temperature'))",
        "}}",
    )
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
        "Office Plate Air Con State Controls",
        f"p{hvac_mode.page}b{hvac_mode.id}",
        [
            ("climate.toggle", "climate.office", {}),
            ("climate.set_hvac_mode", "climate.office", {"hvac_mode": "heat"}),
            ("climate.set_hvac_mode", "climate.office", {"hvac_mode": "cool"}),
            ("climate.set_hvac_mode", "climate.office", {"hvac_mode": "auto"}),
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
        "Office Plate Air Con Oscillation Controls",
        f"p{oscillation_mode.page}b{oscillation_mode.id}",
        [
            ("climate.set_swing_mode", "climate.office", {"swing_mode": "Off"}),
            ("climate.set_swing_mode", "climate.office", {"swing_mode": "Vertical"}),
            ("climate.set_swing_mode", "climate.office", {"swing_mode": "Horizontal"}),
            ("climate.set_swing_mode", "climate.office", {"swing_mode": "3D"}),
        ],
    )
)
