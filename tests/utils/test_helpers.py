import pytest
from rsg.utils.helpers import inspect_signature, make_attrs


class TestMakeAttrs:
    class MyClass:
        make_attrs_private: bool = False
        private_prefix: str = "_"

        def __init__(self, arg1, arg2, arg3, kwarg1=10, kwarg2=0.12, **kwargs) -> None:
            make_attrs(
                self,
                locals(),
                private=self.make_attrs_private,
                ignore=("self",),
                private_prefix=self.private_prefix,
                recur_on=("kwargs",),
            )

    @pytest.mark.parametrize(["private"], [[True], [False]])
    def test_make_attrs(self, private: bool):
        self.MyClass.make_attrs_private = private
        kwargs = {
            "arg1": 3,
            "arg2": ("a", "b"),
            "arg3": {"a": 10, "b": 0.10},
            "kwarg1": 3,
            "kwarg2": 12,
            "kwarg3": [10, "hello"],
        }
        my_obj = self.MyClass(**kwargs)
        for k, v in kwargs.items():
            if private:
                k = f"{self.MyClass.private_prefix}{k}"
            assert getattr(my_obj, k) == v


class TestInspectSignature:
    @staticmethod
    def simple_function():
        pass

    def simple_method(self):
        pass

    @classmethod
    def simple_clsmethod(cls):
        pass

    @staticmethod
    def argonly_function(arg1, arg2, arg3):
        pass

    def argonly_method(self, arg1, arg2, arg3):
        pass

    @classmethod
    def argonly_clsmethod(cls, arg1, arg2, arg3):
        pass

    @staticmethod
    def kwargonly_function(kwarg1="hello", kwarg2=1.0):
        pass

    def kwargonly_method(self, kwarg1="hello", kwarg2=1.0):
        pass

    @classmethod
    def kwargonly_clsmethod(cls, kwarg1="hello", kwarg2=1.0):
        pass

    @staticmethod
    def full_function(arg1, arg2, arg3, kwarg1="hello", kwarg2=1.0):
        pass

    def full_method(self, arg1, arg2, arg3, kwarg1="hello", kwarg2=1.0):
        pass

    @classmethod
    def full_clsmethod(cls, arg1, arg2, arg3, kwarg1="hello", kwarg2=1.0):
        pass

    args = ["arg1", "arg2", "arg3"]
    kwargs = {"kwarg1": "hello", "kwarg2": 1.0}
    simple_params = ([], {})
    argonly_params = (args, {})
    kwargonly_params = ([], kwargs)
    full_params = (args, kwargs)

    @pytest.mark.parametrize(
        ["fn", "expected"],
        [
            ["simple_function", simple_params],
            ["simple_method", simple_params],
            ["simple_clsmethod", simple_params],
            ["argonly_function", argonly_params],
            ["argonly_method", argonly_params],
            ["argonly_clsmethod", argonly_params],
            ["kwargonly_function", kwargonly_params],
            ["kwargonly_method", kwargonly_params],
            ["kwargonly_clsmethod", kwargonly_params],
            ["full_function", full_params],
            ["full_method", full_params],
            ["full_clsmethod", full_params],
        ],
    )
    def test_inspect_signature(self, fn, expected):
        fn = getattr(self, fn)
        res = inspect_signature(fn)
        assert res == expected
