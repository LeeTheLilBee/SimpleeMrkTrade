"""SC033 package-wide destructive-operation regression wall.

This is source static analysis, not provider IAM/Object-Lock certification.
A future deletion feature must be a deliberate separately reviewed protocol,
not an accidental method/call added to Simplee Cloud.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

from simplee_cloud.contracts import CiphertextBackend
from simplee_cloud.local_backend import LocalPrivateCiphertextBackend
from simplee_cloud.s3_backend import S3CompatibleCiphertextBackend
from simplee_cloud.service import CiphertextStorageService
from simplee_cloud.bound_port import SourceOnlyBoundCloudPort


ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_DEFS = {
    "delete", "delete_object", "delete_objects", "remove", "unlink",
    "rmdir", "rmtree", "purge", "erase", "destroy", "wipe",
}
FORBIDDEN_CALLS = {
    "os.remove", "os.unlink", "os.rmdir", "shutil.rmtree",
    "Path.unlink", "Path.rmdir",
    "delete_object", "delete_objects",
}
FORBIDDEN_SQL_PREFIXES = ("delete ", "drop table ", "truncate ")


def production_modules():
    return sorted(
        path for path in ROOT.glob("*.py")
        if path.name != "__init__.py"
    )


def dotted(node):
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
    return ".".join(reversed(parts))


def static_violations(path):
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    violations = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name.lower() in FORBIDDEN_DEFS:
                violations.append((node.lineno, "definition", node.name))
        elif isinstance(node, ast.Call):
            name = dotted(node.func)
            tail = name.rsplit(".", 1)[-1].lower()
            if name in FORBIDDEN_CALLS or tail in FORBIDDEN_DEFS:
                violations.append((node.lineno, "call", name))
            # Block direct SQL destructive mutation in runtime source even if
            # spelled with a sqlite execute call. Append-only trigger DDL such
            # as "BEFORE DELETE" is not a destructive SQL statement.
            if tail in {"execute", "executescript"} and node.args:
                arg = node.args[0]
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    statements = [
                        x.strip().lower()
                        for x in arg.value.split(";") if x.strip()
                    ]
                    for statement in statements:
                        if statement.startswith(FORBIDDEN_SQL_PREFIXES):
                            violations.append(
                                (node.lineno, "destructive_sql", statement[:80])
                            )
    return violations


def test_entire_runtime_package_has_no_destructive_storage_or_database_calls():
    failures = {
        path.name: static_violations(path)
        for path in production_modules()
    }
    failures = {name: items for name, items in failures.items() if items}
    assert failures == {}


@pytest.mark.parametrize("cls", [
    CiphertextBackend,
    LocalPrivateCiphertextBackend,
    S3CompatibleCiphertextBackend,
    CiphertextStorageService,
    SourceOnlyBoundCloudPort,
])
def test_public_storage_contracts_have_no_destructive_method_names(cls):
    methods = {
        name.lower() for name in dir(cls)
        if not name.startswith("__")
    }
    assert not (methods & FORBIDDEN_DEFS)


def test_guard_does_not_mistake_retention_hold_language_for_delete_capability(tmp_path):
    path = tmp_path / "safe.py"
    path.write_text(
        '"""Deletion is NOT authorized."""\n'
        'def retention_delete_status():\n'
        '    return {"provider_delete_authorized": False}\n',
        encoding="utf-8",
    )
    # The helper is a status/report name, not a destructive primitive. Only
    # exact dangerous method names/calls are forbidden.
    assert static_violations(path) == []


@pytest.mark.parametrize("source,expected", [
    ("def delete():\n    pass\n", "definition"),
    ("def f(client):\n    client.delete_object(Bucket='x', Key='y')\n", "call"),
    ("def f(p):\n    p.unlink()\n", "call"),
    ("import os\ndef f(p):\n    os.remove(p)\n", "call"),
    ("def f(db):\n    db.execute('DELETE FROM records')\n", "destructive_sql"),
])
def test_guard_catches_representative_future_destructive_regressions(
    tmp_path, source, expected,
):
    path = tmp_path / "bad.py"
    path.write_text(source, encoding="utf-8")
    violations = static_violations(path)
    assert violations
    assert violations[0][1] == expected
