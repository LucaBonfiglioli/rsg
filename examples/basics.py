from rsg.core import Rsg, generator


class RsgFooBar(Rsg):
    @generator("foo", default_chance=0.6)
    def generate_foo(self):
        return "foo"

    @generator("bar", default_chance=0.6)
    def generate_bar(self):
        return "bar"


if __name__ == "__main__":
    rsg = RsgFooBar(foo_chance=0.8, bar_chance=0.2)
    [print(next(rsg)) for _ in range(10)]
