import openhasp


class Theme:
    colors = dict(
        background=None,
        background_secondary=None,
        background_tertiary=None,
        selection=None,
        foreground=None,
        active_1=None,
        active_2=None,
        active_3=None,
        active_4=None,
        active_5=None,
        active_6=None,
        active_7=None,
        active_8=None,
    )

    def __init__(self):
        self.styles = {
            "default": {
                openhasp.styling.ObjectStylePart.MAIN: {
                    "bg_color": self.colors["background"],
                    "text_color": self.colors["foreground"],
                }
            },
            "navigation": {
                openhasp.styling.ObjectStylePart.MAIN: {
                    "bg_color": self.colors["background_secondary"],
                    "text_color": self.colors["foreground"],
                    "shadow_color": openhasp.styling.color("#000000"),
                    "shadow_opa": 100,
                    "shadow_width": 10,
                    "shadow_ofs_x": 3,
                    "shadow_ofs_y": 3,
                    "radius": 0,
                },
                (
                    openhasp.styling.ObjectStylePart.ITEMS,
                    openhasp.styling.ObjectStyleState.TOGGLED,
                ): {"bg_color": self.colors["active_6"]},
            },
            "floating-button": {
                openhasp.styling.ObjectStylePart.MAIN: {
                    "bg_color": self.colors["foreground"],
                    "border_color": self.colors["active_5"],
                    "text_color": self.colors["background"],
                    "radius": 50,
                    "shadow_color": self.colors["background_tertiary"],
                    "shadow_opa": 100,
                    "shadow_width": 10,
                    "shadow_ofs_x": 3,
                    "shadow_ofs_y": 3,
                },
                (
                    openhasp.styling.ObjectStylePart.MAIN,
                    openhasp.styling.ObjectStyleState.TOGGLED,
                ): {
                    "bg_color": self.colors["active_6"],
                    "border_color": self.colors["foreground"],
                    "text_color": self.colors["foreground"],
                },
            },
            "floating-panel": {
                openhasp.styling.ObjectStylePart.MAIN: {
                    "radius": 10,
                    "shadow_color": self.colors["background_tertiary"],
                    "shadow_opa": 100,
                    "shadow_width": 10,
                    "shadow_ofs_x": 3,
                    "shadow_ofs_y": 3,
                    "bg_color": self.colors["background_tertiary"],
                }
            },
            "control-matrix": {
                openhasp.styling.ObjectStylePart.MAIN: {
                    "border_width": 0,
                    "bg_color": self.colors["background_tertiary"],
                },
                openhasp.styling.ObjectStylePart.ITEMS: {
                    "bg_color": self.colors["background_secondary"],
                    "text_color": self.colors["foreground"],
                    "border_color": self.colors["foreground"],
                    "border_opa": 50,
                },
            },
            "small-control-matrix": {
                openhasp.styling.ObjectStylePart.MAIN: {
                    "border_width": 0,
                    "bg_color": self.colors["background"],
                    "pad_top": 2,
                    "pad_bottom": 2,
                    "pad_left": 2,
                    "pad_right": 2,
                    "pad_inner": 2,
                },
                openhasp.styling.ObjectStylePart.ITEMS: {
                    "bg_color": self.colors["background_secondary"],
                    "text_color": self.colors["foreground"],
                    "border_color": self.colors["foreground"],
                    "border_opa": 50,
                },
            },
        }

    def styles_for(self, profile):
        return self.styles.get(profile, self.styles["default"])


class Dracula(Theme):
    colors = dict(
        background="#282a36",  # dark gray
        background_secondary="#44475a",  # gray
        background_tertiary="#0E0D12",  # very dark gray
        selection="#ff79c6",  # pink
        foreground="#f8f8f2",  # off-white
        active_1="#6272a4",  # muted purple
        active_2="#8be9fd",  # cyan
        active_3="#50fa7b",  # green
        active_4="#ffb86c",  # orange
        active_5="#ff79c6",  # pink
        active_6="#bd93f9",  # purple
        active_7="#ff5555",  # red
        active_8="#f1fa8c",  # yellow
    )
