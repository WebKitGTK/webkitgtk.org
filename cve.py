#! /usr/bin/env python3

from dataclasses import dataclass
from functools import cached_property
from typing import Self

import re

cve_id_re = re.compile(r"^CVE-(\d+)-(\d+)$")


def is_valid_id(cve_id: str) -> bool:
    """Checks whether a string is a valid CVE identifier."""
    return cve_id_re.match(cve_id) is not None


def parse_id(cve_id: str) -> tuple[int, int]:
    """Parses a CVE identifier string into its components.

    Returns a tuple with the year and serial numbers extracted from the string.
    """
    id_parts_match = cve_id_re.match(cve_id)
    if id_parts_match is None:
        raise ValueError(f"Invalid CVE string: {cve_id!r}")
    return (int(id_parts_match[1]), int(id_parts_match[2]))


def unparse_id(cve_id: tuple[int, int]) -> str:
    """Formats a year in serial number into a CVE identifier."""
    return f"CVE-{cve_id[0]:04}-{cve_id[1]:04}"


@dataclass(frozen=True, slots=True)
class Id:
    """Represents a CVE identifier."""

    year: int
    serial: int

    is_valid = is_valid_id

    @classmethod
    def parse(cls, cve_id: str) -> Self:
        """Parses a CVE identifier string into an identifier."""
        parsed = parse_id(cve_id)
        return cls(year=parsed[0], serial=parsed[1])

    def __str__(self):
        """Represents a CVE identifier as a string."""
        return unparse_id((self.year, self.serial))


class Entry:
    """Convenience class to access CVE JSON data."""

    _data: dict

    def __init__(self, data: dict):
        self._data = data

    @cached_property
    def identifier(self) -> Id:
        """Identifier for the CVE entry."""
        return Id.parse(self._data["cveMetadata"]["cveId"])

    @cached_property
    def published(self):
        """Whether the CVE entry has been published."""
        return self._data["cveMetadata"]["state"] == "PUBLISHED"

    @cached_property
    def description(self) -> None | str:
        """CVE entry description."""
        for container_id, container in self._data.get("containers", {}).items():
            for desc in container.get("descriptions", ()):
                if isinstance(desc, dict) and desc.get("lang", None) in ("en", "eng"):
                    return desc["value"]
        return None


__all__ = [
    "is_valid_id",
    "parse_id",
    "unparse_id",
    "Id",
    "Entry",
]
