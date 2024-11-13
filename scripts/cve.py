#! /usr/bin/env python3

from dataclasses import dataclass
from datetime import datetime, UTC
from functools import cached_property, lru_cache
from json import load as json_load
from pathlib import Path
from time import gmtime
from typing import Self

import logging
import re

log = logging.getLogger(__name__)

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


def path_datetime(p: Path) -> datetime:
    mtime = p.stat().st_mtime
    ms = 1000 * (mtime - int(mtime))
    t = gmtime(mtime)
    return datetime(
        t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec, int(ms), UTC
    )


@dataclass(slots=True)
class CacheEntry:
    time: datetime
    data: Entry | None = None


class DiskCache:
    __path: Path

    def __init__(self, path: Path):
        self.__path = path.absolute()
        if self.__path.exists():
            assert self.__path.is_dir()
        else:
            self.__path.mkdir(parents=True, exist_ok=True)
        self._data = None

    def get_json_path(self, cve_id: Id) -> Path:
        return self.__path / str(cve_id.year) / f"{cve_id!s}.json"

    def get(self, cve_id: Id | str) -> None | Entry:
        if isinstance(cve_id, str):
            cve_id = Id.parse(cve_id)
        assert isinstance(cve_id, Id)
        entry = self.get_entry(cve_id)
        return None if entry is None else entry.data

    def get_entry(self, cve_id: Id) -> None | CacheEntry:
        json_path = self.get_json_path(cve_id)
        if json_path.is_file() or self.materialize_file(cve_id, json_path):
            with json_path.open() as fp:
                json_data = json_load(fp)
            if json_data.get("dataType", None) != "CVE_RECORD":
                return None
            if json_data.get("dataVersion", None) != "5.1":
                return None
            return CacheEntry(data=Entry(json_data), time=path_datetime(json_path))
        return None

    def materialize_file(self, cve_id: Id, json_path: Path) -> bool:
        return False


class DiskFetcherCache(DiskCache):
    __base_url: str = "https://cveawg.mitre.org/api/cve/{cve_id}"

    def __init__(self, path: Path, base_url: str = None):
        super().__init__(path)
        if base_url is not None:
            self.__base_url = base_url

    def materialize_file(self, cve_id: Id, json_path: Path) -> bool:
        from urllib.error import HTTPError
        from urllib.request import urlopen

        json_url = self.__base_url.format(cve_id=cve_id)
        log.info("%s, fetching: %s", cve_id, json_url)

        try:
            response = urlopen(json_url)
        except HTTPError as err:
            log.debug("%s, exception: %s", cve_id, err)
            if err.status == 404:
                return False
            else:
                raise

        content_encoding = response.getheader("content-encoding")
        if content_encoding:
            content_encoding = content_encoding.lower()
            log.debug("%s, content encoding: %s", cve_id, content_encoding)
            if content_encoding in ("gzip", "x-gzip"):
                from gzip import GzipFile

                response = GzipFile(fileobj=response)

        temp_path = json_path.with_suffix(".fetch")
        temp_dir = temp_path.parent
        try:
            temp_dir.mkdir(exist_ok=True)
        except Exception as e:
            log.error("%s, cannot mkdir '%s': %s", cve_id, temp_dir, e)
            raise

        try:
            with temp_path.open("wb") as fp:
                while data := response.read(1024):
                    fp.write(data)
        except Exception as e:
            log.error("%s, cannot write '%s': %s", cve_id, temp_path, e)
            raise

        log.debug("%s, saved: %s", cve_id, json_path)
        temp_path.rename(json_path)
        return True


class LRUMemDiskFetcherCache(DiskFetcherCache):
    @lru_cache
    def get_entry(self, cve_id: Id) -> None | CacheEntry:
        return super().get_entry(cve_id)

    def cache_info(self):
        return self.get_entry.cache_info()

    def cache_clear(self):
        self.get_entry.cache_clear()


__all__ = [
    "is_valid_id",
    "parse_id",
    "unparse_id",
    "Id",
    "Entry",
    "CacheEntry",
    "DiskCache",
    "DiskFetcherCache",
    "LRUMemDiskFetcherCache",
]


if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.DEBUG)
    cve_id = Id.parse(sys.argv[1])
    cc = LRUMemDiskFetcherCache(Path(__file__).parent / "cve")
    cve = cc.get(cve_id)
    if cve:
        print(f"{cve.identifier}: {cve.description}")
    raise SystemExit(1)
