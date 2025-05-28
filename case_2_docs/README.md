# Semgrep Findings Exporter

This script exports code findings from Semgrep into a JSON file for further analysis and integration with data warehouses.

## Prerequisites

- Python 3.7+
- `requests` library (install with `pip install requests`)
- Semgrep API token with appropriate permissions

### Generating a Semgrep API Token

1. Log in to your [Semgrep Cloud Platform](https://semgrep.dev/login) account
2. Click on your profile picture in the top-right corner
3. Select **Settings** from the dropdown menu
4. Navigate to the **Access Tokens** section
5. Click **Create New Token**
6. Give your token a descriptive name (e.g., "Data Warehouse Export")
7. Select the appropriate permissions (at minimum, you'll need `findings:read`)
8. Click **Create Token**
9. **Important**: Copy the token immediately, as it won't be shown again

**Note**: Keep your API token secure and never commit it to version control.

## Setup

1. Install the required dependencies:
   ```bash
   pip install requests
   ```

2. Set your Semgrep API token as an environment variable:
   ```bash
   export SEMGREP_API_TOKEN='your-api-token-here'
   ```
   
   On Windows:
   ```cmd
   set SEMGREP_API_TOKEN=your-api-token-here
   ```

## Usage

Run the script:
```bash
python fetch_semgrep_findings.py
```

By default, the script will:
- Fetch all findings since January 1, 2024
- Save the results to `semgrep_findings.json` in the current directory

## Output

The script generates a JSON file containing an array of findings, where each finding includes:
- Repository information
- Rule information
- File path and line numbers
- Severity and confidence levels
- Code snippets
- Timestamps

## Customization

You can modify the following variables in the script:
- `START_DATE`: Change the date to fetch findings from a different start date
- `OUTPUT_FILE`: Change the output filename
- `SEMGREP_API_URL`: Update if using a different Semgrep deployment

## Error Handling

The script includes basic error handling for:
- Missing API tokenfet
- API request failures
- File write permissions

## Next Steps

1. Review the generated JSON file for the findings
2. Import the JSON into your data warehouse using your preferred ETL tool
3. Schedule this script to run periodically for continuous data collection
