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

## How to Run

Execute commands using:
```
conda run -n bandicoot python -c "import bandicoot as bc; <commands>"
```

Do NOT create script files. Run commands inline and read the output.

## Visualization Commands

| Command | Purpose |
|---------|---------|
| `bc.visualization.run(user, port=4242)` | Start interactive dashboard |
| `bc.visualization.export(user, 'output_dir/')` | Export static files |

## Workflow

### Option 1: Interactive Dashboard

```
user = bc.read_csv('user_id', 'path/')
bc.visualization.run(user, port=4242)
```

Open browser to `http://localhost:4242`. Press Ctrl+C to stop.

### Option 2: Export Static Files

```
user = bc.read_csv('user_id', 'path/')
bc.visualization.export(user, 'output_dir/')
```

To view exported files:
```
cd output_dir/
python -m http.server 8000
```
Then open `http://localhost:8000`

## Dashboard Features

| Panel | Shows |
|-------|-------|
| Summary | Basic stats, data quality, key metrics |
| Timeline | Activity timeline with zoom/pan |
| Network | Contact network graph |
| Map | Antenna locations (if available) |
| Charts | Call duration, daily/weekly patterns |

## Data Requirements

| Feature | Requires |
|---------|----------|
| Timeline | Records with datetime |
| Network | correspondent_id in records |
| Map | Antennas file with coordinates |
| Spatial | antenna_id matching antennas file |

## Examples

Start dashboard server:
```
/bandicoot:visualize ego demo/data/ demo/data/antennas.csv
```
Open `http://localhost:4242` in browser.

Custom port:
```
/bandicoot:visualize ego demo/data/ demo/data/antennas.csv --port=8080
```

Export static files:
```
/bandicoot:visualize ego demo/data/ demo/data/antennas.csv --export
```

Export to custom directory:
```
/bandicoot:visualize ego demo/data/ --export --output=my_visualization
```

## Export Directory Structure

```
output_dir/
  index.html          # Main page
  js/                 # JavaScript files
  css/                # Stylesheets
  data/               # User data (JSON)
```

## Server Notes

- Runs local HTTP server
- Only accessible from local machine
- Ctrl+C to stop server
- Server blocks terminal until stopped

### Windows Considerations

- Use `localhost` not `0.0.0.0` in browser
- Firewall may prompt - allow for local only
- Try different browser if blocked

## Troubleshooting

**Server won't start**
- Check port not in use: `netstat -an | grep PORT`
- Try different port: `--port=8080`
- Check firewall settings

**Map not showing**
- Verify antennas file provided
- Check antenna coordinates valid
- Ensure records have antenna_id values

**Browser shows blank page**
- Check browser console (F12)
- Try different browser
- Clear browser cache
- Use export mode instead

**Can't stop server**
- Windows: Close terminal or Task Manager
- Unix: Ctrl+C or `kill -9 $(lsof -t -i:PORT)`
