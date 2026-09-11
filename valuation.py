from typing import Mapping, Union

from esovalue.eso import value_eso

Number = Union[int, float]

FIXED_PARAMETERS = {"iterations": 50, "m": None}


def option_value(parameters: Mapping[str, Number]) -> float:
    return float(value_eso(**dict(FIXED_PARAMETERS, **parameters)))
