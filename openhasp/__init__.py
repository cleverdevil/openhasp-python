from __future__ import annotations

import json
import math
from dataclasses import dataclass, field, fields
from enum import Enum
from typing import Annotated

import yaml

from openhasp.automation import HASSConfiguration

from . import icons, styling, types

#
# Plates
#


class PlateCollection:
    def __init__(self):
        self.plates = {}

    def add(self, plate):
        self.plates[plate.name] = plate

    def get(self, name):
        return self.plates.get(name)

    @property
    def jsonl(self):
        jsonl = {}
        for name, plate in self.plates.items():
            jsonl[name] = plate.jsonl
        return jsonl

    @property
    def hass_yaml(self):
        return "\n".join([plate.hass_yaml for _, plate in self.plates.items()])

    @property
    def hass_automations_yaml(self):
        return "\n".join(
            [plate.hass_automations_yaml for _, plate in self.plates.items()]
        )


plates = PlateCollection()


class Plate:
    def __init__(self, name, w, h, theme=None):
        self._id_counter = 0
        self.name = name
        self.w = w
        self.h = h
        self.text_font = None
        self.text_color = None
        self.pages = []
        self.automations = []
        self.theme = theme

        plates.add(self)

    def set_theme(self, theme):
        self.theme = theme

    def id(self):
        self._id_counter += 1
        return self._id_counter

    def page(self, layout, title, *args):
        page = Page(self, layout=layout, title=title, *args)
        layout.page = page
        self.pages.append(page)
        return page

    def add(self, obj, *args, **kwargs):
        obj.plate = self
        if self.text_font is not None:
            obj.styles.set(text_font=self.text_font)
        if self.text_color is not None:
            obj.styles.set(text_color=self.text_color)
        self.pages[-1].add(obj, *args, **kwargs)
        return obj

    def add_automation(self, automation):
        automation.plate = self
        self.automations.append(automation)

    def set_font(self, text_font, text_color):
        self.text_font = text_font
        self.text_color = text_color

    @property
    def json(self):
        for page in self.pages:
            for child in page.children:
                yield child.json

    @property
    def jsonl(self):
        rows = []
        for child in self.json:
            if isinstance(child, list):
                for j in child:
                    rows.append(j)
            else:
                rows.append(child)

        return "\n".join([json.dumps(row) for row in rows])

    @property
    def hass_yaml(self):
        objects = []
        for page in self.pages:
            for child in page.children:
                if child.has_automations:
                    objects.append(child.hass.yaml)
        return yaml.dump({self.name: {"objects": objects}})

    @property
    def hass_automations_yaml(self):
        automations = []
        for a in self.automations:
            y = a.yaml
            if isinstance(y, list):
                automations.extend(y)
            else:
                automations.append(y)
        return yaml.dump([a for a in automations])


#
# Layouts
#


@dataclass
class Layout:
    children: list[str] = field(default_factory=list)


class GridLayout(Layout):
    def __init__(self, c, r, padding_x=0, padding_y=0):
        self.c = c
        self.r = r
        self.padding = (padding_x, padding_y)
        super().__init__()

    @property
    def cell_width(self):
        return math.floor(self.page.plate.w / self.c)

    @property
    def cell_height(self):
        return math.floor(self.page.plate.h / self.r)

    def add_internal(self, obj):
        self.children.append(obj)
        obj.id = self.page.plate.id()
        obj._layout = self
        self.children.append(obj)

    def add(self, obj, c=None, r=None, w=None, h=None, **kw):
        padding_x = self.padding[0]
        padding_y = self.padding[1]

        if kw.get("ignore_padding"):
            padding_x = 0
            padding_y = 0

        if c is not None and r is not None and w is not None and h is not None:
            obj.x = (self.cell_width * c) + padding_x
            obj.y = (self.cell_height * r) + padding_y
            obj.w = (self.cell_width * w) - (2 * padding_x)
            obj.h = (self.cell_height * h) - (2 * padding_y)

        self.children.append(obj)
        obj.id = self.page.plate.id()

        obj._layout = self

    @property
    def json(self):
        return [child.json for child in self.children]


#
# Pages
#


class Page:
    def __init__(self, plate, layout=None, title=None):
        self.plate = plate
        self.title = title
        self._page_added = False
        self.set_layout(layout)

    def set_layout(self, layout):
        self.layout = layout
        layout.page = self

    def add(self, obj, *args, **kwargs):
        if not self._page_added:
            self.layout.children.append(Comment(comment=self.title, page=self.number))
            self._page_added = True

        obj.page = self.number
        obj.plate = self.plate

        self.layout.add(obj, *args, **kwargs)

    @property
    def number(self):
        for i, page in enumerate(self.plate.pages):
            if page == self:
                return i
        return 0

    @property
    def children(self):
        return self.layout.children


#
# Objects
#


@dataclass
class Object:
    obj: str = "obj"
    id: Annotated[int, types.ValueRange(1, 254)] = None
    page: Annotated[int, types.ValueRange(0, 12)] = None
    groupid: Annotated[int, types.ValueRange(0, 15)] = None
    x: Annotated[int, types.int16] = 0
    y: Annotated[int, types.int16] = 0
    w: Annotated[int, types.int16] = 0
    h: Annotated[int, types.int16] = 0
    enabled: bool = None
    hidden: bool = None
    action: str = None
    click: bool = None
    ext_click_h: Annotated[int, types.uint8] = None
    ext_click_v: Annotated[int, types.uint8] = None
    parentid: Annotated[int, types.uint8] = None
    text_font: str = None
    align: str = None
    pad_top: Annotated[int, types.int16] = None
    pad_bottom: Annotated[int, types.int16] = None
    pad_left: Annotated[int, types.int16] = None
    pad_right: Annotated[int, types.int16] = None
    value_str: str = None
    value_ofs_y: Annotated[int, types.int16] = None
    value_font: Annotated[int, types.uint8] = None

    _hass: HASSConfiguration = None
    _styles: styling.ObjectStyles = None

    @property
    def json(self):
        j = {}

        for f in fields(self):
            if f.name.startswith("_"):
                continue
            value = getattr(self, f.name)
            if value is not None:
                j[f.name] = value

        j.update(self.styles.json)

        return j

    @property
    def styles(self):
        if not self._styles:
            self._styles = styling.ObjectStyles(self)
        return self._styles

    @property
    def hass(self):
        if not self._hass:
            self._hass = HASSConfiguration(target=self)
        return self._hass

    @property
    def has_automations(self):
        return self._hass is not None


@dataclass
class Comment:
    page: Annotated[int, types.ValueRange(0, 12)] = None
    comment: str = None
    has_automations = False

    @property
    def json(self):
        if self.page:
            return dict(page=self.page, comment=self.comment)
        return dict(comment=self.comment)


@dataclass
class Button(Object):
    obj: str = "btn"
    toggle: bool = False
    val: Annotated[int, types.on_off] = None
    text: str = None
    mode: str = None


@dataclass
class Switch(Object):
    obj: str = "switch"
    val: Annotated[int, types.on_off] = None


@dataclass
class Label(Object):
    obj: str = "label"
    text: str = None
    mode: str = None
    align: str = None


@dataclass
class Slider(Object):
    obj: str = "slider"
    val: Annotated[int, types.int16] = 0
    min: Annotated[int, types.int16] = 0
    max: Annotated[int, types.int16] = 0


@dataclass
class Image(Object):
    obj: str = "img"
    src: str = None
    auto_size: bool = None
    offset_x: Annotated[int, types.int16] = None
    offset_y: Annotated[int, types.int16] = None
    zoom: Annotated[int, types.uint16] = None
    angle: Annotated[int, types.int16] = None
    pivot_x: Annotated[int, types.int16] = None
    pivot_y: Annotated[int, types.int16] = None
    antialias: bool = None


ArcType = Enum("ArcType", ["NORMAL", "SYMMETRICAL", "REVERSE"])


@dataclass
class Arc(Object):
    obj: str = "arc"
    min: Annotated[int, types.int16] = None
    max: Annotated[int, types.int16] = None
    val: Annotated[int, types.int16] = None
    rotation: Annotated[int, types.int16] = None
    type: ArcType = ArcType.NORMAL
    adjustable: bool = None
    start_angle: Annotated[int, types.angle] = None
    end_angle: Annotated[int, types.angle] = None
    start_angle10: Annotated[int, types.angle] = None
    end_angle10: Annotated[int, types.angle] = None


@dataclass
class Gauge(Object):
    obj: str = "gauge"
    min: Annotated[int, types.int16] = None
    max: Annotated[int, types.int16] = None
    val: Annotated[int, types.int16] = None
    critical_value: Annotated[int, types.int16] = None
    label_count: Annotated[int, types.uint8] = None
    line_count: Annotated[int, types.uint16] = None
    angle: Annotated[int, types.angle] = None
    rotation: Annotated[int, types.angle] = None
    format: Annotated[int, types.uint16] = None


@dataclass
class Bar(Object):
    obj: str = "bar"
    val: Annotated[int, types.int16] = None
    min: Annotated[int, types.int16] = None
    max: Annotated[int, types.int16] = None
    start_value: Annotated[int, types.int16] = None


@dataclass
class ButtonMatrix(Object):
    obj: str = "btnmatrix"
    options: list = field(default_factory=list)
    toggle: bool = False
    one_check: bool = None
    val: Annotated[int, types.int8] = None

    def add_row(self, *items):
        self.options.extend(items)
        self.options.append("\n")


@dataclass
class Roller(Object):
    obj: str = "roller"
    options: list = field(default_factory=list)
    val: Annotated[int, types.int16] = None
    text: str = None
    rows: Annotated[int, types.int8] = None
    mode: Annotated[int, types.on_off] = None

    @property
    def json(self):
        j = super().json
        j["options"] = "\n".join((str(i) for i in self.options))

        if self.val is not None:
            return [j, {"obj": "roller", "id": self.id, "val": self.val}]

        return j


@dataclass
class ColorPicker(Object):
    obj: str = "cpicker"
    scale_width: Annotated[int, types.uint16] = None
    pad_inner: Annotated[int, types.int16] = None
    mode: str = None
    mode_fixed: bool = None


class TabButtonPosition:
    NONE = 0
    TOP = 1
    BOTTOM = 2
    LEFT = 3
    RIGHT = 4


@dataclass
class Tab(Object):
    obj: str = "tab"
    text: str = None

    @property
    def json(self):
        j = super().json
        del j["w"]
        del j["h"]
        return j


@dataclass
class TabView(Object):
    obj: str = "tabview"
    btn_pos: int = TabButtonPosition.TOP
    val: Annotated[int, types.int8] = None

    @property
    def json(self):
        j = super().json
        del j["w"]
        del j["h"]
        return j


#
# Pre-Assembled Widgets
#


@dataclass
class MediaControlsButtonMatrix(ButtonMatrix):
    buttons = [
        "volume_mute",
        "info",
        "keyboard_arrow_up",
        "home",
        "info",
        "\n",
        "volume_up",
        "keyboard_arrow_left",
        "filter_tilt_shift",
        "keyboard_arrow_right",
        "replay",
        "\n",
        "volume_down",
        "arrow_back",
        "keyboard_arrow_down",
        "menu",
        "forward_media",
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.options = [icons.get(x) if x != "\n" else x for x in self.buttons]
