from __future__ import annotations

import random
import typing
from dataclasses import dataclass, field

import yaml

if typing.TYPE_CHECKING:
    from openhasp import Object


def join(*args):
    return "".join(args)


@dataclass
class HASSConfiguration:
    target: "Object" = None
    properties: typing.MutableMapping[str, str] = field(default_factory=dict)
    events: typing.MutableMapping[str, str] = field(default_factory=dict)
    automations: list = field(default_factory=list)

    def on(self, event_name, meta):
        if isinstance(meta["entity_id"], tuple):
            meta["entity_id"] = list(meta["entity_id"])
        self.events.setdefault(event_name, []).append(meta)

    def inherit_value_from(self, prop, entity_id, attribute, before="", after=""):
        self.properties[prop] = (
            before
            + "{{ "
            + f'state_attr("{entity_id}", "{attribute}")'
            + " }}"
            + after
        )

    def inherit_value_from_template(self, prop, template):
        self.properties[prop] = template

    def on_change(self, service, entity_id, data):
        self.on("changed", {"service": service, "entity_id": entity_id, "data": data})

    def on_down(self, service, entity_id, data):
        self.on("down", {"service": service, "entity_id": entity_id, "data": data})

    def on_up(self, service, entity_id, data):
        self.on("up", {"service": service, "entity_id": entity_id, "data": data})

    @property
    def yaml(self):
        yaml = {
            "obj": f"p{self.target.page}b{self.target.id}",
            "properties": self.properties,
        }

        if len(self.events):
            yaml["event"] = self.events

        return yaml


class Scenes:
    def __init__(self):
        self.scenes = []

    def add(self, scene):
        self.scenes.append(scene)

    @property
    def yaml(self):
        return yaml.dump([s.yaml for s in self.scenes], Dumper=yaml.Dumper)


scenes = Scenes()


@dataclass
class Scene:
    id: str = field(default_factory=lambda: f"{random.randint(1000000, 10000000)}")
    states: dict = field(default_factory=dict)
    name: str = "Generated Scene"

    def __post_init__(self):
        scenes.add(self)

    def set(self, entity_id, state, **attributes):
        attributes["state"] = state
        self.states[entity_id] = attributes

    @property
    def entity_id(self):
        return f"scene.{self.id}"

    @property
    def yaml(self):
        y = dict(id=self.id, name=self.name, entities={}, metadata={})

        for entity_id, state in self.states.items():
            y["entities"][entity_id] = state
            y["metadata"][entity_id] = dict(entity_only=True)

        return y


class Automation:
    pass


class OpenHASPConfigAutomation(Automation):
    def __init__(self, title, identifier, trigger, action):
        self.title = title
        self.identifier = identifier
        self.trigger = trigger
        self.action = action

    @property
    def yaml(self):
        automation = {
            "mode": "single",
            "id": f"{self.plate.name}_automation_{self.identifier}",
            "alias": f"{self.title}",
            "trigger": [self.trigger],
            "condition": [],
            "action": [self.action],
        }
        return automation


class ButtonMatrixAutomation(Automation):
    def __init__(self, title, matrix_id, actions):
        self.title = title
        self.matrix_id = matrix_id
        self.actions = actions

    @property
    def yaml(self):
        automations = []
        for button_id, action in enumerate(self.actions):
            actions = action if isinstance(action, list) else [action]

            for count, action in enumerate(actions):
                action = list(action)
                service = action.pop(0)
                entity_id = action.pop(0) if len(action) else None
                data = action.pop(0) if len(action) else None

                automation = {
                    "id": join(
                        f"{self.plate.name}",
                        "_press_",
                        f"{self.matrix_id}-{button_id}-{count}",
                    ),
                    "alias": join(
                        f"{self.plate.name}",
                        "- Button - ",
                        f"{self.title} - ({self.matrix_id}-{button_id}-{count})",
                    ),
                    "trigger": [
                        {
                            "platform": "mqtt",
                            "topic": f"hasp/{self.plate.name}/state/{self.matrix_id}",
                        }
                    ],
                    "condition": [
                        {
                            "condition": "template",
                            "value_template": " ".join(
                                [
                                    "{{",
                                    "trigger.payload_json['event'] == 'up'",
                                    "and",
                                    f"trigger.payload_json['val'] == {button_id}",
                                    "}}",
                                ]
                            ),
                        }
                    ],
                }
                automation["action"] = {"service": service}
                if entity_id:
                    if isinstance(entity_id, tuple):
                        entity_id = list(entity_id)
                    automation["action"]["target"] = {"entity_id": entity_id}

                if data:
                    automation["action"]["data"] = data

                automations.append(automation)
        return automations


class MediaPlayerRemoteAutomation(Automation):
    def __init__(self, title, matrix_id, actions):
        self.title = title
        self.matrix_id = matrix_id
        self.actions = actions

    @property
    def yaml(self):
        automations = []
        for button_id, (service, entity_id, data) in enumerate(self.actions):
            automations.append(
                {
                    "id": join(
                        f"{self.plate.name}",
                        "_remote_press_",
                        f"{self.matrix_id}-{button_id}",
                    ),
                    "alias": join(
                        f"{self.plate.name}",
                        " Remote Press ",
                        f"({self.matrix_id}-{button_id})",
                    ),
                    "trigger": [
                        {
                            "platform": "mqtt",
                            "topic": f"hasp/{self.plate.name}/state/{self.matrix_id}",
                        }
                    ],
                    "condition": [
                        {
                            "condition": "template",
                            "value_template": " ".join(
                                [
                                    "{{",
                                    "trigger.payload_json['event'] == 'up'",
                                    "and",
                                    f"trigger.payload_json['val'] == {button_id}",
                                    "}}",
                                ]
                            ),
                        }
                    ],
                    "action": [
                        {
                            "service": service,
                            "target": {"entity_id": entity_id},
                            "data": data,
                        }
                    ],
                }
            )
        return automations


class ArtworkAutomation(Automation):
    def __init__(
        self,
        title,
        entity_id,
        image,
        container,
        trigger_attribute=None,
        width=480,
        height=480,
        default_image=None,
        resizer_url=None,
    ):

        self.title = title
        self.entity_id = entity_id
        self.image_id = f"p{image.page}b{image.id}"
        self.container_id = f"p{container.page}b{container.id}"
        self.trigger_attribute = trigger_attribute
        self.width = width
        self.height = height
        self.default_image = default_image
        self.resizer_url = resizer_url

    @property
    def _prefix(self):
        return f"{self.resizer_url}?width={self.width}&height={self.height}&url="

    @property
    def _url(self):
        raise NotImplementedError

    @property
    def yaml(self):
        return {
            "id": f"am-{self.entity_id}-{random.randint(0, 65535)}",
            "alias": self.title,
            "mode": "single",
            "trigger": [
                {
                    "platform": "state",
                    "entity_id": self.entity_id,
                    "attribute": self.trigger_attribute,
                }
            ],
            "condition": [],
            "action": [
                {
                    "choose": [
                        {
                            "conditions": [
                                {
                                    "condition": "template",
                                    "value_template": join(
                                        "{{ ",
                                        "state_attr(",
                                        f"'{self.entity_id}'",
                                        f"'{self.trigger_attribute}')",
                                        " != ",
                                        "None",
                                        " }}",
                                    ),
                                }
                            ],
                            "sequence": [
                                {
                                    "service": "openhasp.push_image",
                                    "target": {
                                        "entity_id": f"openhasp.{self.plate.name}"
                                    },
                                    "data": {
                                        "image": "".join([self._prefix, self._url]),
                                        "obj": self.image_id,
                                        "width": self.width,
                                        "height": self.height,
                                        "fitscreen": True,
                                    },
                                },
                            ],
                        },
                        {
                            "conditions": [
                                {
                                    "condition": "template",
                                    "value_template": join(
                                        "{{ ",
                                        "not state_attr(",
                                        f"'{self.entity_id}',",
                                        f"'{self.trigger_attribute}')",
                                        " }}",
                                    ),
                                }
                            ],
                            "sequence": [
                                {
                                    "service": "openhasp.push_image",
                                    "target": {
                                        "entity_id": f"openhasp.{self.plate.name}"
                                    },
                                    "data": {
                                        "image": self.default_image,
                                        "obj": self.image_id,
                                        "fitscreen": True,
                                        "width": self.width,
                                        "height": self.height,
                                    },
                                },
                            ],
                        },
                    ]
                },
            ],
        }


class MediaPlayerArtworkAutomation(ArtworkAutomation):
    def __init__(
        self,
        entity_id,
        image,
        container,
        hass_ip=None,
        hass_port=8123,
        width=480,
        height=480,
        resizer_url=None,
        default_image=None,
    ):
        self.hass_ip = hass_ip
        self.hass_port = hass_port
        self.default_image = default_image
        self.resizer_url = resizer_url

        super().__init__(
            title=f"Media Player Artwork Automation ({entity_id})",
            entity_id=entity_id,
            image=image,
            container=container,
            trigger_attribute="entity_picture",
            default_image=default_image,
            width=width,
            height=height,
            resizer_url=resizer_url,
        )

    @property
    def _url(self):
        return "".join(
            [
                "http://",
                f"{self.hass_ip}:{self.hass_port}",
                "{{",
                f'state_attr("{self.entity_id}", "entity_picture") | urlencode',
                "}}",
            ]
        )


class SteamArtworkAutomation(ArtworkAutomation):
    def __init__(
        self, entity_id, image, container, width=480, height=480, resizer_url=None
    ):
        super().__init__(
            title=f"Steam Artwork Automation ({entity_id})",
            entity_id=entity_id,
            image=image,
            container=container,
            trigger_attribute="game_image_main",
            width=width,
            height=height,
            resizer_url=resizer_url,
        )

    @property
    def _url(self):
        return "".join(
            [
                "{{",
                f'state_attr("{self.entity_id}", "game_image_main")',
                "}}",
            ]
        )
