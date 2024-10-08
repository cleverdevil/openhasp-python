from __future__ import annotations

from dataclasses import dataclass, fields
from enum import Enum
from typing import Annotated

from . import types


@dataclass
class Color:
    r: Annotated[int, types.Annotated[int, types.int8]]
    g: Annotated[int, types.Annotated[int, types.int8]]
    b: Annotated[int, types.Annotated[int, types.int8]]

    @classmethod
    def from_hex(cls, hex_value: str) -> Color:
        r_str, g_str, b_str = hex_value[1:3], hex_value[3:5], hex_value[5:7]
        return Color(r=int(r_str, 16), g=int(g_str, 16), b=int(b_str, 16))

    @property
    def hex(self) -> str:
        return "#%02x%02x%02x" % (self.r, self.g, self.b)

    @property
    def json(self):
        return self.hex


def color(hx):
    return Color.from_hex(hx)


class JSONEncodableEnum(Enum):
    @property
    def json(self):
        return self.value


class GradientDirection(JSONEncodableEnum):
    NONE = 0
    HORIZONTAL = 1
    VERTICAL = 2

    @property
    def json(self):
        return self.value


class BorderSide(JSONEncodableEnum):
    NONE = 0
    BOTTOM = 1
    TOP = 2
    TOP_BOTTOM = 3
    LEFT = 4
    BOTTOM_LEFT = 5
    TOP_LEFT = 6
    TOP_BOTTOM_LEFT = 7
    RIGHT = 8
    BOTTOM_RIGHT = 9
    TOP_RIGHT = 10
    TOP_BOTTOM_RIGHT = 11
    LEFT_RIGHT = 12
    BOTTOM_LEFT_RIGHT = 13
    TOP_LEFT_RIGHT = 14
    FULL = 15


class TextDecor(JSONEncodableEnum):
    NONE = 0
    UNDERLINE = 1
    STRIKETHROUGH = 2
    UNDERLINE_STRIKETHROUGH = 3


class ObjectStylePart(JSONEncodableEnum):
    MAIN = 0
    INDICATOR = 10
    KNOB = 20
    ITEMS_BACKGROUND = 30
    ITEMS = 40
    SELECTED_ITEM = 50
    MAJOR_TICKS = 60
    TEXT_CURSOR = 70
    SCROLLBAR = 80
    OTHER = 90


class ObjectStyleState(JSONEncodableEnum):
    DEFAULT = 0
    TOGGLED = 1
    PRESSED = 2
    PRESSED_TOGGLED = 3
    DISABLED = 4
    DISABLED_TOGGLED = 5


class ObjectStyleBase:
    part: ObjectStylePart = None
    state: ObjectStyleState = None

    def apply(self, s):
        if isinstance(s, ObjectStylePart):
            self.part = s
        elif isinstance(s, ObjectStyleState):
            self.state = s

    @property
    def json(self):
        j = {}
        for f in fields(self):
            if f.name.startswith("_"):
                continue

            if f.name in ("part", "state"):
                continue

            value = getattr(self, f.name)
            if value is not None:
                name = f.name
                descriptor = 0

                if self.part:
                    descriptor += self.part.value

                if self.state:
                    descriptor += self.state.value

                if descriptor:
                    name = f"{f.name}{descriptor:02d}"

                if hasattr(value, "json"):
                    value = value.json

                j[name] = value
        return j


@dataclass
class GeneralStyle(ObjectStyleBase):
    radius: Annotated[int, types.Annotated[int, types.int16]] = None
    clip_corner: bool = None


@dataclass
class PaddingAndMarginStyle(ObjectStyleBase):
    pad_top: Annotated[int, types.int16] = None
    pad_bottom: Annotated[int, types.int16] = None
    pad_left: Annotated[int, types.int16] = None
    pad_right: Annotated[int, types.int16] = None
    pad_inner: Annotated[int, types.int16] = None
    margin_top: Annotated[int, types.int16] = None
    margin_bottom: Annotated[int, types.int16] = None
    margin_left: Annotated[int, types.int16] = None
    margin_right: Annotated[int, types.int16] = None


@dataclass
class BackgroundStyle(ObjectStyleBase):
    bg_opa: Annotated[int, types.Annotated[int, types.int8]] = None
    bg_color: Color = None
    bg_grad_color: Color = None
    bg_grad_dir: GradientDirection = None
    bg_grad_stop: Annotated[int, types.Annotated[int, types.int8]] = None
    bg_main_stop: Annotated[int, types.Annotated[int, types.int8]] = None


@dataclass
class BorderStyle(ObjectStyleBase):
    border_color: Color = None
    border_opa: Annotated[int, types.Annotated[int, types.int8]] = None
    border_width: Annotated[int, types.Annotated[int, types.int8]] = None
    border_side: BorderSide = None
    border_post: bool = None


@dataclass
class OutlineStyle(ObjectStyleBase):
    outline_color: Color = None
    outline_opa: Annotated[int, types.Annotated[int, types.int8]] = None
    outline_width: Annotated[int, types.Annotated[int, types.int8]] = None
    outline_pad: Annotated[int, types.Annotated[int, types.int16]] = None


@dataclass
class ShadowStyle(ObjectStyleBase):
    shadow_color: Color = None
    shadow_opa: Annotated[int, types.Annotated[int, types.int8]] = None
    shadow_width: Annotated[int, types.int16] = None
    shadow_ofs_x: Annotated[int, types.int16] = None
    shadow_ofs_y: Annotated[int, types.int16] = None
    shadow_spread: Annotated[int, types.Annotated[int, types.int8]] = None


@dataclass
class TextStyle(ObjectStyleBase):
    text_color: Color = None
    text_font: str = None
    text_opa: Annotated[int, types.Annotated[int, types.int8]] = None
    text_letter_space: Annotated[int, types.int16] = None
    text_line_space: Annotated[int, types.int16] = None
    text_decor: TextDecor = None
    text_sel_color: Color = None


@dataclass
class LineStyle(ObjectStyleBase):
    line_color: Color = None
    line_opa: Annotated[int, types.Annotated[int, types.int8]] = None
    line_width: Annotated[int, types.int16] = None
    line_rounded: bool = None
    line_dash_width: Annotated[int, types.int16] = None
    line_dash_gap: Annotated[int, types.int16] = None


@dataclass
class ScaleStyle(ObjectStyleBase):
    scale_grad_color: Color = None
    scale_end_color: Color = None
    scale_width: Annotated[int, types.int16] = None
    scale_border_width: Annotated[int, types.int16] = None
    scale_end_line_width: Annotated[int, types.int16] = None
    scale_end_border_width: Annotated[int, types.int16] = None


@dataclass
class ImageStyle(ObjectStyleBase):
    image_opa: Annotated[int, types.Annotated[int, types.int8]] = None
    image_recolor: Color = None
    image_recolor_opa: Annotated[int, types.Annotated[int, types.int8]] = None


@dataclass
class ObjectStyle(
    GeneralStyle,
    PaddingAndMarginStyle,
    BackgroundStyle,
    BorderStyle,
    OutlineStyle,
    ShadowStyle,
    TextStyle,
    LineStyle,
    ScaleStyle,
    ImageStyle,
):
    pass


class ObjectStyles:

    def __init__(self, obj):
        self.obj = obj
        self.styles = []
        self.profile = None

    def use_profile(self, profile="defaults"):
        self.profile = profile
        return self.obj

    def finalize_styles(self):
        if not self.profile:
            return

        if not getattr(self.obj.plate, "theme"):
            return

        profile_styles = self.obj.plate.theme.styles_for(self.profile)
        for target, styles in profile_styles.items():
            s = ObjectStyle(**styles)

            targets = [target]
            if isinstance(target, (list, tuple)):
                targets = target

            for target in targets:
                s.apply(target)

            self.styles.append(s)

    def set(
        self,
        part=None,
        state=None,
        **styles,
    ):
        if len(styles):
            s = ObjectStyle(**styles)
            s.part = part
            s.state = state
            self.styles.append(s)
        return self.obj

    @property
    def json(self):
        self.finalize_styles()
        j = {}
        for style in self.styles:
            j.update(style.json)
        return j
