---
description: Start Bandicoot interactive visualization dashboard
argument-hint: <user_id> <records_path> [antennas_path] [--port=4242] [--export]
allowed-tools: Bash
---

# Bandicoot: Visualization Dashboard

Start the interactive D3.js visualization dashboard or export static visualization files.

## Arguments

- `user_id` (required): User identifier (filename without .csv)
- `records_path` (required): Directory containing the records CSV
- `antennas_path` (optional): Path to antennas CSV file
- `--port`: Server port number (default: 4242)
- `--export`: Export static files instead of running server
- `--output`: Export directory (default: `{user_id}_viz/`)

## Execution

### Option 1: Run Interactive Dashboard

```python
import bandicoot as bc

user_id = '{user_id}'
records_path = '{records_path}'
antennas_path = '{antennas_path}' if '{antennas_path}' else None
port = {port} if {port} else 4242

# Load user
print(f"Loading user: {user_id}")
user = bc.read_csv(
    user_id,
    records_path,
    antennas_path,
    describe=True,
    warnings=True
)

print(f"\n{'=' * 50}")
print("Starting Bandicoot Visualization Dashboard")
print('=' * 50)
print(f"\nServer starting on port {port}")
print(f"Open your browser to: http://localhost:{port}")
print(f"\nPress Ctrl+C to stop the server")
print('=' * 50)

# Start visualization server
bc.visualization.run(user, port=port)
```

### Option 2: Export Static Files

```python
import bandicoot as bc
import os

user_id = '{user_id}'
records_path = '{records_path}'
antennas_path = '{antennas_path}' if '{antennas_path}' else None
output_dir = '{output}' if '{output}' else f'{user_id}_viz'

# Load user
print(f"Loading user: {user_id}")
user = bc.read_csv(
    user_id,
    records_path,
    antennas_path,
    describe=True,
    warnings=True
)

print(f"\nExporting visualization to: {output_dir}")

# Export static files
path = bc.visualization.export(user, output_dir)

print(f"\n{'=' * 50}")
print("Visualization Export Complete")
print('=' * 50)
print(f"\nFiles exported to: {path}")
print(f"\nTo view the visualization:")
print(f"  1. Navigate to: {output_dir}")
print(f"  2. Start a local server:")
print(f"     python -m http.server 8000")
print(f"  3. Open: http://localhost:8000")
print('=' * 50)
```

## Examples

### Start Dashboard Server

```
/bandicoot:visualize ego demo/data/ demo/data/antennas.csv
```

Then open `http://localhost:4242` in your browser.

### Custom Port

```
/bandicoot:visualize ego demo/data/ demo/data/antennas.csv --port=8080
```

### Export Static Files

```
/bandicoot:visualize ego demo/data/ demo/data/antennas.csv --export
```

### Export to Custom Directory

```
/bandicoot:visualize ego demo/data/ --export --output=my_visualization
```

## Dashboard Features

The Bandicoot visualization dashboard includes:

### 1. Summary Panel
- Basic user statistics
- Data quality indicators
- Key metrics overview

### 2. Timeline View
- Interactive activity timeline
- Calls and texts by day
- Zoom and pan capabilities

### 3. Contact Network
- Visual network graph
- Contact interaction frequency
- Clustered by communication patterns

### 4. Location Map
- Antenna locations on map (if available)
- Movement patterns
- Home and frequent locations

### 5. Statistical Charts
- Call duration distribution
- Daily/weekly patterns
- Contact distribution

## Important Notes

### Server Mode

1. The visualization runs a local HTTP server
2. Only accessible from your local machine by default
3. Press `Ctrl+C` in the terminal to stop the server
4. The server blocks the terminal until stopped

### Windows Considerations

- Use `localhost` not `0.0.0.0` in browser
- Firewall may prompt for network access (allow for local only)
- Some browsers may block local servers - try different browser

### Export Mode

Advantages:
- No running server required
- Can be shared/hosted anywhere
- Permanent copy of visualization

To serve exported files:
```bash
cd {output_dir}
python -m http.server 8000
```

Then open `http://localhost:8000`

## Data Requirements

For full visualization features:

- **Timeline**: Requires records with datetime
- **Network**: Requires correspondent_id in records
- **Map**: Requires antennas file with coordinates
- **Spatial**: Requires antenna_id in records matching antennas file

## Troubleshooting

### Server Won't Start

1. Check port is not in use: `netstat -an | grep {port}`
2. Try different port: `--port=8080`
3. Check firewall settings

### Map Not Showing

1. Verify antennas file is provided
2. Check antenna coordinates are valid
3. Ensure records have antenna_id values

### Browser Shows Blank Page

1. Check browser console for errors (F12)
2. Try different browser
3. Clear browser cache
4. Use export mode instead

### Can't Stop Server

On Windows:
- Close the terminal window
- Or use Task Manager to end Python process

On Unix:
- Press Ctrl+C multiple times
- Or `kill -9 $(lsof -t -i:{port})`

## Export Directory Structure

When using `--export`, creates:

```
{output_dir}/
  index.html          # Main visualization page
  js/                 # JavaScript files
    bandicoot.js
    d3.min.js
    ...
  css/                # Stylesheets
    style.css
  data/               # User data (JSON)
    user.json
```

## Alternative: Quick Visualization

For quick visual inspection without full dashboard:

```python
import bandicoot as bc
import matplotlib.pyplot as plt

user = bc.read_csv('ego', 'demo/data/', 'demo/data/antennas.csv')

# Plot call duration distribution
durations = [r.call_duration for r in user.records if r.call_duration]
plt.hist(durations, bins=30)
plt.xlabel('Call Duration (seconds)')
plt.ylabel('Frequency')
plt.title(f'Call Duration Distribution - {user.name}')
plt.savefig('call_duration.png')
```

Note: Requires matplotlib (not included with Bandicoot).
