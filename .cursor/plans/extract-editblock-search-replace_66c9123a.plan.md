---
name: extract-editblock-search-replace
overview: Build a fully standalone library based on Aider’s editblock SEARCH/REPLACE flow, preserving behavior as exactly as possible while removing Aider runtime coupling. Keep scope to editblock flow only (no udiff/wholefile extraction).
todos:
  - id: freeze-feature-map
    content: Create a frozen inventory doc of editblock entrypoints, symbols, prompts, dependencies, tests, and fixtures as extraction acceptance baseline.
    status: pending
  - id: design-lib-boundary
    content: Define standalone public API and internal module boundaries, with no runtime dependency on Aider classes/lifecycle.
    status: pending
  - id: port-core-parser-applier
    content: Move parser and replacement algorithms into standalone library modules with typed public APIs and preserved semantics.
    status: pending
  - id: port-prompt-assets
    content: Move editblock prompt templates (main/editor/fenced) and shell prompt fragments with placeholder compatibility.
    status: pending
  - id: parity-harness
    content: Build behavior-parity tests against frozen Aider-derived cases so output and error behavior match exactly (or document intentional deviations).
    status: pending
  - id: migrate-and-extend-tests
    content: Port direct tests/fixtures into standalone tests and add focused regressions for fuzzy, malformed-block, and prompt-format edge cases.
    status: pending
isProject: false
---

# Extract Editblock Search/Replace Library

## Confirmed Scope

- Include only editblock flow (`diff` / `editor-diff` family), plus prompts used by that flow.
- Exclude unified-diff and wholefile engines.
- Final artifact is standalone (not invoking Aider runtime/coder classes in production path).
- Preserve behavior/code semantics as close to exact as possible; only adapt where decoupling is required.
- Do not reinvent implementations that already exist in source/stdlib dependencies.

## Current Feature Map (what will be extracted)

### Source-of-truth entry points (for parity mapping)

- CLI/model route into editblock format:
  - [aider/main.py](/home/pycharm/cyber/projects/search_replace_py/aider-main/aider/main.py)
  - [aider/models.py](/home/pycharm/cyber/projects/search_replace_py/aider-main/aider/models.py)
- Coder selection + lifecycle (reference only):
  - [aider/coders/**init**.py](/home/pycharm/cyber/projects/search_replace_py/aider-main/aider/coders/__init__.py)
  - [aider/coders/base_coder.py](/home/pycharm/cyber/projects/search_replace_py/aider-main/aider/coders/base_coder.py)
    - `Coder.create()` picks `edit_format="diff"` coder
    - `apply_updates()` drives `get_edits()` → `apply_edits_dry_run()` → `apply_edits()`
    - `fmt_system_prompt()` and `format_chat_chunks()` inject prompt templates/placeholders

### Core editblock implementation

- Primary module: [aider/coders/editblock_coder.py](/home/pycharm/cyber/projects/search_replace_py/aider-main/aider/coders/editblock_coder.py)
- Class methods to extract:
  - `EditBlockCoder.get_edits`
  - `EditBlockCoder.apply_edits_dry_run`
  - `EditBlockCoder.apply_edits`
- Parser/patch functions to extract:
  - `prep`, `perfect_or_whitespace`, `perfect_replace`, `replace_most_similar_chunk`
  - `try_dotdotdots`
  - `replace_part_with_missing_leading_whitespace`, `match_but_for_leading_whitespace`
  - `replace_closest_edit_distance` (currently unreachable/inactive fallback)
  - `strip_quoted_wrapping`, `do_replace`
  - `strip_filename`, `find_original_update_blocks`, `find_filename`, `find_similar_lines`
  - constants/regex: `HEAD`, `DIVIDER`, `UPDATED`, `split_re`, `missing_filename_err`

### Prompt assets in scope

- Main prompt templates:
  - [aider/coders/editblock_prompts.py](/home/pycharm/cyber/projects/search_replace_py/aider-main/aider/coders/editblock_prompts.py)
  - [aider/coders/editor_editblock_prompts.py](/home/pycharm/cyber/projects/search_replace_py/aider-main/aider/coders/editor_editblock_prompts.py)
  - [aider/coders/editblock_fenced_prompts.py](/home/pycharm/cyber/projects/search_replace_py/aider-main/aider/coders/editblock_fenced_prompts.py)
- Shared prompt dependencies:
  - [aider/coders/base_prompts.py](/home/pycharm/cyber/projects/search_replace_py/aider-main/aider/coders/base_prompts.py)
  - [aider/coders/shell.py](/home/pycharm/cyber/projects/search_replace_py/aider-main/aider/coders/shell.py)
- Prompt consumers:
  - [aider/coders/editblock_coder.py](/home/pycharm/cyber/projects/search_replace_py/aider-main/aider/coders/editblock_coder.py)
  - [aider/coders/editor_editblock_coder.py](/home/pycharm/cyber/projects/search_replace_py/aider-main/aider/coders/editor_editblock_coder.py)
  - [aider/coders/editblock_fenced_coder.py](/home/pycharm/cyber/projects/search_replace_py/aider-main/aider/coders/editblock_fenced_coder.py)

### Dependency map (editblock scope, keep as-is unless required)

- Stdlib/runtime:
  - `difflib` (`SequenceMatcher`, `get_close_matches` for fuzzy matching)
  - `math` (chunk-length windowing for fuzzy distance search)
  - `re` (SEARCH/REPLACE block regex parsing)
  - `pathlib.Path` (filename/path normalization, new-file creation)
  - `sys` (CLI helper in module `main()` only)
- Aider-specific runtime dependencies to remove from production path:
  - `Coder` integration hooks from `base_coder.py`
  - prompt placeholder expansion in `fmt_system_prompt`
  - `utils.split_chat_history_markdown` helper usage in module `main()`
- Third-party runtime dependencies specific to standalone editblock core: none required.

### Fuzzy matching status

- Active fuzzy paths:
  - filename fuzzy resolution in `find_filename()` via `difflib.get_close_matches(..., cutoff=0.8)`
  - mismatch hint generation in `find_similar_lines()` via `SequenceMatcher`
- Inactive fuzzy path:
  - `replace_closest_edit_distance()` exists but is bypassed by early `return` in `replace_most_similar_chunk()`.

```183:188:/home/pycharm/cyber/projects/search_replace_py/aider-main/aider/coders/editblock_coder.py
    return
    # Try fuzzy matching
    res = replace_closest_edit_distance(whole_lines, part, part_lines, replace_lines)
    if res:
        return res
```

### Test and fixture map

- Direct core coverage:
  - [tests/basic/test_editblock.py](/home/pycharm/cyber/projects/search_replace_py/aider-main/tests/basic/test_editblock.py)
  - [tests/basic/test_find_or_blocks.py](/home/pycharm/cyber/projects/search_replace_py/aider-main/tests/basic/test_find_or_blocks.py)
- Integration/selection coverage touching diff path:
  - [tests/basic/test_coder.py](/home/pycharm/cyber/projects/search_replace_py/aider-main/tests/basic/test_coder.py)
  - [tests/basic/test_models.py](/home/pycharm/cyber/projects/search_replace_py/aider-main/tests/basic/test_models.py)
- Fixtures:
  - [tests/fixtures/chat-history.md](/home/pycharm/cyber/projects/search_replace_py/aider-main/tests/fixtures/chat-history.md)
  - [tests/fixtures/chat-history-search-replace-gold.txt](/home/pycharm/cyber/projects/search_replace_py/aider-main/tests/fixtures/chat-history-search-replace-gold.txt)

## Extraction Design (standalone library)

- New library modules (proposed):
  - `search_replace/parser.py` (block parsing, filename resolution)
  - `search_replace/apply.py` (exact/whitespace/dotdotdots replacement)
  - `search_replace/fuzzy.py` (similar-line + optional closest-distance functions)
  - `search_replace/prompts.py` (editblock prompt templates + variants)
  - `search_replace/types.py` (`EditBlock`, parse/apply result DTOs)
  - `search_replace/errors.py` (typed parse/apply errors)
- Standalone API boundary:
  - expose pure parse/apply/prompt APIs that do not require Aider objects.
  - keep filesystem/path operations explicit and injectable where needed.
  - preserve exact parsing/replacement behavior and error-message contracts from source implementation.

## Validation Strategy

- Port/parametrize current direct tests from `test_editblock.py` and `test_find_or_blocks.py` into library tests first.
- Add regression tests for known edge behavior:
  - new-file creation (`SEARCH` empty)
  - multi-block same file
  - shell block extraction (`None` filename path)
  - quadruple-backtick fence behavior
  - fuzzy filename matches and no-match error payload format
- Add parity harness cases that compare standalone outputs/errors against frozen Aider-derived expected outputs.
- Document any unavoidable adaptations introduced by decoupling, with explicit before/after behavior notes.

## Risks to control during extraction

- Prompt placeholder contract drift (`{fence}`, `{final_reminders}`, shell placeholders).
- Behavior drift in malformed block errors (important for model retry loop).
- Accidental activation/deactivation of currently inactive fuzzy replacement branch.
- Hidden coupling to Aider lifecycle (`apply_updates`, coder state, chat chunk assembly) leaking into standalone design.

