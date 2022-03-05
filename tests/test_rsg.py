import rich
from rsg.core import RsgBase, generator


class RsgSasso(RsgBase):
    @generator("sasso")
    def _generate_sasso(self) -> str:
        return f"SASSO"


def test_rsg():
    generator = RsgSasso(
        min_depth=4,
        max_depth=4,
        list_chance=1.0,
        dict_chance=1.0,
        min_breadth=1,
        max_breadth=4,
        sasso_chance=1.0,
        max_float_val=0.1,
    )
    for _ in range(100):
        rich.print(next(generator))
