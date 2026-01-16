# Command Reference Refactoring - Completed

**Date**: 2026-01-15
**Task**: Convert code templates to command references across the Bandicoot plugin

## Summary

Refactored all agent and command files in the Bandicoot plugin from code templates to command references. The previous format contained large Python code blocks (50-100+ lines) that agents would copy-paste into wrapper scripts. The new format teaches agents to RUN Bandicoot commands directly using inline Python.

## Files Refactored: 16 Total

### Agents (1 file)

| File | Commit | Summary |
|------|--------|---------|
| `agents/batch-processor.md` | `73d1c42` | Replaced batch processing script template with command reference tables and inline execution pattern |

### Commands (13 files)

| File | Commit | Summary |
|------|--------|---------|
| `commands/analyze.md` | `cd012df` | Replaced full analysis script with `bc.utils.all()` command reference |
| `commands/analyze-individual.md` | `03db708` | Replaced individual indicator script with `bc.individual.*` command table |
| `commands/analyze-spatial.md` | `3061b9f` | Replaced spatial script with `bc.spatial.*` command table |
| `commands/analyze-network.md` | `ef6dd03` | Replaced network analysis script with `bc.network.*` command table |
| `commands/analyze-recharge.md` | `df708db` | Replaced recharge script with `bc.recharge.*` command table |
| `commands/load.md` | `950f62d` | Replaced load script with `bc.read_csv()` options table |
| `commands/quick-stats.md` | `452420a` | Replaced stats script with property and indicator command tables |
| `commands/export.md` | `24ea377` | Replaced export script with `bc.to_csv/bc.to_json` reference |
| `commands/describe.md` | `85a9d55` | Replaced describe script with `user.describe()` and property tables |
| `commands/visualize.md` | `8f61890` | Replaced visualization script with `bc.visualization.*` reference |
| `commands/compare.md` | `01f9eb4` | Replaced comparison script with batch processing workflow reference |
| `commands/batch.md` | `e0420a0` | Replaced batch processing script with workflow and command reference |
| `commands/generate-sample.md` | `1e153b2` | Replaced generation script with `bc.tests.sample_user()` reference |

### Skills (1 file)

| File | Commit | Summary |
|------|--------|---------|
| `skills/bandicoot-analysis/SKILL.md` | `f62365f` | Removed `Write` from allowed-tools to prevent wrapper script creation |

## Files Skipped

| File | Reason |
|------|--------|
| `agents/indicator-developer.md` | About creating custom code, not running Bandicoot |
| `commands/validate.md` | Uses bundled validation script (exception noted in file) |
| `skills/data-preparation/SKILL.md` | Keeps `Write` tool - data prep may need file creation for format conversion |
| `skills/result-interpretation/SKILL.md` | Already read-only, no code templates |
| `skills/bandicoot-analysis/quick-reference.md` | Already in command reference format |
| `skills/bandicoot-analysis/indicator-reference.md` | Already in API documentation format |

## Key Changes Made

### Before (Code Template Pattern)
```python
import bandicoot as bc
user = bc.read_csv('{user_id}', '{records_path}', network=True)
print(f"User: {user.name}")
print(f"Records: {len(user.records)}")
# ... 50+ more lines of script
```

### After (Command Reference Pattern)
```markdown
## Commands

| Command | Purpose |
|---------|---------|
| `bc.read_csv('user_id', 'path/', network=True)` | Load with network |
| `user.name` | User identifier |
| `len(user.records)` | Record count |

Execute inline: `conda run -n bandicoot python -c "import bandicoot as bc; ..."`
```

## Principles Applied

1. **No large code blocks** - Replaced with command reference tables
2. **Tell them WHAT exists** - Not HOW to write a script
3. **Single-line examples only** - Commands that can be run inline
4. **Keep interpretation tables** - Retained helpful value interpretation guides
5. **Keep troubleshooting sections** - Retained diagnostic guidance
6. **Remove Write from allowed-tools** - Prevents file creation in analysis agents

## Verification

All changes committed individually with descriptive commit messages following the pattern:
```
refactor(<type>): Convert <filename> to command reference

Replaced code templates with command reference format.
Agents should run Bandicoot commands directly, not copy scripts.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

## Impact

Agents using these files will now:
- Execute Bandicoot commands inline via `conda run -n bandicoot python -c "..."`
- Reference the API directly instead of copying script templates
- Not create wrapper Python files
- Understand what functions exist without needing to write boilerplate
