import openhasp as hasp

plate = hasp.plates.get("theaterplate")

# page three - Gaming
plate.page(layout=hasp.GridLayout(32, 20), title="Page 3 - Gaming")
plate.set_font("32", "#FFFFFF")
plate.add(hasp.Label(text="Gaming PC", align="left"), c=5, r=0.5, w=28, h=4)

# now playing view
np_container = plate.add(
    hasp.Object(hidden=False).styles.set(
        border_width=0, border_opa=0, bg_opa=0, outline_opa=0, shadow_opa=0
    ),
    c=5,
    r=3,
    w=26,
    h=16.5,
)
plate.set_font(28, "#FFFFFF")
np_label = plate.add(
    hasp.Label(align="left", parentid=np_container.id, mode="dots"),
    c=0,
    r=0.25,
    w=26,
    h=2,
)
np_label.hass.inherit_value_from_template(
    "text",
    "{{ " + "state_attr('sensor.steam_76561198858658876', 'game') or 'Idle' " + " }}",
)

np_image = plate.add(
    hasp.Image(parentid=np_container.id, src="L:/now-playing.png"), c=0, r=2, w=26, h=14
)

plate.add_automation(
    hasp.automation.SteamArtworkAutomation(
        "sensor.steam_76561198858658876",
        np_image,
        np_container,
        width=624,
        height=350,
        resizer_url="http://192.168.7.20:5020/image/resize_padded",
    )
)
