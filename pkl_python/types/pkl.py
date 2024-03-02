from __future__ import annotations
from typing import Any, Dict, List, Tuple, Union, Set, TypeAlias
from enum import Enum

# BaseObject is the Python representation of `pkl.base#Object`.
BaseObject: TypeAlias = Dict[str, PklAny]


# Dynamic is the Python representation of `pkl.base#Dynamic`.
class Dynamic:
    # object properties
    properties: Dict[str, PklAny]
    entries: Dict[Any, PklAny]
    elements: List[PklAny]


class DataSizeUnit(Enum):
    B = "b"
    KB = "kb"
    KIB = "kib"
    MB = "mb"
    MIB = "mib"
    GB = "gb"
    GIB = "gib"
    TB = "tb"
    TIB = "tib"
    PB = "pb"
    PIB = "pib"


# DataSize is the Python representation of `pkl.base#DataSize`.
#
# It represents a quantity of binary data, represented by value (e.g. 30.5) and unit
# (e.g. mb).
class DataSize:
    # value is the value of this data size.
    value: float

    # unit is the unit of this data size.
    unit: DataSizeUnit


class DurationUnit(Enum):
    NS = "ns"
    US = "us"
    MS = "ms"
    S = "s"
    MIN = "min"
    HOUR = "hour"
    D = "d"


# Duration is the Python representation of `pkl.base#Duration`.
#
# It represents an amount of time, represented by value (e.g. 30.5) and unit
# (e.g. s).
class Duration:
    # value is the value of this duration.
    value: float

    # unit is the unit of this duration.
    unit: DurationUnit


# IntSeq is the Python representation of `pkl.base#IntSeq`.
#
# This value exists for compatibility. IntSeq should preferrably be used as a way to describe
# logic within a Pkl program, and not passed as data between Pkl and Python.
class IntSeq:
    # start is the start of this seqeunce.
    start: int

    # end is the end of this seqeunce.
    end: int

    # step is the common difference of successive members of this sequence.
    step: int


# Regex is the Python representation of `pkl.base#Regex`.
class Regex:
    # pattern is the regex pattern expression in string form.
    pattern: str


# Pair is the Python representation of `pkl.base#Pair`.
Pair: TypeAlias = Tuple[Any, PklAny]

AnyObject: TypeAlias = Union[
    BaseObject,
    Dynamic,
    Dict[Any, PklAny],
    List[PklAny],
    Set[PklAny],
    Duration,
    DataSize,
    Pair,
    IntSeq,
    Regex,
    Dict,
]

PklAny: TypeAlias = Union[None, AnyObject, Dict[PklAny, PklAny], str, int, bool]
