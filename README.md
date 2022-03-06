# RSG - Random Struct Generator

**Rsg** is a tool that helps creating randomly generated nested data structures, from 
simple built-in structures as lists, dictionaries and tuples, to custom composite class 
hierarchies. 

In its current state, this library is merely a toy project with a few basic utilities,
created with the intent of experimenting with python decorators and language inspection.
It was originally a function that generated random yaml files for testing purposes, 
that quickly grew to become a generic subpackage that had no dependencies and could be
exported as a separate python package. 

## Basics

Generators are subclasses of `Rsg` with special "generator" methods:

```python
class RsgFooBar(Rsg):
    @generator("foo")
    def generate_foo(self):
        return "foo"

    @generator("bar")
    def generate_bar(self):
        return "bar"
```

This class genertes either `"foo"` or `"bar"` with equal chance:

```python
rsg = RsgFooBar()
[print(next(rsg)) for _ in range(10)]
# bar foo foo bar foo foo bar bar foo foo
```

You can set a custom chance for each generator method, by setting the keyword agument
named `<METHOD_NAME>_chance` in the object constructor. Probabilities are normalized
automatically, so you don't need to ensure they sum up to one.

```python
rsg = RsgFooBar(foo_chance=0.8, bar_chance=0.2)
[print(next(rsg)) for _ in range(10)]
# foo foo bar foo foo foo foo foo foo bar
```

Chances values all default to 1.0, you can set a custom default value when decorating
a generator method. Default values are used only when a chance value is not specified
in the object constructor.

```python
@generator("foo", default_chance=0.2)
```

## Parameters

What if a generator method needs parameters? In this example we want to make a generator
of random powers of a number (a parameter), with the maximum exponent bounded by anohter
parameter.

To do so, just add any amount of parameters to a generator method, you can use both
positional and keyword arguments, without the need to implement a custom constructor
for your class.

```python
class RsgPowers(Rsg):
    @generator("power")
    def generate_power(self, base: int, max_exp: int = 5):
        exp = randint(0, max_exp)
        return base**exp
```

To set the declared parameters, just pass them to the class constructor, as if you had
actually implemented it!

```python
rsg = RsgPowers(base=2, max_exp=10)
[print(next(rsg)) for _ in range(10)]
# 512 1024 16 128 32 1024 64 8 8 1
```

In the previous example, the parameter `max_exp` has a default value of `5`, this means
that you don't have to explicitly set it in the object constructor. On the other hand,
the `base` parameter doesn't have a default value, and so it must be set explicitly.

## Composite Structures

A generator method can be of two types: 
- Leaf - Objects with no children, like the ones used so far.
- Composite - Objects with randomly generated children, which in turn can have children recursively.

Let's make a generator of lists-of-lists-of-lists-of-l...

```python
class RsgList(Rsg):
    @generator("list")
    def generate_list(self, children: Iterable[Any]) -> list:
        return list(children)
```

To make it recursive, you just need to add an argument named `children` to the method.
This argument will contain an iterable of N randomly generated children objects.
The children objects are generated with the same generator used for the parent object.

Recusion is governed by the following parameters:
- `min_depth` - The minimum number of recursions before a leaf object can be generated.
  Ignored if no composite generators are available.
- `max_depth` - The maximum number of recursions. Must be >= `min_depth`.
- `min_breadth` - The minimum number of children per recursion step. If no leaf 
  generators are available, on the last recursion step `min_breadth` is forced to 0.
- `max_breadth` - The maximum number of children per recursion step.

```python
rsg = RsgList(min_depth=1, max_depth=3, min_breadth=2, max_breadth=4)
print(next(rsg))
# [[[[], []], [[], []], [[], []], [[], []]], [[[], [], [], []], [[], []], [[], []], [[], []]]]
```

## Mixin

You can combine any `Rsg` by simply inheriting from them:

```python
class RsgMixed(RsgFooBar, RsgList, RsgPowers):
    pass
```

You can still set all parameters of the base classes, remember to set the required ones,
or otherwise you will get an `AttributeError`!

```python
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
# [[[9, 243, 'foo', 'bar'], 27, ['foo', 3]], ['foo', [243, 81, 243]], ['foo', 243]]
```

## Built-in Generators

Rsg provides generators for the following built-in types:
- `int` - `rsg.core.RsgInt` generates uniform integer values. 
- `float` - `rsg.core.RsgFloat` generates uniform float values. 
- `str` - `rsg.core.RsgStr` generates random strings containing a uniform random number
  of letters, digits and punctuations. 
- `list` - `rsg.core.RsgList` generates nested lists. 
- `tuple` - `rsg.core.RsgTuple` generates nested tuples. 
- `dict` - `rsg.core.RsgDict` generates nested dicts with valid python identifiers
  as keys.

In addition, `rsg.core.RsgBase` combines all previous generators into one:

```python
from rsg.core import RsgBase

rsg = RsgBase(min_depth=1, max_depth=4, min_breadth=1, max_breadth=3)
print(next(rsg))
# [
#     ((0.73354,), (0.12835, '[^U`zq')),
#     [643, ["QiX0@'", [0.95934, 0.27090, 0.66838]]],
#     [{'N_dHLJUZA': 0.00379, 'D0N0uK1_eH': [667, 0.29715], 'SjWKcs_D': {'IMUUZH': 630}}]
# ]
```