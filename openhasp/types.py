from dataclasses import dataclass


@dataclass
class ValueRange:
    min: int
    max: int

    def validate_value(self, x):
        if not (self.min <= x <= self.max):
            raise ValueError(f"{x} must be in range [{self.min}, {self.max}]")


uint8 = ValueRange(0, 255)
uint16 = ValueRange(0, 65535)
int8 = ValueRange(-128, 128)
int16 = ValueRange(-32767, 32767)
angle = ValueRange(0, 360)
on_off = ValueRange(0, 1)
