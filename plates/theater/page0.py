"""
Theater Plate: Page 0
=====================

Global page containing elements that display on all pages, including navigation
and home control overlay.
"""

import openhasp as hasp

plate = hasp.plates.get("theaterplate")
plate.page(layout=hasp.GridLayout(32, 20), title="Page Zero")

# activity selector
plate.set_font("md_48", "#FFFFFF")
activities = plate.add(
    hasp.ButtonMatrix(
        options=[
            "\ue639",
            "\n",  # Apple TV - TV
            "\ue02c",
            "\n",  # Zidoo Z9X - Movie
            "\uf135",
            "\n",  # Gaming - Controller
            "\ue8ac",  # Power Off - Power
        ],
        align="center",
        toggle=True,
        one_check=True,
        val=3,
    ).styles.use_profile(
        "navigation",
    ),
    c=0,
    r=0,
    w=4,
    h=20,
)

# set the current activity button as active by watching the AVR's source
activities.hass.inherit_value_from_template(
    "val",
    (
        "{{"
        + "{'Apple TV': 0, 'Zidoo Z9X': 1, 'Punk': 2}"
        + ".get(state_attr('media_player.home_theater_receiver', 'source'), 3)"
        + "}}"
    ),
)


def activity_sync(attribute, source, page):
    kw = {}
    kw["title"] = f"Theater Plate - Activity Page Sync - {source}"
    kw["identifier"] = f"theater_plate_activity_page_sync_{page}"
    kw["trigger"] = {
        "platform": "state",
        "entity_id": ["media_player.home_theater_receiver"],
    }
    kw["action"] = {
        "service": "openhasp.command",
        "target": {"entity_id": "openhasp.theaterplate"},
        "data": {"keyword": "page", "parameters": page},
    }

    if attribute:
        kw["trigger"]["attribute"] = attribute

    if source:
        kw["trigger"]["to"] = source
    else:
        kw["trigger"]["to"] = "off"

    plate.add_automation(hasp.automation.OpenHASPConfigAutomation(**kw))


activity_sync("source", "Apple TV", 1)
activity_sync("source", "Zidoo Z9X", 2)
activity_sync("source", "Punk", 3)
activity_sync(None, None, 4)


# when an activity button is tapped, switch the current activity
def activity(page, btn, source):
    return [
        ("openhasp.change_page", "openhasp.theaterplate", {"page": page}),
        (
            "openhasp.command",
            "openhasp.theaterplate",
            {
                "keyword": "jsonl",
                "parameters": {"id": activities.id, "page": 0, "val": btn},
            },
        ),
        (
            f"media_player.turn_{'on' if source is not None else 'off'}",
            "media_player.home_theater_receiver",
        ),
        (
            "media_player.select_source",
            "media_player.home_theater_receiver",
            {"source": source},
        ),
        (
            "light.turn_on",
            (
                "light.home_theater_main_lights",
                "light.stairs_main_lights",
                "light.ceiling_fan",
            ),
            {"transition": 10, "brightness_pct": 0 if source is not None else 100},
        ),
        ("script.projector_power",),
        ("script.projector_power",),
        ("script.projector_power",),
    ]


plate.add_automation(
    hasp.automation.ButtonMatrixAutomation(
        "Theater Plate - Activity Switcher",
        f"p{activities.page}b{activities.id}",
        (
            activity(1, 0, "Apple TV"),
            activity(2, 1, "Zidoo Z9X"),
            activity(3, 2, "Punk"),
            activity(4, 3, None),
        ),
    )
)

from . import page0_homecontrol as _  # noqa
