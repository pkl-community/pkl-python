import msgpack
from typing import Any, Dict, List, Union

# Define the constants
codeObject = 0x1
codeMap = 0x2
codeMapping = 0x3
codeList = 0x4
codeListing = 0x5
codeSet = 0x6
codeDuration = 0x7
codeDataSize = 0x8
codePair = 0x9
codeIntSeq = 0xA
codeRegex = 0xB
codeClass = 0xC
codeTypeAlias = 0xD
codeObjectMemberProperty = 0x10
codeObjectMemberEntry = 0x11
codeObjectMemberElement = 0x12

# Define the types
Code = Union[
    int,
    codeObject,
    codeMap,
    codeMapping,
    codeList,
    codeListing,
    codeSet,
    codeDuration,
    codeDataSize,
    codePair,
    codeIntSeq,
    codeRegex,
    codeClass,
    codeTypeAlias,
    codeObjectMemberProperty,
    codeObjectMemberEntry,
    codeObjectMemberElement,
]


class Decoder:
    def __init__(self):
        self.decoder = msgpack.Unpacker(raw=False)

    def decode(self, bytes: bytes) -> Any:
        self.decoder.feed(bytes)
        return self.decode_any(next(self.decoder))

    def decode_code(self, code: Code, rest: List[Any]) -> Dict[str, Any]:
        if code == codeObject:
            name, module_uri, entries = rest
            if name == "Dynamic" and module_uri == "pkl:base":
                return self.decode_dynamic(entries)
            return self.decode_object(name, module_uri, entries)
        elif code in [codeMap, codeMapping]:
            (map,) = rest
            return self.decode_map(map)
        elif code in [codeList, codeListing]:
            (list,) = rest
            return self.decode_list(list)
        elif code == codeSet:
            (list,) = rest
            return set(self.decode_list(list))
        elif code == codeDuration:
            value, unit = rest
            return {"value": value, "unit": unit}
        elif code == codeDataSize:
            value, unit = rest
            return {"value": value, "unit": unit}
        elif code == codePair:
            first, second = rest
            return [self.decode_any(first), self.decode_any(second)]
        elif code == codeIntSeq:
            start, end, step = rest
            return {"start": start, "end": end, "step": step}
        elif code == codeRegex:
            (pattern,) = rest
            return {"pattern": pattern}
        elif code in [codeClass, codeTypeAlias]:
            return {}
        else:
            raise ValueError(f"encountered unknown object code: {code}")

    def decode_object(
        self, name: str, rest: List[Code]
    ) -> Dict[str, Any]:
        out = {}
        for entry in rest:
            code, *rest = entry
            if code == codeObjectMemberProperty:
                name, value = rest
                out[name] = self.decode_any(value)
            elif code in [codeObjectMemberEntry, codeObjectMemberElement]:
                raise ValueError("Unexpected object member entry in non-Dynamic object")
        return out

    def decode_dynamic(self, rest: List[Code]) -> Dict[str, Any]:
        properties = {}
        entries = {}
        elements = []
        for entry in rest:
            code, *rest = entry
            if code == codeObjectMemberProperty:
                name, value = rest
                if not isinstance(name, str):
                    raise ValueError("object member property keys must be strings")
                properties[name] = self.decode_any(value)
            elif code == codeObjectMemberEntry:
                key, value = rest
                entries[self.decode_any(key)] = self.decode_any(value)
            elif code == codeObjectMemberElement:
                i, value = rest
                if not isinstance(i, int):
                    raise ValueError("object member element indices must be numbers")
                elements.append(self.decode_any(value))
        return {"properties": properties, "entries": entries, "elements": elements}

    def decode_map(self, map: Dict[Any, Any]) -> Dict[Any, Any]:
        return {self.decode_any(k): self.decode_any(v) for k, v in map.items()}

    def decode_list(self, list: List[Any]) -> List[Any]:
        return [self.decode_any(item) for item in list]

    def decode_any(self, value: Any) -> Any:
        if value is None:
            return value
        if isinstance(value, list):
            # object case
            code, *rest = value
            return self.decode_code(code, rest)
        if isinstance(value, dict):
            raise ValueError(
                f"unexpected object {value} provided to decode_any; expected primitive type or list"
            )
        # primitives
        return value
