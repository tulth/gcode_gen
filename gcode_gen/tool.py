import numpy as np
from . import base_types
from . import number


class Tool(base_types.Named):
    def __init__(self,
                 cut_diameter,
                 cut_height,
                 shank_diameter=(1 / 8 * number.mm_per_inch),
                 name=None,
                 ):
        super().__init__(name)
        self.cut_diameter = cut_diameter
        self.shank_diameter = shank_diameter
        self.cut_height = cut_height

    @property
    def default_name(self):
        return self.__class__.__name__


class Carbide3D_101(Tool):
    def __init__(self,
                 ):
        super().__init__(cut_diameter=(1 / 8 * number.mm_per_inch),
                         cut_height=(0.75 * number.mm_per_inch),
                         shank_diameter=(1 / 8 * number.mm_per_inch),
                         )


class Carbide3D_102(Tool):
    def __init__(self,
                 ):
        super().__init__(cut_diameter=(1 / 8 * number.mm_per_inch),
                         cut_height=(0.75 * number.mm_per_inch),
                         shank_diameter=(1 / 8 * number.mm_per_inch),
                         )


class Carbide3D_112(Tool):
    def __init__(self,
                 ):
        super().__init__(cut_diameter=(1 / 16 * number.mm_per_inch),
                         cut_height=(0.25 * number.mm_per_inch),
                         shank_diameter=(1 / 8 * number.mm_per_inch),
                         )


class InventablesPcbDrill_1p2mm(Tool):
    def __init__(self,
                 ):
        super().__init__(cut_diameter=1.2,
                         cut_height=(0.4 * number.mm_per_inch),
                         shank_diameter=(1 / 8 * number.mm_per_inch),
                         )


class InventablesPcbDrill_1p1mm(Tool):
    def __init__(self,
                 ):
        super().__init__(cut_diameter=1.1,
                         cut_height=(0.4 * number.mm_per_inch),
                         shank_diameter=(1 / 8 * number.mm_per_inch),
                         )


class InventablesPcbDrill_1p0mm(Tool):
    def __init__(self,
                 ):
        super().__init__(cut_diameter=1,
                         cut_height=(0.4 * number.mm_per_inch),
                         shank_diameter=(1 / 8 * number.mm_per_inch),
                         )


class InventablesPcbDrill_0p9mm(Tool):
    def __init__(self,
                 ):
        super().__init__(cut_diameter=0.9,
                         cut_height=(0.4 * number.mm_per_inch),
                         shank_diameter=(1 / 8 * number.mm_per_inch),
                         )


class InventablesPcbDrill_0p8mm(Tool):
    def __init__(self,
                 ):
        super().__init__(cut_diameter=0.8,
                         cut_height=(0.4 * number.mm_per_inch),
                         shank_diameter=(1 / 8 * number.mm_per_inch),
                         )


class InventablesPcbDrill_0p7mm(Tool):
    def __init__(self,
                 ):
        super().__init__(cut_diameter=0.7,
                         cut_height=(0.4 * number.mm_per_inch),
                         shank_diameter=(1 / 8 * number.mm_per_inch),
                         )


class InventablesPcbDrill_0p6mm(Tool):
    def __init__(self,
                 ):
        super().__init__(cut_diameter=0.6,
                         cut_height=(0.4 * number.mm_per_inch),
                         shank_diameter=(1 / 8 * number.mm_per_inch),
                         )


class InventablesPcbDrill_0p5mm(Tool):
    def __init__(self,
                 ):
        super().__init__(cut_diameter=0.5,
                         cut_height=(0.4 * number.mm_per_inch),
                         shank_diameter=(1 / 8 * number.mm_per_inch),
                         )


class InventablesPcbDrill_0p4mm(Tool):
    def __init__(self,
                 ):
        super().__init__(cut_diameter=0.4,
                         cut_height=(0.4 * number.mm_per_inch),
                         shank_diameter=(1 / 8 * number.mm_per_inch),
                         )


class InventablesPcbDrill_0p3mm(Tool):
    def __init__(self,
                 ):
        super().__init__(cut_diameter=0.3,
                         cut_height=(0.4 * number.mm_per_inch),
                         shank_diameter=(1 / 8 * number.mm_per_inch),
                         )


class InventablesPcbMill_P3_3002(Tool):
    def __init__(self,
                 ):
        self.cutAngle = 30 * np.pi / 180
        shank_diameter = (1 / 8 * number.mm_per_inch)
        cut_height = (shank_diameter / 2) / np.tan(self.cutAngle / 2)
        super().__init__(cut_diameter=0.2,
                         cut_height=cut_height,
                         shank_diameter=shank_diameter,
                         )


class Mill_0p5mm(Tool):
    def __init__(self,
                 ):
        super().__init__(cut_diameter=0.5,
                         cut_height=(0.25 * number.mm_per_inch),  # FIXME?
                         shank_diameter=(1 / 8 * number.mm_per_inch),
                         )


class Mill_0p01mm(Tool):  # not for real! For testing extreme cases
    def __init__(self,
                 ):
        super().__init__(cut_diameter=0.01,
                         cut_height=(0.25 * number.mm_per_inch),  # FIXME?
                         shank_diameter=(1 / 8 * number.mm_per_inch),
                         )


