"""Data model and serialization for project metadata."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


def _encode(values: tuple[str, ...]) -> str:
    return ":".join(values)


@dataclass(frozen=True)
class ProjectMetadata:
    root: Path
    subprojects: tuple[str, ...]
    languages: tuple[str, ...]
    environment: str
    version: str
    source: Path
    tests: tuple[str, ...]
    git_directory: Path
    ignored: tuple[str, ...]

    def as_ini_values(self) -> dict[str, str]:
        return {
            "PROJ_ROOT": str(self.root),
            "PROJ_SUBS": _encode(self.subprojects),
            "PROJ_LANGS": _encode(self.languages),
            "PROJ_ENV": self.environment,
            "PROJ_VSN": self.version,
            "PROJ_SRC": str(self.source),
            "PROJ_TEST": _encode(self.tests),
            "PROJ_GITD": str(self.git_directory),
            "PROJ_IGNORE": _encode(self.ignored),
        }

    @property
    def project_directory(self) -> Path:
        return self.root / ".prj" / "config"
