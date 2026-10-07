#! /usr/bin/env python3

from collections.abc import Iterable
from functools import cached_property
from itertools import batched
from datetime import datetime
from pathlib import Path
import cve
import logging
import sys

log = logging.getLogger(__name__)

_DB_INIT_STATEMENTS = """\
BEGIN;

CREATE TABLE IF NOT EXISTS metadata (
    key TEXT NOT NULL PRIMARY KEY,
    value TEXT DEFAULT NULL,
    type TEXT NOT NULL DEFAULT 'string'
);

INSERT INTO metadata (key, value, type)
VALUES ('db_schema', 0, 'number')
ON CONFLICT (key) DO NOTHING;

COMMIT;
"""


_DB_SCHEMA_V1 = """\
BEGIN;

CREATE TABLE cve (
    cve_id TEXT PRIMARY KEY,
    cve_json JSONB NOT NULL,
    state TEXT AS (json_extract(cve_json, '$.cveMetadata.state')),
    assigner TEXT AS (json_extract(cve_json, '$.cveMetadata.assignerShortName')),
    date_published TIMESTAMP AS (json_extract(cve_json, '$.cveMetadata.datePublished')),
    date_reserved TIMESTAMP AS (json_extract(cve_json, '$.cveMetadata.dateReserved')),
    date_updated TIMESTAMP AS (json_extract(cve_json, '$.cveMetadata.dateUpdated'))
);

CREATE VIEW descriptions AS SELECT
    cve_id,
    value->>'lang' AS lang,
    value->>'value' AS description
FROM
    cve,
    json_each(cve.cve_json, '$.containers.cna.descriptions');

CREATE VIEW problems AS SELECT
    cve_id,
    value->>'lang' AS lang,
    value->>'description' AS description
FROM (
    SELECT
        cve_id,
        value->'$' AS descriptions
    FROM
        cve,
        json_each(cve_json, '$.containers.cna.problemTypes')
), json_each(descs, '$.descriptions');

CREATE VIEW credits AS SELECT
    cve_id,
    value->>'type' AS type,
    value->>'value' AS credit
FROM
    cve,
    json_each(cve.cve_json, '$.containers.cna.credits');

COMMIT;
"""


class GitCloneHelper:
    """
    Used to run Git commands in a checkout of the CVE list repository.

    The methods in this class ensure that the Git commands are run with a
    known configuration: reading global and user configuration files disabled,
    the needed environment variables pre-set in the environment, and the work
    directory set to the top level path of the checkout.
    """
    def __init__(self, database, clone_path: Path):
        self.__database = database
        self.__path = clone_path.resolve()
        if not self.__path.is_dir():
            raise ValueError(f"Not a directory: {self.__path}")
        self.__gitdir = self.__path / ".git"
        if not self.__gitdir.exists():
            raise ValueError(f"Git directory missing: {self.__gitdir}")

    @property
    def path(self) -> Path:
        """
        Path to the Git repository checkout.
        """
        return self.__path

    @cached_property
    def checkout_commit(self) -> str:
        """
        Commit hash of the HEAD commit of the Git repository checkout.
        """
        return self.get_git_output("rev-parse", "@").strip()

    @cached_property
    def pristine_checkout(self):
        """
        Whether the Git checkout is in a clean, pristine state.

        This will return `True` even if there are untracked and unknown files;
        as long as there are no modifications (either staged or unstaged) to
        tracked files.
        """
        for _ in filter(lambda s: s[:2] not in ("!!", "??"),
                self.get_git_nullsep_output("status", "--porcelain", "-z")):
            return False
        return True

    @cached_property
    def git_command_environment(self) -> dict[str, str]:
        """
        Dictionary of environment variables to used with Git commands.
        """
        from os import environ, getcwd
        git_environ = {
            "GIT_ADVICE": "0",
            "GIT_CONFIG_GLOBAL": "/dev/null",
            "GIT_DIR": str(self.__gitdir),
            "GIT_NO_LAZY_FETCH": "1",
            "GIT_TERMINAL_PROMPT": "false",
            "OLDPWD": getcwd(),
            "PWD": str(self.__path),
        }
        allowed_env_vars = ("HOME", "PATH", "XDG_CONFIG_HOME",
                "XDG_CACHE_HOME", "XDG_DATA_HOME", "XDG_STATE_HOME",
                "XDG_RUNTIME_DIR", "XDG_DATA_DIRS", "XDG_CONFIG_DIRS",
                "GIT_TRACE")
        for name, value in environ.items():
            if name in allowed_env_vars or name.startswith("GIT_TRACE_"):
                git_environ[name] = value
        return git_environ

    def run_git(self, *command, output=False):
        """
        Run a Git command.

        :param command: Arguments to the ``git`` program.
        :param output: Whether to capture the output of the program.
        """
        import subprocess
        git_command = ["git", "--no-pager"]
        git_command.extend(command)
        return subprocess.run(git_command, cwd=self.__path, check=True,
                env=self.git_command_environment,
                stdout=(subprocess.PIPE if output else subprocess.DEVNULL))

    def get_git_output(self, *command):
        """
        Run a Git command, returning its output.

        :param command: Arguments to the ``git`` program.
        """
        return self.run_git(*command, output=True).stdout.decode("utf-8")

    def get_git_nullsep_output(self, *command):
        """
        Run a Git command, capture its output, and split it in null-delimited entries.

        :param command: Arguments to the ``git`` program.
        """
        text = self.get_git_output(*command)
        if text.endswith("\0"):
            text = text[:-1]
        return text.split("\0")


class Database:
    """
    Holds a connection to the CVE database and provides utility methods.

    SQLite is used unconditionally.
    """
    def __init__(self, database_path: Path, initialize: bool|None = None):
        """
        Initialize the database.

        :param database_path: path to the SQLite database.
        :para initialize: whether to initialize the SQLite database.
        """
        import sqlite3
        self.__path = database_path
        if initialize is None:
            initialize = not database_path.exists()
        self.connection = sqlite3.connect(database_path)
        self.log_debug("opened %r", self.connection)
        if initialize:
            self.initialize()

    def log_debug(self, fmt, *arg, **kw):
        """
        Log a message with severity 'DEBUG', prefixing it with the database
        path. Uses `logging.Logger.debug()` under the hood.
        """
        log.debug("%s: " + fmt, self.__path, *arg, **kw)

    def log_warning(self, fmt, *arg, **kw):
        """
        Log a message with severity 'WARNING', prefixing it with the database
        path. Uses `logging.Logger.debug()` under the hood.
        """
        log.warning("%s: " + fmt, self.__path, *arg, *kw)

    def log_info(self, fmt, *arg, **kw):
        """
        Log a message with severity 'INFO', prefixing it with the database
        path. Uses `logging.Logger.debug()` under the hood.
        """
        log.info("%s: " + fmt, self.__path, *arg, **kw)

    def close(self):
        """
        Close the connection to the SQLite database.
        """
        self.connection.close()

    def initialize(self):
        """
        Initialize the database.
        """
        self.connection.executescript(_DB_INIT_STATEMENTS)
        db_schema = self.get_metadata("db_schema")
        self.log_debug("current schema version=%d", db_schema)
        if db_schema > 1:
            raise RuntimeError("only DB schema v1 supported")
        if db_schema == 0:
            self.log_info("creating v1 schema")
            self.connection.executescript(_DB_SCHEMA_V1)
            self.set_metadata("db_schema", 1)

    def insert_many(self, items: Iterable[(str, bytes)]):
        """
        Insert a batch of CVEs in the database.

        :param items: iterable over ``(cve_id, json_text)`` pairs.
        """
        with self.connection:
            self.connection.executemany("""\
                INSERT INTO cve (cve_id, cve_json) VALUES (?, jsonb(?))
                """, items)

    def insert(self, cve_id: str, json_text: bytes):
        """
        Insert a single CVE in the database.

        :param cve_id: CVE identifier.
        :param json_text: CVE data in JSON format.
        """
        self.insert_many(((cve_id, json_text),))

    def update_many(self, items: Iterable[(str, bytes)]):
        """
        Update a batch of CVEs in the database.

        :param items: iterable over ``(cve_id, json_text)`` pairs.
        """
        with self.connection:
            self.connection.executemany("""\
                UPDATE cve SET cve_json = jsonb(?) WHERE cve_id = ?
                """, ((json_text, cve_id) for (cve_id, json_text) in items))

    def update(self, cve_id: str, json_text: bytes):
        """
        Update a single CVE in the database.

        :param cve_id: CVE identifier.
        :param json_text: CVE data in JSON format.
        """
        self.update_many(((cve_id, json_text),))

    def upsert_many(self, items: Iterable[(str, bytes)]):
        """
        Insert or update a batch of CVEs in the database.

        Note that the ``cveMetadata.dateUpdated`` field of the JSON data is
        checked, and the database entry updated only if the update timestamp
        is newer than the one previously stored.

        :param items: iterable over ``(cve_id, json_text)`` pairs.
        """
        with self.connection:
            self.connection.executemany("""\
                INSERT INTO cve (cve_id, cve_json) VALUES (?, jsonb(?))
                ON CONFLICT (cve_id) DO UPDATE SET cve_json = excluded.cve_json
                WHERE date_updated < excluded.date_updated
                """, items)

    def upsert(self, cve_id: str, json_text: bytes):
        """
        Insert or update a single CVE in the database.

        Note that the ``cveMetadata.dateUpdated`` field of the JSON data is
        checked, and the database entry updated only if the update timestamp
        is newer than the one previously stored.

        :param cve_id: CVE identifier.
        :param json_text: CVE data in JSON format.
        """
        self.insert_many(((str, json_text),))

    def list_metadata(self):
        for row in self.connection.execute("SELECT key, type FROM metadata"):
            yield row[0], row[1]

    def delete_metadata(self, key: str):
        with self.connection:
            self.connection.execute("DELETE FROM metadate WHERE key = ?", key)

    def set_metadata(self, key: str, value: str|int|datetime):
        type_string = None
        if isinstance(value, str):
            type_string = 'string'
            value_string = value
        elif isinstance(value, int):
            type_string = 'number'
            value_string = str(value)
        elif isinstance(value, datetime):
            type_string = 'timestamp'
            value_string = value.isoformat()
        else:
            raise ValueError(value)

        with self.connection:
            self.connection.execute("""\
                INSERT INTO metadata (key, value, type) VALUES (?, ?, ?)
                ON CONFLICT (key) DO UPDATE SET value = excluded.value
                """, (key, value_string, type_string))

    def get_metadata(self, key: str) -> str|int|datetime|None:
        cursor = self.connection.execute("""\
            SELECT type, value FROM metadata WHERE key = ?
            """, (key,))

        if not cursor:
            return None
        row = cursor.fetchone()
        if not row:
            return None

        if row[0] == "string":
            return row[1]
        elif row[0] == "number":
            return int(row[1])
        elif row[0] == "timestamp":
            return datetime.fromisoformat(row[1])
        else:
            raise TypeError(key)

    @property
    def meta_git_commit(self) -> str|None:
        return self.get_metadata("git_commit")

    @meta_git_commit.setter
    def meta_git_commit(self, value: str):
        self.set_metadata("git_commit", value)

    @meta_git_commit.deleter
    def meta_git_commit(self):
        self.delete_metadata("git_commit")

    @property
    def meta_git_path(self) -> Path|None:
        path_string = self.get_metadata("git_path")
        if path_string is None:
            return None
        return Path(path_string).resolve()

    @meta_git_path.setter
    def meta_git_path(self, value: Path|str):
        self.set_metadata("git_path", str(Path(value).resolve()))

    @meta_git_path.deleter
    def meta_git_path(self):
        self.delete_metadata("git_path")

    def get_json(self, cve_id: str):
        """
        Get data for a CVE in JSON format.
        """
        return self.connection.execute("""\
            SELECT json(cve_json) AS json FROM cve WHERE cve_id = ?
            """, (cve_id,)).fetchone()[0]

    def get_dict(self, cve_id: str) -> None|dict:
        """
        Get data for a CVE as a dictionary.

        Note that this returns the same data as ``get_json()`` decoded into
        into Python types.
        """
        json_text = self.get_json(cve_id)
        if json_text is None:
            return None
        import json
        return json.loads(json_text)

    def get(self, cve_id: str) -> None|cve.Entry:
        """
        Get data for a CVE.
        """
        # TODO: Query database directly instead of parsing JSON via .get_dict()
        data = self.get_dict(cve_id)
        if data is None:
            return None
        return cve.Entry(data=data)

    def __len__(self):
        """
        Get the number of CVEs in the database.
        """
        if self.get_metadata("db_schema") > 0:
            return self.connection.execute("SELECT count(*) FROM cve").fetchone()[0]
        return 0

    @cached_property
    def git_helper(self):
        meta_source = self.get_metadata("source")
        if meta_source is None:
            self.log_warning("No 'source' metadata, assuming 'git', YMMV.")
        if meta_source != 'git':
            raise RuntimeError(f"Only 'git' source supported, source='{meta_source}'.")
        git_path = self.meta_git_path
        if git_path is None:
            raise RuntimeError(f"Using 'git' source, but no 'git_path' set.")
        return GitCloneHelper(self, git_path)

    def __import(self, import_many, files: Iterable[Path], batch_size=50):
        count = 0
        with self.connection:
            for batch in batched(files, batch_size):
                count += len(batch)
                import_many(((p.stem, p.read_text()) for p in batch))
                self.log_debug("Processed %d files, continuing...", count)
            self.meta_git_commit = self.git_helper.checkout_commit
        self.log_info("Processed %d files, now at %s", count, self.git_helper.checkout_commit)

    def full_import(self):
        self.log_debug("Performing a full import.")
        assert self.meta_git_commit is None
        git_path = self.git_helper.path
        self.__import(self.insert_many, (git_path / p for p in
            self.git_helper.get_git_nullsep_output("ls-files", "-z",
                "--no-empty-directory", "--no-directory",
                "--no-resolve-undo", "--full-name",
                "cves/**/CVE-*.json")))

    def update_import(self, start_commit=None, end_commit=None):
        if start_commit is None:
            start_commit = self.meta_git_commit
        if end_commit is None:
            end_commit = self.git_helper.checkout_commit
        self.log_debug("Import update from %s to %s", start_commit, end_commit)
        git_path = self.git_helper.path
        self.__import(self.upsert_many, (git_path / p for p in
            self.git_helper.get_git_nullsep_output("diff",
                f"{start_commit}..{end_commit}", "-z", "--raw",
                "--name-only", "cves/**/CVE-*.json")))
