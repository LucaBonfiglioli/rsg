from basics import RsgFooBar
from composite import RsgList
from parameters import RsgPowers


class RsgMixed(RsgFooBar, RsgList, RsgPowers):
    pass


if __name__ == "__main__":
    rsg = RsgMixed(
        base=3,
        foo_chance=0.1,
        bar_chance=0.1,
        power_chance=0.4,
        list_chance=0.4,
        min_depth=2,
        max_depth=3,
        min_breadth=2,
        max_breadth=4,
    )
    print(next(rsg))
