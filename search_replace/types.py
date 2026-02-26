from dataclasses import dataclass
from enum import StrEnum
from typing import TypeAlias


class BlockKind(StrEnum):
    SEARCH_REPLACE = "search_replace"
    SHELL = "shell"


Fence: TypeAlias = tuple[str, str]
DEFAULT_FENCE: Fence = ("`" * 3, "`" * 3)


@dataclass(frozen=True, slots=True)
class EditBlock:
    path: str
    original: str
    updated: str


@dataclass(frozen=True, slots=True)
class ParseResult:
    edits: list[EditBlock]
    shell_commands: list[str]


@dataclass(frozen=True, slots=True)
class ApplyResult:
    updated_edits: list[EditBlock]
