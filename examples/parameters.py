from random import randint
from rsg.core import Rsg, generator


class RsgPowers(Rsg):
    @generator("power")
    def generate_power(self, base: int, max_exp: int = 5):
        exp = randint(0, max_exp)
        return base**exp


if __name__ == "__main__":
    rsg = RsgPowers(base=2, max_exp=10)
    [print(next(rsg)) for _ in range(10)]
