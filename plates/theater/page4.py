"""
Theater Plate: Page 4
=====================

"Power Off" page that displays a helpful message about how to use the plate.
"""

import openhasp as hasp

plate = hasp.plates.get("theaterplate")

plate.page(layout=hasp.GridLayout(32, 20), title="Page 4 - Idle")
plate.set_font("32", "#FFFFFF")
plate.add(hasp.Label(text="Power Off", align="left"), c=5, r=0.5, w=28, h=4)

plate.set_font("24", "#ffffff")
welcome_message = (
    "Select an activity using the buttons on the left. "
    "To control the lights, fan, or magic poster, tap the "
    "home control button on the bottom right of the screen."
)
plate.add(
    hasp.Label(text=welcome_message, align="left", mode="break"), c=5, r=4, w=26, h=14
)
