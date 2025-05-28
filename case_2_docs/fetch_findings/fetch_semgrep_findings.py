#!/usr/bin/env python3
"""
Fetch code findings from Semgrep API and save them to a JSON file.

This script retrieves all findings since a specified start date and saves them to a JSON file.
"""

import os
import json
import requests
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

# Configuration
SEMGREP_API_URL = "https://semgrep.dev/api/v1"
OUTPUT_FILE = "semgrep_findings.json"
START_DATE = "2024-01-01T00:00:00Z"  # ISO 8601 format


def get_headers(api_token: str) -> Dict[str, str]:
    """Generate headers for Semgrep API requests."""
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_token}",
    }


def get_findings(api_token: str, start_date: str) -> List[Dict[str, Any]]:
    """Fetch all findings from Semgrep API since the start date."""
    url = f"{SEMGREP_API_URL}/findings"
    headers = get_headers(api_token)
    all_findings = []
    page = 1
    per_page = 100  # Maximum allowed by API

    while True:
        params = {
            "since": start_date,
            "page": page,
            "per_page": per_page,
        }

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            if not data.get("findings"):
                break
                
            all_findings.extend(data["findings"])
            
            # Check if we've reached the last page
            if len(data["findings"]) < per_page:
                break
                
            page += 1
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching findings: {e}")
            break

    return all_findings


def save_to_json(data: List[Dict[str, Any]], filename: str) -> None:
    """Save data to a JSON file."""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Successfully saved {len(data)} findings to {filename}")


def main():
    # Get API token from environment variable
    api_token = os.environ.get("SEMGREP_API_TOKEN")
    if not api_token:
        print("Error: SEMGREP_API_TOKEN environment variable not set")
        print("Please set your Semgrep API token as an environment variable:")
        print("  export SEMGREP_API_TOKEN='your-api-token-here'")
        return

    print(f"Fetching findings since {START_DATE}...")
    findings = get_findings(api_token, START_DATE)
    
    if findings:
        save_to_json(findings, OUTPUT_FILE)
    else:
        print("No findings found for the specified date range.")


if __name__ == "__main__":
    main()
