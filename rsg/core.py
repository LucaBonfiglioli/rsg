from __future__ import annotations

import copy
import inspect
import string
from abc import ABCMeta
from random import choice, choices, randint, random
from typing import Any, Callable

from rsg.utils.helpers import make_attrs

_gen_meth_t = Callable[[], Any]


class _GeneratorFn:
    def __init__(
        self,
        name: str,
        is_leaf: bool,
        method: _gen_meth_t,
        argnames: list[str],
        kwargnames: dict[str, Any],
    ) -> None:
        make_attrs(self, locals(), private=True)

    @property
    def name(self) -> str:
        return self._name

    @property
    def is_leaf(self) -> bool:
        return self._is_leaf

    @property
    def chance_kw(self) -> str:
        return f"{self.name}_chance"

    def __call__(self, caller: Any) -> Any:
        args = [getattr(caller, x) for x in self._argnames]
        kwargs = {k: getattr(caller, k, v) for k, v in self._kwargnames.items()}
        return self._method(caller, *args, **kwargs)

    def __repr__(self) -> str:
        return f"GeneratorFn({self.name}, {self._method.__name__})"

    def __hash__(self) -> int:
        return hash(self.name)


class _GeneratorFnFactory:
    @classmethod
    def _inspect_signature(cls, fn: Callable) -> tuple[list[str], dict[str, Any]]:
        params = inspect.signature(fn).parameters
        args = []
        kwargs = {}
        for k, v in params.items():
            if k == "self":
                continue
            if v.default == inspect._empty:
                args.append(k)
            else:
                kwargs[k] = v.default
        return args, kwargs

    @classmethod
    def create(cls, name: str, is_leaf: bool, fn: Callable) -> _GeneratorFn:
        args, kwargs = cls._inspect_signature(fn)
        return _GeneratorFn(name, is_leaf, fn, args, kwargs)


def generator(name: str, is_leaf: bool = False) -> Callable[[Callable], _GeneratorFn]:
    def _wrapped(fn: Callable) -> _GeneratorFn:
        return _GeneratorFnFactory.create(name, is_leaf, fn)

    return _wrapped


class RsgMeta(ABCMeta):
    def __init__(self, name, bases, namespace) -> None:
        super().__init__(name, bases, namespace)
        gen = inspect.getmembers(self, predicate=lambda x: isinstance(x, _GeneratorFn))
        self._generators_map: dict[str, _GeneratorFn] = {v.name: v for _, v in gen}


class Rsg(metaclass=RsgMeta):
    @classmethod
    @property
    def _generators(cls) -> set[_GeneratorFn]:
        return set(cls._generators_map.values())

    def __init__(
        self,
        min_depth: int = 0,
        max_depth: int = 4,
        min_breadth: int = 2,
        max_breadth: int = 4,
        **kwargs,
    ) -> None:
        make_attrs(self, locals())
        self._kwargs = kwargs
        self._child = None

        if len(self._generators) == 0:
            gen = _GeneratorFnFactory.create("default", True, (lambda self: None))
            self._generators_map[gen.name] = gen

        leaf_gen = {x for x in self._generators if x.is_leaf}
        non_leaf_gen = {x for x in self._generators if not x.is_leaf}

        available_gen = set()
        if self.min_depth == 0:
            available_gen.update(leaf_gen)
        if self.max_depth > 0:
            available_gen.update(non_leaf_gen)

        if len(available_gen) == 0:
            available_gen = self._generators

        self._gen_chances = {x: kwargs.get(x.chance_kw, 1.0) for x in available_gen}

    @property
    def child(self) -> Rsg:
        if self._child is None:
            self._child = copy.copy(self)
            self._child.min_depth = max(0, self.min_depth - 1)
            self._child.max_depth = max(0, self.max_depth - 1)
        return self._child

    def _generate_child(self) -> Any:
        return next(self.child)

    def _generate_children(self) -> list[Any]:
        n = randint(self.min_breadth, self.max_breadth)
        n = n if self.max_depth > 0 else 0
        res = [self._generate_child() for _ in range(n)]
        return res

    def generate(self) -> Any:
        fns, probs = list(zip(*[(k, v) for k, v in self._gen_chances.items()]))
        fn = choices(fns, probs)[0]
        return fn(self)

    def __next__(self) -> Any:
        return self.generate()


class RsgStr(Rsg):
    @generator("str", is_leaf=True)
    def _generate_str(self, min_str_len: int = 4, max_str_len: int = 10) -> str:
        n = randint(min_str_len, max_str_len)
        charset = string.ascii_letters + string.digits + string.punctuation
        return "".join(choices(charset, k=n))


class RsgFloat(Rsg):
    @generator("float", is_leaf=True)
    def _generate_float(self, max_float_val: float = 1000.0) -> float:
        return random() * max_float_val


class RsgInt(Rsg):
    @generator("int", is_leaf=True)
    def _generate_int(self, max_int_val: int = 1000) -> int:
        return randint(0, max_int_val)


class RsgDict(Rsg):
    @generator("dict")
    def _generate_dict(self, min_key_len: int = 4, max_key_len: int = 10) -> dict:
        def _generate_key() -> str:
            n = randint(min_key_len, max_key_len)
            charset = string.ascii_letters + string.digits + "_"
            return choice(string.ascii_letters) + "".join(choices(charset, k=n - 1))

        return {_generate_key(): x for x in self._generate_children()}


class RsgList(Rsg):
    @generator("list")
    def _generate_list(self) -> list:
        return self._generate_children()


class RsgTuple(Rsg):
    @generator("tuple")
    def _generate_tuple(self) -> tuple:
        return tuple(self._generate_children())


class RsgBase(RsgInt, RsgFloat, RsgStr, RsgDict, RsgList, RsgTuple):
    pass
