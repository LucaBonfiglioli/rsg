from __future__ import annotations

import inspect
import string
from abc import ABCMeta
from random import choice, choices, randint, random
from typing import Any, Callable, Iterable

from rsg.utils.helpers import inspect_signature, make_attrs

_gen_meth_t = Callable[[], Any]


class _GeneratorFn:
    """Private class used to decorate a generator method, can be invoked without
    arguments, the argument required by the original method are automatically filled
    with the proper values.
    """

    CHILDREN_ARG = "children"

    def __init__(
        self,
        name: str,
        is_leaf: bool,
        method: _gen_meth_t,
        argnames: list[str],
        kwargnames: dict[str, Any],
        default_chance: float,
    ) -> None:
        """Constructor for `_GeneratorFN`.

        Args:
            name (str): Name of the generator method, this name is used to dynamically
            add arguments to the Rsg constructor.
            is_leaf (bool): True if the outputs of this method are leaf.
            method (_gen_meth_t): The method to wrap.
            argnames (list[str]): The names of all positional arguments.
            kwargnames (dict[str, Any]): The names and default value of all keyword
            arguments.
        """
        make_attrs(self, locals(), private=True)

    @property
    def name(self) -> str:
        """The name of this method."""
        return self._name

    @property
    def is_leaf(self) -> bool:
        """Leaf/Non-Leaf boolean value."""
        return self._is_leaf

    @property
    def chance_kw(self) -> str:
        """The name of the keyword argument that controls the chance of this generator
        method."""
        return f"{self.name}_chance"

    @property
    def default_chance(self) -> float:
        """The default chance associated to this method"""
        return self._default_chance

    def __call__(self, caller: Rsg) -> Any:
        args = [getattr(caller, x) for x in self._argnames]
        kwargs = {k: getattr(caller, k, v) for k, v in self._kwargnames.items()}

        if not self.is_leaf:
            kwargs[self.CHILDREN_ARG] = caller._generate_children()

        return self._method(caller, *args, **kwargs)

    def __repr__(self) -> str:  # pragma: no cover
        return f"GeneratorFn({self.name}, {self._method.__name__})"

    def __hash__(self) -> int:
        return hash(self.name)


class _GeneratorFnFactory:
    """Factory for `_GeneratorFn`."""

    @classmethod
    def create(
        cls, name: str, fn: Callable, default_chance: float = 1.0
    ) -> _GeneratorFn:
        """Creates a `_GeneratorFn` from a name and a callable method.

        Args:
            name (str): Custom name of the method.
            fn (Callable): Method to decorate.
            default_chance (float, optional): Default chance for this generator,
            defaults to 1.0

        Returns:
            _GeneratorFn: The decorated method as a `_GeneratorFn` instance.
        """
        args, kwargs = inspect_signature(fn)
        args.pop(0)
        is_leaf = _GeneratorFn.CHILDREN_ARG not in args
        if not is_leaf:
            args.remove(_GeneratorFn.CHILDREN_ARG)
        return _GeneratorFn(name, is_leaf, fn, args, kwargs, default_chance)


def generator(
    name: str, default_chance: float = 1.0
) -> Callable[[Callable], _GeneratorFn]:
    """Decorator for generator methods. Any method decorated with this function is
    added to a pool of generators and automatically invoked with the right arguments.

    See `Rsg` documentation for more info.

    Args:
        name (str): The custom name of the method
        default_chance (float, optional): Default chance for this generator, defaults to
        1.0

    Returns:
        Callable[[Callable], _GeneratorFn]: Decorator function.
    """

    def _wrapped(fn: Callable) -> _GeneratorFn:
        return _GeneratorFnFactory.create(name, fn, default_chance=default_chance)

    return _wrapped


class RsgMeta(ABCMeta):
    """Metaclass that inspects members to find all `_GeneratorFn` instances and adds
    them to a class attribute.
    """

    def __init__(self, name, bases, namespace) -> None:
        super().__init__(name, bases, namespace)
        gen = inspect.getmembers(self, predicate=lambda x: isinstance(x, _GeneratorFn))
        self._generators_map: dict[str, _GeneratorFn] = {v.name: v for _, v in gen}


class Rsg(metaclass=RsgMeta):
    """Base class for all Generators. Provides functionalities to recursively generate
    custom data structures with custom breadth, depth and fully customizable logic.

    Example:
        Let's make a random generator for powers of a number::

            class RandomPower(Rsg):
                @generator("power")
                def random_powers(self, base: int, exp_max: int):
                    exp = random.randint(0, exp_max)
                    return base**exp

        Here, the method `random_powers` takes two inputs: `base` and
        `exp_max`. After decorating the method with `@generator("power")`, we can pass
        these parameters directly in the class constructor::

            gen = RandomPower(base=2, exp_max=10)
            [next(gen) for _ in range(5)]

            >>> [1, 512, 4, 64, 16]

        Let's complicate things, by creating a generator of nested lists containing
        random powers, starting from the previous example::

            class NestedRandomPowers(RandomPower):
                @generator("list")
                def random_lists(self, children):
                    return list(children)

        Here, the method `random_lists` takes an argument named `children` which is
        a reseved argument that contains an iterable of random children objects.
        The function simply converts the iterator to a list and returns it.

        The number of generated children and the structure depth can be customized with
        `Rsg` base class parameters which are inherited by all subclasses::

            gen = NestedRandomPowers(
                min_depth=2,
                max_depth=3,
                min_breadth=2,
                max_breadth=5,
                base=2,
                exp_max=10,
            )
            next(gen)

            >>> [[16, [64, 16, 1, 256]], [128, [64, 32]], [[256, 128, 8, 2], [1, 8]]]

        When having more than one generator method you can set a custom random
        probability for each of them, by setting the `<METHOD_NAME>_chance` keyword
        argument to a custom float. All these probabilities are normalized internally
        so you don't have to do it on your own::

            gen = NestedRandomPowers(
                base=2,
                exp_max=10,
                list_chance=0.75,
                power_chance=0.25,
            )

        You can combine more Generators into one with multiple inheritance::

            from rsg.core import RsgInt, RsgFloat, RsgStr

            ValueGenerator(IntRsg, FloatRsg, StrRsg):
                pass

            gen = ValueGenerator(int_chance=1, float_chance=0.5, str_chance=0.2)
            [next(gen) for _ in range(10)]

            >>> [413, 'U(II9_|>@<', 0.05976, 483, 153, 'A36WAEKM', 209, 633, 444, 754]


    """

    @classmethod
    @property
    def _generators(cls) -> set[_GeneratorFn]:
        return set(cls._generators_map.values())

    def __init__(
        self,
        min_depth: int = 0,
        max_depth: int = 1,
        min_breadth: int = 0,
        max_breadth: int = 1,
        **kwargs,
    ) -> None:
        """Constructor for `Rsg`

        Args:
            min_depth (int, optional): Minimum structure depth, ignored if no recursive
            generator is available. Defaults to 0.
            max_depth (int, optional): Maximum structure depth. Defaults to 1.
            min_breadth (int, optional): Minimum number of children. Ignored if maximum
            depth is 0. Defaults to 0.
            max_breadth (int, optional): Maximum number of children. Defaults to 1.
        """
        make_attrs(self, locals())
        self._kwargs = kwargs
        self._child = None

        if len(self._generators) == 0:
            gen = _GeneratorFnFactory.create("default", (lambda self: None))
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

        self._gen_chances = {
            x: kwargs.get(x.chance_kw, x.default_chance) for x in available_gen
        }

    @property
    def child(self) -> Rsg:
        """Returns a copy of this `Rsg` with min and max depth reduced by one.

        Returns:
            Rsg: The child `Rsg`
        """
        if self._child is None:
            self._child = self.__class__(
                min_depth=max(0, self.min_depth - 1),
                max_depth=max(0, self.max_depth - 1),
                min_breadth=self.min_breadth,
                max_breadth=self.max_breadth,
                **self._kwargs,
            )
        return self._child

    def _generate_children(self) -> Iterable[Any]:
        """Generate a random amount of children objects using the child rsg.

        Returns:
            Iterable[Any]: An iterable of children objects
        """
        n = randint(self.min_breadth, self.max_breadth)
        n = n if self.max_depth > 0 else 0
        res = [next(self.child) for _ in range(n)]
        return res

    def generate(self) -> Any:
        """Generate a random object

        Returns:
            Any: The generated object
        """
        fns, probs = list(zip(*[(k, v) for k, v in self._gen_chances.items()]))
        fn = choices(fns, probs)[0]
        return fn(self)

    def __next__(self) -> Any:
        """Alias for `generate`"""
        return self.generate()


class RsgStr(Rsg):
    """Rsg for random strings of letters, digits and punctuations

    Args:
        min_str_len (int, optional): Minimum string length. Defaults to 4.
        max_str_len (int, optional): Maximum string length. Defaults to 10.
    """

    @generator("str")
    def _generate_str(self, min_str_len: int = 4, max_str_len: int = 10) -> str:
        n = randint(min_str_len, max_str_len)
        charset = string.ascii_letters + string.digits + string.punctuation
        return "".join(choices(charset, k=n))


class RsgFloat(Rsg):
    """Rsg for random floats

    Args:
        max_float_val (float, optional): Maximum float value. Defaults to 1.0
    """

    @generator("float")
    def _generate_float(self, max_float_val: float = 1.0) -> float:
        return random() * max_float_val


class RsgInt(Rsg):
    """Rsg for random integers

    Args:
        max_int_val (int, optional): Maximum integer value. Defaults to 1000
    """

    @generator("int")
    def _generate_int(self, max_int_val: int = 1000) -> int:
        return randint(0, max_int_val)


class RsgDict(Rsg):
    """Rsg for random dictionaries, keys are valid python identifiers.

    Args:
        min_key_len (int, optional): Minimum key length. Defaults to 4.
        max_key_len (int, optional): Maximum key length. Defaults to 10.
    """

    @generator("dict")
    def _generate_dict(
        self, children: Iterable[Any], min_key_len: int = 4, max_key_len: int = 10
    ) -> dict:
        def _generate_key() -> str:
            n = randint(min_key_len, max_key_len)
            charset = string.ascii_letters + string.digits + "_"
            return choice(string.ascii_letters) + "".join(choices(charset, k=n - 1))

        return {_generate_key(): x for x in children}


class RsgList(Rsg):
    """Rsg for random lists."""

    @generator("list")
    def _generate_list(self, children: Iterable[Any]) -> list:
        return list(children)


class RsgTuple(Rsg):
    """Rsg for random tuples."""

    @generator("tuple")
    def _generate_tuple(self, children: Iterable[Any]) -> tuple:
        return tuple(children)


class RsgBase(RsgInt, RsgFloat, RsgStr, RsgDict, RsgList, RsgTuple):
    """Rsg for random built-in objects."""

    pass
