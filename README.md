# tb-meteo-app 
Command-line tool for downloading meteorological time series from a ThingsBoard instance and exporting it to CSV. This tool:

- Connects to a ThingsBoard REST API
- Fetches telemetry for predefined identifiers (devices/assets)
- Resamples data to standard timestamps
- Exports data to CSV
- Stores configuration locally
- Uses a uv-managed virtual environment

## Requirements
- Python ≥ 3.10
- Git
- uv (recommended for dev, but not necessary)

# Installation

## Step 1 - Clone the repository

```sh
	git clone https://github.com/rytis-paskauskas/tb-meteo-app.git
	cd tb-meteo-app
```

## Step 2 — Create Virtual Environment

### Linux / macOS

```sh 
	python3 -m venv .venv
	source .venv/bin/activate
```

### Windows (PowerShell)

```sh 
	python -m venv .venv
	.venv\Scripts\activate
```

You should now see (.venv) in your prompt.

## Step 3 - Install dependencies
```sh
	pip install -r requirements.txt
```

## Step 4 - Run the app

```sh
	python tb-meteo-app.py --configure
```

Then (example)
```sh 
	python tb-meteo-app.py meteorain \
	--start="2025-01-01" \
	--end="2025-02-01" \
	--out=rain.csv
```

# Running the Application
Since this is a script-based project, always use:
```sh
	python tb-meteo-app.py
```

or (optionally)
```sh 
	uv run tb-meteo-app.py
```

## Configuration
Before fetching data, you must configure the application.
Run:

```sh
	python tb-meteo-app.py --configure
```

You will be prompted for:
- API endpoint
- Username
- Password
- Preferred time zone (e.g., UTC, Europe/Rome, Indian/Maldives, etc.)

The timezone is validated against the system timezone database.

The configuration file is stored locally:

### Linux / macOS
```sh
	~/.config/tb-meteo-app/config.json
```

### Windows
```sh
	%APPDATA%\tb-meteo-app\config.json
```

You only need to run `--configure` once unless credentials change.

## Fetching Data
After configuration, you can request data.

Syntax:

```sh 
	tb-meteo-app.py <identifier> --start="<ISO datetime>" --end="<ISO datetime>" --out=<filename>.csv
```

(optional) Run via uv:

```sh 
	uv run tb-meteo-app.py <identifier> \
	--start=<...> \
	--end=<...> \
	--out=<...>
```

### Required Arguments

`<identifier>` : Must be one of the predefined identifiers:
  - meteorain
  - meteohelix
  - meteowind

These correspond to predefined telemetry configurations.

`--start` : Start date/time in ISO format. Accepted formats:

```txt
2025-01-01
2025-01-01T00:00:00
2025-01-01T12:30:00
```

`--end` :  End date/time in ISO format. Must satisfy: `start < end`


If invalid or missing, the application will stop with an error.

`--out` : optional output CSV filename. If omitted, defaults to: `output.csv`


## Example Workflows

Assuming you have successfully downloaded the repository and installed the dependencies. 

### Configure once
```sh 
	python tb-meteo-app.py --configure
```

### Fetch rain data for January
```sh 
	python tb-meteo-app.py meteorain \
	--start="2025-01-01" \
	--end="2025-02-01" \
	--out=january_rain.csv
```


### Get help
```sh
	python tb-meteo-app.py -h
```
