# SPDX-License-Identifier: MIT

from base64 import b32hexencode
from dataclasses import asdict, dataclass, field, fields
from datetime import datetime, UTC
from email.utils import format_datetime, parsedate_to_datetime
from hashlib import sha256
from logging import getLogger
from pathlib import Path
from ruamel.yaml import YAML
from tempfile import NamedTemporaryFile
from typing import Any, Self
from urllib.error import HTTPError
from urllib.request import urlopen, Request


log = getLogger(__name__)


@dataclass(slots=True)
class CacheEntry:
    __YAML = YAML(typ="safe")

    __TIME_DEFAULT = datetime(1970, 1, 1, 0, 0, 0, 0, UTC)

    url: str
    blob: str | None = None
    etag: str | None = None
    type: str | None = None
    size: int | None = None
    expires: datetime | None = None
    mtime: datetime = __TIME_DEFAULT
    data: dict[str, Any] = field(default_factory=dict)

    def __get_http_expires(self) -> str:
        if self.expires is None:
            raise ValueError("Cannot format None expires value")
        return format_datetime(self.expires, usegmt=True)

    def __set_http_expires(self, value: str | None):
        value = value.strip()
        if value and value not in ("0", "-1"):
            self.expires = parsedate_to_datetime(value)
        else:
            self.expires = None

    http_expires = property(__get_http_expires, __set_http_expires)

    def __get_http_mtime(self) -> str:
        return format_datetime(self.mtime, usegmt=True)

    def __set_http_mtime(self, value: str | None):
        if value:
            self.mtime = parsedate_to_datetime(value)
        else:
            self.mtime = self.__TIME_DEFAULT

    http_mtime = property(__get_http_mtime, __set_http_mtime)

    def get_blob_path(self, base_path: Path) -> Path:
        if not self.blob:
            meta_path = self.get_meta_path(base_path)
            if meta_path.is_file():
                self.__load(meta_path)
            if not self.blob:
                raise ValueError("No 'blob' name set")
        return base_path / f"B:{self.blob}"

    def open_blob(self, base_path: Path, mode="r"):
        return self.get_blob_path(base_path).open(mode + "b")

    @classmethod
    def for_url(cls, base_path: Path, url: str) -> Self:
        entry = cls(url=url)
        entry.load(base_path)
        return entry

    @staticmethod
    def get_url_meta_path(base_path: Path, url: str) -> Path:
        encoded_url = b32hexencode(url.encode("ascii")).decode("ascii")
        return base_path / f"M:{encoded_url}"

    def get_meta_path(self, base_path: Path) -> Path:
        return self.get_url_meta_path(base_path, self.url)

    def load(self, base_path: Path) -> bool:
        meta_path = self.get_meta_path(base_path)
        if meta_path.is_file():
            self.__load(meta_path)
            return True
        return False

    def save(self, base_path: Path):
        self.__save(self.get_meta_path(base_path))

    def __load(self, meta_path: Path):
        with meta_path.open("r") as f:
            data = self.__YAML.load(f)
        if data["url"] != self.url:
            raise RuntimeError(f"Inconsitent URL in cache entry:\n "
                f"- Expected: {self.url}\n - Found: {data['url']}")
        for f in fields(self):
            if f.name == "url":
                continue
            if f.name in data:
                setattr(self, f.name, data[f.name])

    def __save(self, meta_path: Path):
        with meta_path.open("w") as f:
            self.__YAML.dump(asdict(self), f)


@dataclass(slots=True)
class Stats:
    misses: int = 0
    errors: int = 0
    hits_local: int = 0
    hits_remote: int = 0

    bytes_remote: int = 0
    bytes_local: int = 0

    @property
    def hits(self):
        return self.hits_local + self.hits_remote

    @property
    def all(self):
        return self.hits + self.misses + self.errors


class HTTPCache:
    __path: Path
    stats: Stats

    def __init__(self, path: Path) -> None:
        self.__path = path.absolute()
        if self.__path.exists():
            assert self.__path.is_dir()
        else:
            self.__path.mkdir(parents=True, exist_ok=True)
        self.stats = Stats()

    def read_blob(self, entry: CacheEntry) -> bytes:
        return entry.get_blob_path(self.__path).read_bytes()

    def get(self, url: str) -> tuple[CacheEntry, bool]:
        entry = CacheEntry.for_url(self.__path, url)
        return (entry, self.__fetch(entry))

    def __fetch(self, entry: CacheEntry) -> bool:
        log.debug("fetch: %s", entry.url)
        request = Request(entry.url)

        blob_path = None
        if entry.blob:
            blob_path = entry.get_blob_path(self.__path)
            if blob_path.is_file():
                if entry.expires and entry.expires > datetime.now(tz=UTC):
                    if entry.size:
                        self.stats.bytes_local += entry.size
                    self.stats.hits_local += 1
                    return True

                if entry.mtime is not None:
                    log.debug("fetch:  - Last-Modified-Since: %s", entry.http_mtime)
                    request.add_header("If-Modified-Since", entry.http_mtime)
                if entry.etag is not None:
                    log.debug("fetch:  - If-None-Match: %s", entry.etag)
                    request.add_header("If-None-Match", entry.etag)

        try:
            response = urlopen(request)
        except HTTPError as e:
            if e.status == 304:  # Not Modified
                log.debug("fetch: ** Cache hit: 304 - Not Modified")
                if entry.size:
                    self.stats.bytes_local += entry.size
                self.stats.hits_remote += 1
                return True
            self.stats.errors += 1
            raise

        log.debug("fetch: ** Cache miss: %d" % response.status)

        entry.http_expires = response.headers.get("Expires", "0")
        entry.http_mtime = response.headers.get("Last-Modified")
        entry.size = int(response.headers.get("Content-Length", 0))
        entry.type = response.headers.get("Content-Type")
        entry.etag = response.headers.get("ETag")
        log.debug("fetch:  - Last-Modified: %s", entry.http_mtime)
        log.debug("fetch:  - Expires: %s", entry.http_expires if entry.expires else None)
        log.debug("fetch:  - Content-Length: %r", entry.size)
        log.debug("fetch:  - Content-Type: %s", entry.type or "")
        log.debug("fetch:  - ETag: %s", entry.etag or "")

        dl_blob = sha256()
        dl_file = NamedTemporaryFile("wb+", prefix="T:", dir=self.__path)
        dl_size = 0
        while data := response.read(1024):
            dl_size += len(data)
            dl_blob.update(data)
            dl_file.write(data)

        if not entry.size:
            entry.size = dl_size

        # Data fetched, link and rename temporary file.
        entry.blob = str(dl_blob.hexdigest())
        log.debug("fetch: ** Saved blob %s", entry.blob)

        blob_path = entry.get_blob_path(self.__path)
        blob_path.unlink(missing_ok=True)
        blob_path.hardlink_to(dl_file.name)
        dl_file.close()

        entry.save(self.__path)

        self.stats.bytes_remote += entry.size
        self.stats.misses += 1
        return False


__all__ = [
    "HTTPCache",
]
