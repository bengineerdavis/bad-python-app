#!/usr/bin/env python3
"""
Fetch code findings from Semgrep API and save them to a JSON file.

This script retrieves all findings since a specified start date across all or specified
deployments and saves them to a JSON file.
"""

import os
import json
import time
import requests
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Union

# Configuration
SEMGREP_API_URL = "https://semgrep.dev/api/v1"
OUTPUT_FILE = "semgrep_findings.json"
START_DATE = "2024-01-01T00:00:00Z"  # ISO 8601 format


def get_headers(api_token: str) -> Dict[str, str]:
    """Generate headers for Semgrep API requests."""
    return {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_token}",
    }


def get_deployments(api_token: str) -> List[Dict[str, Any]]:
    """Fetch all deployments accessible by the API token."""
    url = f"{SEMGREP_API_URL}/deployments"
    headers = get_headers(api_token)
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json().get('deployments', [])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching deployments: {e}")
        return []


def get_findings_for_deployment(
    api_token: str, 
    deployment_slug: str, 
    start_date: str,
    max_pages: int = 1000
) -> List[Dict[str, Any]]:
    """
    Fetch all findings for a specific deployment since the start date.
    
    Args:
        api_token: Semgrep API token
        deployment_slug: The deployment slug/identifier
        start_date: ISO 8601 formatted date string
        max_pages: Maximum number of pages to fetch (safety limit)
        
    Returns:
        List of findings for the deployment
    """
    url = f"{SEMGREP_API_URL}/deployments/{deployment_slug}/findings"
    headers = get_headers(api_token)
    all_findings = []
    
    # Convert ISO date to Unix timestamp (seconds since epoch)
    try:
        dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        since_timestamp = int(dt.timestamp())
        print(f"  Using timestamp: {since_timestamp} ({start_date})")
    except (ValueError, TypeError) as e:
        print(f"Error: Invalid date format. Please use ISO 8601 format (e.g., 2024-01-01T00:00:00Z)")
        print(f"Error details: {str(e)}")
        return []
    
    page = 1
    has_more = True
    
    while has_more and page <= max_pages:
        print(f"  Fetching page {page}...")
        
        try:
            # Make the API request
            response = requests.get(
                url,
                headers=headers,
                params={
                    "since": since_timestamp,
                    "page": page
                }
            )
            
            print(f"  Response status: {response.status_code}")
            
            # Check for rate limiting
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 60))
                print(f"  Rate limited. Waiting {retry_after} seconds...")
                time.sleep(retry_after)
                continue
                
            response.raise_for_status()
            
            # Print raw response for debugging
            response_text = response.text
            print(f"  Raw response: {response_text[:500]}..." if len(response_text) > 500 else f"  Raw response: {response_text}")
            
            # Parse the response
            try:
                data = response.json()
                print(f"  Parsed JSON response type: {type(data)}")
                
                # The API might return a dictionary with a 'findings' key or an array directly
                if isinstance(data, dict) and 'findings' in data:
                    findings = data['findings']
                    print(f"  Found {len(findings)} findings in 'findings' key")
                elif isinstance(data, list):
                    findings = data
                    print(f"  Found {len(findings)} findings in root array")
                else:
                    print(f"  Unexpected response format: {data}")
                    has_more = False
                    break
                
                if findings:
                    all_findings.extend(findings)
                    print(f"  Total findings so far: {len(all_findings)}")
                    
                    # If we got fewer than 100 items, we've reached the end
                    if len(findings) < 100:
                        has_more = False
                    else:
                        page += 1
                else:
                    print("  No findings in this page")
                    has_more = False
                    
            except json.JSONDecodeError as je:
                print(f"  Error decoding JSON: {je}")
                has_more = False
                
        except requests.exceptions.RequestException as e:
            print(f"  Error fetching findings: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"  Response status: {e.response.status_code}")
                try:
                    print(f"  Response body: {e.response.json()}")
                except:
                    print(f"  Response text: {e.response.text[:500]}...")
            has_more = False
            
        except json.JSONDecodeError as je:
            print(f"  Error decoding JSON response: {je}")
            if hasattr(e, 'response'):
                print(f"  Response text: {e.response.text[:500]}...")
            has_more = False
            
        # Add a small delay between requests to avoid rate limiting
        time.sleep(1)
    
    return all_findings


def get_findings(
    api_token: str, 
    start_date: str, 
    deployment_slugs: Optional[List[str]] = None
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Fetch findings from Semgrep API for specified deployments or all accessible ones.
    
    Args:
        api_token: Semgrep API token
        start_date: ISO 8601 formatted date string
        deployment_slugs: Optional list of deployment slugs to fetch from. 
                         If None, fetches from all accessible deployments.
    
    Returns:
        Dictionary mapping deployment slugs to their findings
    """
    if deployment_slugs is None:
        # If no deployments specified, get all accessible deployments
        deployments = get_deployments(api_token)
        deployment_slugs = [d['slug'] for d in deployments]
        if not deployment_slugs:
            print("No deployments found or accessible with the provided token")
            return {}
    
    all_findings = {}
    
    for slug in deployment_slugs:
        print(f"Fetching findings for deployment: {slug}")
        findings = get_findings_for_deployment(api_token, slug, start_date)
        if findings:
            all_findings[slug] = findings
            print(f"  Found {len(findings)} findings for {slug}")
        else:
            print(f"  No findings for {slug} since {start_date}")
    
    return all_findings


def save_to_json(data: List[Dict[str, Any]], filename: str) -> None:
    """Save data to a JSON file."""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Successfully saved {len(data)} findings to {filename}")


def main():
    import argparse
    
    # Set up argument parsing
    parser = argparse.ArgumentParser(description='Fetch Semgrep findings for deployments.')
    parser.add_argument('--deployments', '-d', nargs='+', 
                        help='List of deployment slugs to fetch findings from')
    parser.add_argument('--since', '-s', default=START_DATE,
                        help=f'Start date in ISO 8601 format (default: {START_DATE})')
    parser.add_argument('--output', '-o', default=OUTPUT_FILE,
                        help=f'Output JSON file (default: {OUTPUT_FILE})')
    
    args = parser.parse_args()
    
    # Get API token from environment variable
    api_token = os.environ.get("SEMGREP_API_TOKEN")
    if not api_token:
        print("Error: SEMGREP_API_TOKEN environment variable not set")
        print("Please set your Semgrep API token as an environment variable:")
        print("  export SEMGREP_API_TOKEN='your-api-token-here'")
        return 1

    print(f"Fetching findings since {args.since}...")
    
    # Fetch findings for specified deployments or all accessible ones
    findings_by_deployment = get_findings(
        api_token=api_token,
        start_date=args.since,
        deployment_slugs=args.deployments
    )
    
    if not findings_by_deployment:
        print("No findings found for the specified criteria.")
        return 0
    
    # Calculate total findings
    total_findings = sum(len(findings) for findings in findings_by_deployment.values())
    print(f"\nFound a total of {total_findings} findings across {len(findings_by_deployment)} deployments.")
    
    # Save the results
    save_to_json(findings_by_deployment, args.output)
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
