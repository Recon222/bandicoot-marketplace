# Plugin Review: Wrapper Script Anti-Pattern Issues

**Date**: 2026-01-15
**Reviewer**: Claude Code MCP Protocol Expert
**Scope**: All agent definitions, skill files, and commands in the Bandicoot plugin

## Executive Summary

This review identifies issues across the Bandicoot plugin where AI agents may misinterpret code examples as "templates to copy into separate script files" rather than "functions to call directly via inline Python." This anti-pattern was discovered when the `network-analyst` agent created a 96-line wrapper script instead of simply calling `bc.network.clustering_coefficient_unweighted(user)` directly.

### Key Findings

1. **1 file already fixed**: `network-analyst.md` has the correct "No Wrapper Scripts" section
2. **2 agent files need the same fix**: `batch-processor.md` and `indicator-developer.md`
3. **3 skill SKILL.md files need explicit guidance**: Missing warnings against wrapper scripts
4. **14 command files need clarification**: All commands show Python code blocks that could be misinterpreted
5. **Several supporting documentation files are at risk**: Reference docs show code that could be copy-pasted into scripts

### Risk Summary

| Priority | File Count | Issue Type |
|----------|------------|------------|
| HIGH | 2 | Agent files missing "No Wrapper Scripts" section |
| HIGH | 3 | Skill SKILL.md files missing explicit inline execution guidance |
| MEDIUM | 14 | Command files showing multi-line Python without context |
| LOW | 8 | Supporting documentation files with code examples |

---

## Detailed File Review

---

### AGENT FILES

---

#### File: `agents/network-analyst.md`

**Priority**: ALREADY FIXED

**Current Status**: This file was already updated with the correct pattern. It includes:

```markdown
## CRITICAL: No Wrapper Scripts

Bandicoot is a complete analysis toolkit. All functions shown below are
BUILT INTO Bandicoot. Your job is to CALL them, not reimplement them.

**DO**: Run Bandicoot functions directly:
```bash
conda run -n bandicoot python -c "
import bandicoot as bc
user = bc.read_csv('user_id', 'data/', network=True)
print(bc.network.clustering_coefficient_unweighted(user))
"
```

**DON'T**: Create .py script files that wrap Bandicoot functions.

The code examples below demonstrate Bandicoot's API. Execute them inline
or in a Python REPL - do not save them as separate scripts.
```

**Recommendation**: Use this file as the template for fixing other agent files.

---

#### File: `agents/batch-processor.md`

**Priority**: HIGH

**Current Issues**:
1. No "No Wrapper Scripts" warning section
2. Shows extensive multi-line Python code blocks (lines 51-168, 176-220, 228-257, etc.) that could easily be misinterpreted as script templates
3. The "Batch Processing Workflow" shows step-by-step Python code without explicitly stating these should be executed inline
4. Code blocks show file operations (opening files, CSV writing) that might encourage script creation

**Specific Problem Areas**:

Lines 51-79: File discovery code shows Python that looks like a standalone script:
```python
import os
import glob

records_path = '{records_path}'
...
```

Lines 85-137: Processing loop shows complete implementation that an agent might save as a file.

Lines 143-169: Export code shows file writing which further suggests "this is a script to save."

**Suggested Changes**:

Add at the beginning (after the frontmatter and before "Your Responsibilities"):

```markdown
## CRITICAL: No Wrapper Scripts

Bandicoot is a complete analysis toolkit. All functions shown below are
BUILT INTO Bandicoot. Your job is to CALL them, not reimplement them.

**DO**: Run Bandicoot functions directly:
```bash
conda run -n bandicoot python -c "
import bandicoot as bc
import os
user_files = [f for f in os.listdir('data/') if f.endswith('.csv')]
for f in user_files[:5]:
    user = bc.read_csv(f[:-4], 'data/')
    print(f'{f}: {len(user.records)} records')
"
```

**DON'T**: Create .py script files that wrap Bandicoot functions.

The code examples below demonstrate Bandicoot's API patterns. Execute them
inline via `conda run -n bandicoot python -c "..."` or in a Python REPL.
Do not save them as separate .py script files.
```

Additionally, update all code block headers to clarify their purpose:
- Change "```python" to "```python  # Execute inline - do not save as script"
- Or add a note above each major code block: "Execute the following inline:"

---

#### File: `agents/indicator-developer.md`

**Priority**: HIGH

**Current Issues**:
1. No "No Wrapper Scripts" warning section
2. This agent's PURPOSE is to write custom indicators, so it's especially prone to creating wrapper scripts
3. Shows complete indicator function implementations (lines 126-162, 184-216, etc.)
4. The "Creating a Custom Indicator" section walks through writing code step-by-step

**Specific Problem Areas**:

Lines 126-162: Shows a complete `callback_time` indicator implementation - an agent might save this as `callback_time.py`.

Lines 219-274: Shows multiple "Indicator Patterns" that look like reusable functions to save.

Lines 305-345: Shows "Example Custom Indicators" that are complete, saveable functions.

**Suggested Changes**:

This agent is a special case because it IS meant to write new indicator code. However, the guidance should be:

Add after frontmatter:

```markdown
## CRITICAL: Understanding When to Write Code

This agent helps develop CUSTOM indicators - new functionality that doesn't
exist in Bandicoot. Before writing any code, always check:

1. **Does Bandicoot already have this indicator?** Check `bc.individual.*`,
   `bc.spatial.*`, `bc.network.*`, and `bc.recharge.*` first.

2. **Is this a wrapper around existing functions?** If you're just combining
   existing Bandicoot calls, execute them inline instead of creating a script.

**When to write a .py file**: Only when creating genuinely NEW indicator logic
that follows the `@grouping` decorator pattern and will be integrated into
the Bandicoot source or used as a reusable module.

**When NOT to write a .py file**: If you're just calling existing Bandicoot
functions with different parameters or combining their outputs.

### Testing Custom Indicators

Test new indicators inline first:

```bash
conda run -n bandicoot python -c "
import bandicoot as bc
from bandicoot.helper.group import grouping
from bandicoot.helper.maths import summary_stats

@grouping
def my_test_indicator(records):
    return len(records)

user = bc.read_csv('ego', 'demo/data/')
result = my_test_indicator(user, groupby=None)
print(result)
"
```

Only save to a file after the indicator logic is validated.
```

---

### SKILL FILES

---

#### File: `skills/bandicoot-analysis/SKILL.md`

**Priority**: HIGH

**Current Issues**:
1. No explicit warning against wrapper scripts
2. Shows extensive API examples (lines 77-251) that look like code to copy into scripts
3. The "Example Workflow" section (lines 529-551) shows a complete multi-line Python script
4. "Validation Script" section (lines 487-515) shows a complete function definition

**Specific Problem Areas**:

Lines 529-551 (Example Workflow):
```python
import bandicoot as bc

# 1. Load user data
user = bc.read_csv('ego', 'demo/data/', 'demo/data/antennas.csv',
                   describe=True, warnings=True)
...
```
This looks like a complete script to save.

Lines 487-515 (Validation Script):
```python
def validate_user_data(user_id, records_path, antennas_path=None):
    """Validate user data before analysis."""
    ...
```
This is a function definition that strongly suggests "save me to a file."

**Suggested Changes**:

Add after the "Environment Setup" section (around line 68):

```markdown
## CRITICAL: Direct Function Calls, Not Wrapper Scripts

Bandicoot is a complete analysis toolkit. The code examples in this skill
documentation demonstrate Bandicoot's API - they should be executed DIRECTLY
using inline Python commands, not saved as separate script files.

**CORRECT approach** - Execute inline:
```bash
conda run -n bandicoot python -c "
import bandicoot as bc
user = bc.read_csv('ego', 'demo/data/', 'demo/data/antennas.csv')
print(bc.individual.number_of_contacts(user, groupby=None))
"
```

**INCORRECT approach** - Do NOT create wrapper scripts:
```python
# DON'T create a file like "analyze_contacts.py" containing:
import bandicoot as bc
def analyze_contacts(user_id, path):
    user = bc.read_csv(user_id, path)
    return bc.individual.number_of_contacts(user)
```

All Bandicoot functions shown below are built-in. Call them directly.
```

Also, update the "Validation Script" section header to:
```markdown
### Validation Script (Execute Inline)

Run this validation inline to check data before full analysis:
```

---

#### File: `skills/result-interpretation/SKILL.md`

**Priority**: MEDIUM

**Current Issues**:
1. No wrapper script warning (though this skill is less likely to cause the issue since it's about interpretation, not implementation)
2. No code execution guidance at all

**Suggested Changes**:

This skill is primarily about interpretation and doesn't show executable code, so the risk is lower. However, add a brief note:

```markdown
## Note on Code Examples

This skill focuses on interpreting Bandicoot results. When you need to compute
indicators mentioned in this skill, call Bandicoot functions directly via
inline Python - do not create wrapper scripts. See the `bandicoot-analysis`
skill for execution patterns.
```

---

#### File: `skills/data-preparation/SKILL.md`

**Priority**: HIGH

**Current Issues**:
1. No wrapper script warning
2. Shows extensive data conversion code (lines 136-252) that looks like scripts to save
3. "Data Validation Script" section (lines 256-308) shows a complete standalone function
4. Multiple code blocks show pandas operations and file I/O that suggest script creation

**Specific Problem Areas**:

Lines 136-158 (Converting Datetime Formats):
```python
import pandas as pd
from datetime import datetime

df = pd.read_csv('original_data.csv')
...
df.to_csv('converted_data.csv', index=False)
```
This is a complete data conversion script.

Lines 256-308 (Data Validation Script):
```python
def validate_bandicoot_csv(filepath):
    """Validate CSV for Bandicoot compatibility."""
    ...
```
Complete function that looks like it should be saved.

**Suggested Changes**:

Add after frontmatter:

```markdown
## Note on Data Preparation Code

The code examples in this skill show data conversion patterns using pandas
and Python's csv module. These are ONE-TIME data preparation operations.

**For one-time data preparation**: You may create and run a temporary script,
then delete it after your data is converted.

**For Bandicoot analysis**: Once data is in the correct format, call Bandicoot
functions directly via inline Python - do not create wrapper scripts around
Bandicoot's API.

```bash
# CORRECT: After data prep, analyze inline
conda run -n bandicoot python -c "
import bandicoot as bc
user = bc.read_csv('my_user', 'data/')
print(bc.individual.active_days(user))
"
```
```

---

### COMMAND FILES

All 14 command files share a common pattern: they show multi-line Python code blocks in their "Execution" sections that could be misinterpreted as script templates to save rather than inline commands to execute.

---

#### File: `commands/analyze.md`

**Priority**: MEDIUM

**Current Issues**:
- Lines 29-155: Shows a complete Python script with configuration, loading, analysis, and reporting
- No explicit instruction that this should be executed inline

**Suggested Changes**:

Add at the start of the "## Execution" section:

```markdown
## Execution

Execute the following Python code inline using `conda run`:

```bash
conda run -n bandicoot python -c "
[... existing code ...]
"
```

**Note**: This code demonstrates the analysis workflow. Execute it inline
or via the REPL - do not save it as a separate script file.
```

---

#### File: `commands/analyze-individual.md`

**Priority**: MEDIUM

**Current Issues**:
- Lines 41-114: Shows complete indicator computation code
- No inline execution guidance

**Suggested Changes**: Same as above - add inline execution context.

---

#### File: `commands/analyze-spatial.md`

**Priority**: MEDIUM

**Current Issues**:
- Lines 31-114: Complete spatial analysis code
- No wrapper script warning

**Suggested Changes**: Same pattern - clarify inline execution.

---

#### File: `commands/analyze-network.md`

**Priority**: MEDIUM

**Current Issues**:
- Lines 27-136: Complete network analysis code
- No inline execution guidance

**Suggested Changes**: Same pattern.

---

#### File: `commands/analyze-recharge.md`

**Priority**: MEDIUM

**Current Issues**:
- Lines 34-154: Complete recharge analysis code
- No inline execution guidance

**Suggested Changes**: Same pattern.

---

#### File: `commands/load.md`

**Priority**: MEDIUM

**Current Issues**:
- Lines 60-94: Complete loading code
- No explicit inline execution instruction

**Suggested Changes**: Same pattern.

---

#### File: `commands/quick-stats.md`

**Priority**: MEDIUM

**Current Issues**:
- Lines 19-131: Complete statistics gathering code

**Suggested Changes**: Same pattern.

---

#### File: `commands/export.md`

**Priority**: MEDIUM

**Current Issues**:
- Lines 23-74: Complete export code

**Suggested Changes**: Same pattern.

---

#### File: `commands/describe.md`

**Priority**: MEDIUM

**Current Issues**:
- Lines 23-189: Very extensive description code

**Suggested Changes**: Same pattern.

---

#### File: `commands/visualize.md`

**Priority**: MEDIUM

**Current Issues**:
- Lines 25-89: Complete visualization code

**Suggested Changes**: Same pattern.

---

#### File: `commands/compare.md`

**Priority**: MEDIUM

**Current Issues**:
- Lines 23-192: Extensive comparison code

**Suggested Changes**: Same pattern.

---

#### File: `commands/batch.md`

**Priority**: MEDIUM

**Current Issues**:
- Lines 23-227: Very extensive batch processing code

**Suggested Changes**: Same pattern.

---

#### File: `commands/validate.md`

**Priority**: LOW

**Current Issues**:
- This command references an external script (`scripts/validate.py`) which is appropriate
- However, it doesn't clarify that other Bandicoot operations shouldn't create scripts

**Suggested Changes**: Add note that validation is a special case where a script is provided.

---

#### File: `commands/generate-sample.md`

**Priority**: MEDIUM

**Current Issues**:
- Lines 19-114: Complete sample generation code

**Suggested Changes**: Same pattern as other commands.

---

### SUPPORTING DOCUMENTATION

---

#### File: `skills/bandicoot-analysis/error-patterns.md`

**Priority**: LOW

**Current Issues**:
- Shows complete error handling function definitions (lines 15-32, 44-96, 111-149, etc.)
- These look like reusable utilities to save

**Suggested Changes**:

Add a note at the beginning:

```markdown
# Bandicoot Error Handling Patterns

This document defines error handling PATTERNS - conceptual approaches to
handling errors in Bandicoot operations. The code examples illustrate these
patterns but should not be saved as wrapper scripts.

When implementing error handling, incorporate these patterns into your inline
Python commands or use them as guidance for understanding errors - do not
create separate error-handling wrapper libraries.
```

---

#### File: `skills/bandicoot-analysis/troubleshooting.md`

**Priority**: LOW

**Current Issues**:
- Shows diagnostic code (lines 440-493, 495-552) that could be saved as utility scripts
- The "Quick Health Check" and "Data Format Validator" sections show complete functions

**Suggested Changes**:

Add context before the "Diagnostic Commands" section:

```markdown
## Diagnostic Commands

The following diagnostic functions demonstrate troubleshooting patterns.
Execute them inline when needed - do not save them as permanent utility scripts.
For routine validation, use the `/bandicoot:validate` command instead.
```

---

#### File: `skills/data-preparation/common-issues.md`

**Priority**: LOW

**Current Issues**:
- Shows many small code snippets for data fixes
- These are appropriately formatted as one-time fixes

**Suggested Changes**: No changes needed - the snippets are appropriately small and contextual.

---

#### File: `skills/data-preparation/csv-formats.md`

**Priority**: LOW

**Current Issues**:
- Primarily documentation, minimal executable code

**Suggested Changes**: None needed.

---

#### File: `skills/result-interpretation/indicator-meanings.md`

**Priority**: LOW

**Current Issues**:
- Minimal executable code, primarily explanatory

**Suggested Changes**: None needed.

---

#### File: `skills/result-interpretation/benchmarks.md`

**Priority**: LOW

**Current Issues**:
- Minimal executable code, primarily reference data

**Suggested Changes**: None needed.

---

#### File: `skills/bandicoot-analysis/indicator-reference.md`

**Priority**: LOW

**Current Issues**:
- Shows single-line function calls as examples (appropriate)
- No multi-line script-like code

**Suggested Changes**: None needed - this file is correctly formatted.

---

#### File: `skills/bandicoot-analysis/quick-reference.md`

**Priority**: LOW

**Current Issues**:
- Shows short code snippets (appropriate)
- Commands are properly formatted as inline calls

**Suggested Changes**: None needed - this is a good example of appropriate formatting.

---

## General Recommendations for Plugin Architecture

### 1. Create a Shared "Execution Guidelines" Document

Create a new file `docs/EXECUTION-GUIDELINES.md` that all agents and skills can reference:

```markdown
# Bandicoot Plugin Execution Guidelines

## Golden Rule: Call, Don't Wrap

Bandicoot is a COMPLETE analysis toolkit. When you see code examples in
this plugin's documentation, they demonstrate Bandicoot's built-in API.
Your job is to CALL these functions directly, not to wrap them in scripts.

## Correct Execution Patterns

### Pattern 1: Single-line inline
```bash
conda run -n bandicoot python -c "import bandicoot as bc; user = bc.read_csv('ego', 'data/'); print(len(user.records))"
```

### Pattern 2: Multi-line inline
```bash
conda run -n bandicoot python -c "
import bandicoot as bc
user = bc.read_csv('ego', 'demo/data/', 'demo/data/antennas.csv')
print(bc.individual.number_of_contacts(user, groupby=None))
print(bc.spatial.radius_of_gyration(user, groupby=None))
"
```

### Pattern 3: Interactive REPL (for exploration)
```bash
conda run -n bandicoot python
>>> import bandicoot as bc
>>> user = bc.read_csv('ego', 'demo/data/')
>>> bc.individual.active_days(user)
```

## Anti-Patterns to Avoid

### DO NOT create wrapper scripts like:
```python
# BAD: analyze_user.py
import bandicoot as bc

def analyze_user(user_id, path):
    user = bc.read_csv(user_id, path)
    return bc.utils.all(user)

if __name__ == "__main__":
    results = analyze_user("ego", "demo/data/")
```

### DO NOT create utility libraries like:
```python
# BAD: bandicoot_helpers.py
import bandicoot as bc

def load_and_validate(user_id, path):
    ...

def safe_analysis(user):
    ...
```

## When IS It Appropriate to Create a Script?

1. **Data preparation**: One-time format conversion scripts are OK
2. **Custom indicators**: New indicator logic following @grouping pattern
3. **Batch automation**: External automation tools (not Claude Code)
4. **Integration**: Connecting Bandicoot to other systems

Even in these cases, keep scripts minimal and focused.
```

### 2. Add Frontmatter Guidelines Reference

Update all agent and skill SKILL.md frontmatter to include a reference:

```yaml
---
name: bandicoot-network-analyst
# ... existing frontmatter ...
execution-guidelines: See docs/EXECUTION-GUIDELINES.md
---
```

### 3. Consider a Lint/Validation Hook

Add a hook that warns when an agent proposes creating a `.py` file that imports bandicoot:

```python
# hooks/validate-output.py
def check_for_wrapper_scripts(output):
    if ".py" in output and "import bandicoot" in output:
        if "Write" in output or "create" in output.lower():
            return {
                "warning": "Creating a wrapper script around Bandicoot functions. "
                           "Consider using inline execution instead. "
                           "See docs/EXECUTION-GUIDELINES.md"
            }
    return None
```

### 4. Standardize Code Block Headers

Establish a convention for code blocks:

- `# INLINE - Execute directly` for code that should be run inline
- `# REFERENCE - API documentation` for code showing function signatures
- `# TEMPLATE - Customize and use` for rare cases where scripts are appropriate

Example:
```python  # INLINE - Execute directly via conda run
import bandicoot as bc
user = bc.read_csv('ego', 'demo/data/')
```

---

## Implementation Priority Matrix

| Priority | Action | Files Affected | Effort |
|----------|--------|----------------|--------|
| P0 | Add "No Wrapper Scripts" section to agents | 2 files | Low |
| P0 | Add inline execution warning to skill SKILL.md files | 3 files | Low |
| P1 | Create shared EXECUTION-GUIDELINES.md | 1 new file | Medium |
| P1 | Update command files with inline execution context | 14 files | Medium |
| P2 | Update supporting documentation | 4 files | Low |
| P3 | Add validation hook | 1 file | Medium |

---

## Summary

The core issue is that AI agents interpret Python code blocks as "templates to save as scripts" rather than "commands to execute inline." The fix already applied to `network-analyst.md` provides the correct pattern. This same pattern should be applied to:

1. **All agent files** (mandatory)
2. **All skill SKILL.md files** (mandatory)
3. **All command files** (recommended)
4. **A new shared guidelines document** (recommended)

The key messaging that must be present:
- Bandicoot is a COMPLETE toolkit - don't wrap it
- Execute functions INLINE via `conda run -n bandicoot python -c "..."`
- Code examples demonstrate the API - they are not script templates
- Your job is to CALL Bandicoot functions, not reimplement them
