#!/usr/bin/env python3
"""
Simple script to fetch findings from Semgrep API for a specific deployment.
"""

import os
import json
import requests
from datetime import datetime
from typing import Dict, List, Any

# Configuration
SEMGREP_API_URL = "https://semgrep.dev/api/v1"

def get_headers(api_token: str) -> Dict[str, str]:
    """Generate headers with authentication."""
    return {
        "Authorization": f"Bearer {api_token}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

def get_deployments(api_token: str) -> List[Dict[str, Any]]:
    """Fetch all deployments available to the API token."""
    url = f"{SEMGREP_API_URL}/deployments"
    headers = get_headers(api_token)
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json().get('deployments', [])

def get_findings(api_token: str, deployment_slug: str, since: int = 0) -> List[Dict[str, Any]]:
    """Fetch all findings for a deployment since the given timestamp."""
    url = f"{SEMGREP_API_URL}/deployments/{deployment_slug}/findings"
    headers = get_headers(api_token)
    all_findings = []
    page = 1
    
    while True:
        print(f"\nFetching page {page}...")
        params = {"since": since, "page": page}
        print(f"  Request URL: {url}")
        print(f"  Params: {params}")
        
        response = requests.get(url, headers=headers, params=params)
        
        print(f"  Response status: {response.status_code}")
        print(f"  Response headers: {dict(response.headers)}")
        
        try:
            data = response.json()
            print(f"  Response JSON type: {type(data)}")
            
            # Print the first 500 chars of the response for debugging
            response_text = json.dumps(data, indent=2)
            print(f"  Response preview: {response_text[:500]}...")
            
            # Try different ways to extract findings
            if isinstance(data, list):
                findings = data
                print(f"  Found {len(findings)} findings in root list")
            elif isinstance(data, dict):
                findings = data.get('findings', [])
                print(f"  Found {len(findings)} findings in 'findings' key")
            else:
                print(f"  Unexpected response format: {type(data)}")
                break
                
            if not findings:
                print("  No more findings found")
                break
                
            all_findings.extend(findings)
            print(f"  Total findings so far: {len(all_findings)}")
            
            if len(findings) < 100:  # Last page
                break
                
            page += 1
            
        except json.JSONDecodeError:
            print(f"  Failed to decode JSON. Response text: {response.text[:500]}...")
            break
            
    return all_findings

def main():
    # Get API token from environment
    api_token = os.environ.get("SEMGREP_API_TOKEN")
    if not api_token:
        print("Error: SEMGREP_API_TOKEN environment variable not set")
        return
    
    # Hardcode the deployment slug we found
    deployment_slug = "bengineerdavis_personal_org"
    print(f"Using deployment: {deployment_slug}")
    
    try:
        # Get all findings since the beginning of time
        print("\nFetching findings...")
        findings = get_findings(api_token, deployment_slug)
        
        # Save to file
        output_file = "semgrep_findings.json"
        with open(output_file, 'w') as f:
            json.dump(findings, f, indent=2)
            
        print(f"\nSuccess! Found {len(findings)} findings. Saved to {output_file}")
        
    except Exception as e:
        print(f"Error: {e}")
        raise  # Re-raise the exception to see full traceback

if __name__ == "__main__":
    main()
