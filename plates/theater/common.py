import json

import openhasp as hasp

plate = hasp.plates.get("theaterplate")


def remote_control(
    name,
    target_entity_id,
    helper_entity_id,
    button_map,
    service="remote.send_command",
    argument_name="command",
):
    plate.set_font("md_48", "#FFFFFF")
    remote_toggle = plate.add(
        hasp.Button(
            text="\ue83e",
            toggle=True,
        ).styles.use_profile("floating-button"),
        c=28.5,
        r=12.5,
        w=3,
        h=3,
    )
    remote_toggle.hass.inherit_value_from_template(
        "val",
        "{{ " + f"int(states.{helper_entity_id}== 'on')" + " }}",
    )

    remote_panel = plate.add(
        hasp.Object(
            hidden=True,
        ).styles.use_profile("floating-panel"),
        c=5,
        r=1,
        w=22,
        h=18,
    )
    remote_toggle.hass.on_down("input_boolean.toggle", helper_entity_id, {})
    plate.add_automation(
        hasp.automation.OpenHASPConfigAutomation(
            title=f"Theater Plate - {name} Remote Panel ON",
            identifier=f"theater_plate_toggle_{name}_remote_panel_on",
            trigger={
                "platform": "state",
                "entity_id": [helper_entity_id],
                "from": "off",
                "to": "on",
            },
            action={
                "service": "openhasp.command",
                "target": {"entity_id": "openhasp.theaterplate"},
                "data": {
                    "keyword": "jsonl",
                    "parameters": json.dumps(
                        {
                            "id": remote_panel.id,
                            "page": remote_panel.page,
                            "hidden": False,
                        }
                    ),
                },
            },
        )
    )
    plate.add_automation(
        hasp.automation.OpenHASPConfigAutomation(
            title=f"Theater Plate - {name} Remote Panel Off",
            identifier=f"theater_plate_toggle_{name}_remote_panel_off",
            trigger={
                "platform": "state",
                "entity_id": [f"input_boolean.theater_plate_{name}_remote_panel_open"],
                "from": "on",
                "to": "off",
            },
            action={
                "service": "openhasp.command",
                "target": {"entity_id": "openhasp.theaterplate"},
                "data": {
                    "keyword": "jsonl",
                    "parameters": json.dumps(
                        {
                            "id": remote_panel.id,
                            "page": remote_panel.page,
                            "hidden": True,
                        }
                    ),
                },
            },
        )
    )
    plate.set_font("md_48", "#FFFFFF")
    remote_buttons = plate.add(
        hasp.MediaControlsButtonMatrix(
            parentid=remote_panel.id, pad_top=0, pad_bottom=0, pad_left=0, pad_right=0
        ).styles.use_profile("control-matrix"),
        c=1,
        r=1,
        w=20,
        h=16,
    )
    plate.add_automation(
        hasp.automation.MediaPlayerRemoteAutomation(
            f"Theater Plate {name} Remote",
            f"p{remote_buttons.page}b{remote_buttons.id}",
            [
                (
                    "media_player.volume_mute",
                    "media_player.home_theater_receiver",
                    {
                        "is_volume_muted": "{%- if states.media_player.home_theater_receiver.attributes.is_volume_muted -%} false {%- else -%} true {%- endif -%}"
                    },
                ),
                (
                    service,
                    target_entity_id,
                    {argument_name: button_map["info"]},
                ),
                (
                    service,
                    target_entity_id,
                    {argument_name: button_map["up"]},
                ),
                (
                    service,
                    target_entity_id,
                    {argument_name: button_map["home"]},
                ),
                (
                    service,
                    target_entity_id,
                    {argument_name: button_map["info"]},
                ),
                ("media_player.volume_up", "media_player.home_theater_receiver", {}),
                (
                    service,
                    target_entity_id,
                    {argument_name: button_map["left"]},
                ),
                (
                    service,
                    target_entity_id,
                    {argument_name: button_map["select"]},
                ),
                (
                    service,
                    target_entity_id,
                    {argument_name: button_map["right"]},
                ),
                (
                    service,
                    target_entity_id,
                    {argument_name: button_map["skip_back"]},
                ),
                ("media_player.volume_down", "media_player.home_theater_receiver", {}),
                (
                    service,
                    target_entity_id,
                    {argument_name: button_map["back"]},
                ),
                (
                    service,
                    target_entity_id,
                    {argument_name: button_map["down"]},
                ),
                (
                    service,
                    target_entity_id,
                    {argument_name: button_map["menu"]},
                ),
                (
                    service,
                    target_entity_id,
                    {argument_name: button_map["skip_fwd"]},
                ),
            ],
        )
    )
