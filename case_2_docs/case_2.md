# Case 2: Ingesting Code Findings into a Data Warehouse

## Current Status

We've developed a Python script to fetch code findings from the Semgrep API, but we're currently facing an issue where the API is returning an empty array for findings, even though we can see data through direct curl requests. This suggests there might be an authentication or permission issue with the API token being used in the script.

### Key Files

1. **Scripts**:
   - `fetch_semgrep_findings.py`: The main script with comprehensive error handling and pagination
   - `simple_fetch.py`: A simplified version focused on core functionality

2. **Documentation**:
   - [README.md](./fetch_findings/README.md): Setup and usage instructions
   - [approach_explanation.md](./fetch_findings/approach_explanation.md): Detailed technical approach
   - [customer_response.md](./fetch_findings/customer_response.md): Draft response to the customer

## Technical Details

### What Works

- Successfully authenticates with the Semgrep API
- Correctly formats API requests to fetch findings
- Handles pagination for large result sets
- Saves results in a structured JSON format

### Current Issue

When running the script, the API returns an empty array for findings, even though:

1. The API token is valid (successful authentication)
2. Direct curl requests with the same token return data
3. The deployment slug is correct

### Next Steps

1. Verify the API token has the correct permissions
2. Check if there are any IP restrictions on the API token
3. Test with a different API token
4. Consider rate limiting or other API restrictions

## Customer Response (Draft)

For the customer response, we've prepared a comprehensive guide that includes:

- Setup instructions
- Usage examples
- Output format details
- Troubleshooting steps

See: [customer_response.md](./fetch_findings/customer_response.md)

## Technical Approach

Our approach included:

1. Using Semgrep's v1 API for comprehensive data access
2. Implementing pagination to handle large result sets
3. Adding error handling and retry logic
4. Providing clear documentation

Full details: [approach_explanation.md](./fetch_findings/approach_explanation.md)

## Resolution Plan

To complete this task, we need to:

1. Resolve the authentication/authorization issue with the API
2. Test the script with a working token
3. Update documentation based on any changes
4. Finalize the customer response with accurate instructions
   - A: [README.md](./README.md)

2. **Approach Explanation**: Separately, explain:
   - _Your approach to creating the script_
   - A: [approach_explanation.md](./fetch_findings/approach_explanation.md)

   - _Next steps if you receive the same request from multiple customers_
   - A: I review their requirements and scope, and then update the script and
     documentation accordingly. I would create a base script and then feature branches
     for each customer request, so I could easily track any customizations while
     optimizing and reducing the amount of code I have to repeat between each request.
