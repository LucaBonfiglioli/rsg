import pytest
from rsg.core import (
    Rsg,
    RsgBase,
    RsgDict,
    RsgFloat,
    RsgInt,
    RsgList,
    RsgStr,
    RsgTuple,
    generator,
)
from rsg.utils.helpers import make_attrs


class TestRsg:
    def test_empty(self):
        rsg = Rsg()
        for _ in range(10):
            assert next(rsg) is None

    def test_single_leaf(self):
        class MyRsg(Rsg):
            @generator("a_letter")
            def generate_a(self):
                return "A"

        rsg = MyRsg()
        for _ in range(10):
            assert next(rsg) == "A"

    def test_single_leaves(self):
        class MyRsg(Rsg):
            @generator("a")
            def generate_a(self):
                return "A"

            @generator("b")
            def generate_b(self):
                return "B"

        rsg = MyRsg(a_chance=0.1, b_chance=0.9)
        for _ in range(10):
            assert next(rsg) in ["A", "B"]

        # Only leaf nodes -> min/max depth should be ignored
        rsg = MyRsg(min_depth=10, max_depth=11)
        for _ in range(10):
            assert next(rsg) in ["A", "B"]

        # Only leaf nodes -> min/max breadth should be ignored
        rsg = MyRsg(min_breadth=10, max_breadth=20)
        for _ in range(10):
            assert next(rsg) in ["A", "B"]

    def test_complex(self):
        class MyStructure:
            def __init__(self, children):
                make_attrs(self, locals())

            def __eq__(self, __o: object) -> bool:
                return __o.children == self.children

        class MyRsg(Rsg):
            @generator("my_struct")
            def generate_my_struct(self, children):
                return MyStructure(children)

        rsg = MyRsg()
        for _ in range(10):
            assert isinstance(next(rsg), MyStructure)

        # Only composite nodes -> when max_depth = 0 shoud return empty struct
        rsg = MyRsg(min_depth=0, max_depth=0)
        for _ in range(10):
            assert next(rsg) == MyStructure([])

        def check_recursive(data):
            assert isinstance(data, MyStructure)
            for x in data.children:
                check_recursive(x)

        rsg = MyRsg(min_depth=2, max_depth=4, min_breadth=2, max_breadth=5)
        for _ in range(10):
            check_recursive(next(rsg))

    def test_complex(self):
        class MyRsg(Rsg):
            @generator("list")
            def generate_lis(self, children):
                return children

            @generator("a", default_chance=0.2)
            def generate_a(self, repeats: int):
                return "a" * repeats

        n = 4

        def check_recursive(data):
            if isinstance(data, list):
                for x in data:
                    check_recursive(x)
            else:
                assert data == "a" * n

        rsg = MyRsg(min_depth=2, max_depth=4, min_breadth=2, max_breadth=5, repeats=n)
        for _ in range(10):
            check_recursive(next(rsg))

        # 'repeats' not specified
        with pytest.raises(AttributeError):
            rsg = MyRsg(min_depth=2, max_depth=4, min_breadth=2, max_breadth=5)
            next(rsg)


class TestRsgList:
    def test_rsg_list(self):
        rsg = RsgList(min_depth=2, max_depth=4, min_breadth=2, max_breadth=4)
        for _ in range(10):
            assert isinstance(next(rsg), list)


class TestRsgDict:
    def test_rsg_dict(self):
        rsg = RsgDict(min_depth=2, max_depth=4, min_breadth=2, max_breadth=4)
        for _ in range(10):
            assert isinstance(next(rsg), dict)


class TestRsgTuple:
    def test_rsg_tuple(self):
        rsg = RsgTuple()
        for _ in range(10):
            assert isinstance(next(rsg), tuple)


class TestRsgInt:
    def test_rsg_int(self):
        rsg = RsgInt()
        for _ in range(10):
            assert isinstance(next(rsg), int)


class TestRsgFloat:
    def test_rsg_float(self):
        rsg = RsgFloat()
        for _ in range(10):
            assert isinstance(next(rsg), float)


class TestRsgStr:
    def test_rsg_str(self):
        rsg = RsgStr()
        for _ in range(10):
            assert isinstance(next(rsg), str)


class TestRsgBase:
    def test_rsg_base(self):
        rsg = RsgBase()
        for _ in range(10):
            assert next(rsg) is not None
