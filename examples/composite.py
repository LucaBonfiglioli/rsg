from rsg.core import Rsg, generator
from typing import Iterable, Any


class RsgList(Rsg):
    @generator("list")
    def generate_list(self, children: Iterable[Any]) -> list:
        return list(children)


if __name__ == "__main__":
    rsg = RsgList(min_depth=1, max_depth=3, min_breadth=2, max_breadth=4)
    print(next(rsg))
