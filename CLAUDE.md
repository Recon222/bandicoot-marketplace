# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Claude Code plugin for analyzing mobile phone metadata using Bandicoot, a Python library for Call Detail Records (CDRs) analysis. The plugin provides slash commands, auto-triggered skills, and multi-step agents for analyzing communication patterns, mobility behavior, and social networks from phone metadata.

## Architecture

### Plugin Structure

```
.claude-plugin/plugin.json  - Plugin manifest (name, version, paths)
commands/                    - Slash commands (14 total)
skills/                      - Auto-triggered contextual skills (3 total)
agents/                      - Multi-step workflow agents (3 total)
hooks/                       - Validation hooks
scripts/                     - Utility scripts
resources/                   - Sample data and templates
```

### Commands vs Skills vs Agents

- **Commands** (`/bandicoot:*`) - User-invoked slash commands for specific operations
- **Skills** - Auto-triggered based on conversation context (CDR analysis, result interpretation, data preparation)
- **Agents** - Complex multi-step workflows (batch processing, network analysis, custom indicator development)

### Key Command Files

Command markdown files in `commands/` use YAML frontmatter:
```yaml
---
description: Command description
argument-hint: <required> [optional] [--flags]
allowed-tools: Bash, Read
---
```

### Skill Files

Skills in `skills/*/SKILL.md` use similar frontmatter with trigger examples:
```yaml
---
name: skill-name
description: |
  When to trigger this skill...
  <example>...</example>
allowed-tools: Bash, Read, Glob
---
```

### Agent Files

Agents in `agents/*.md` define multi-step workflows with model preferences:
```yaml
---
name: agent-name
model: sonnet
allowed-tools: Bash, Read, Glob
---
```

## Critical Development Pattern

**NEVER create wrapper scripts around Bandicoot.** All Bandicoot operations must be executed inline:

```bash
# CORRECT - inline execution
conda run -n bandicoot python -c "
import bandicoot as bc
user = bc.read_csv('ego', 'demo/data/', 'demo/data/antennas.csv')
print(bc.individual.number_of_contacts(user))
"

# INCORRECT - do not create script files for Bandicoot calls
```

This pattern is enforced throughout the plugin because:
1. Each command execution is independent (no state persistence)
2. Reduces complexity and potential for version drift
3. Makes command behavior transparent and debuggable

## Bandicoot Environment

Always use `conda run -n bandicoot` for cross-platform compatibility. Never use `conda activate` in scripts.

```bash
# Verify environment
conda run -n bandicoot python -c "import bandicoot as bc; print(f'Bandicoot {bc.__version__}')"
```

## Data Format Requirements

Records CSV requires these columns:
- `datetime` - Format: `YYYY-MM-DD HH:MM:SS`
- `interaction` - Values: `call`, `text`
- `direction` - Values: `in`, `out`
- `correspondent_id` - Unique contact identifier

Optional: `call_duration`, `antenna_id`, `latitude`, `longitude`

File naming convention: Records file must be `{user_id}.csv` in the records directory.

## Testing Changes

Validate environment and data format:
```bash
conda run -n bandicoot python scripts/validate.py --env-only
conda run -n bandicoot python scripts/validate.py --user ego --data demo/data/ --antennas demo/data/antennas.csv
```

## Key Bandicoot API

```python
import bandicoot as bc

# Load user
user = bc.read_csv('user_id', 'records_path/', 'antennas.csv', describe=True)

# Run all indicators
results = bc.utils.all(user, groupby='week', summary='default')

# Export
bc.to_csv(results, 'output.csv')
bc.to_json(results, 'output.json')

# Individual indicators
bc.individual.number_of_contacts(user)
bc.individual.call_duration(user)
bc.individual.percent_nocturnal(user)

# Spatial indicators (requires antenna data)
bc.spatial.radius_of_gyration(user)
bc.spatial.number_of_antennas(user)

# Network indicators (requires network=True when loading)
bc.network.clustering_coefficient_unweighted(user)
```
