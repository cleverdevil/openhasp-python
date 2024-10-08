import openhasp as hasp
import openhasp.themes as themes

plate = hasp.Plate(name="theaterplate", w=800, h=480)

from . import common  # noqa

plate.common = common
plate.set_theme(themes.Dracula())


from . import page0 as _  # noqa
from . import page1 as _  # noqa
from . import page2 as _  # noqa
from . import page3 as _  # noqa
from . import page4 as _  # noqa
