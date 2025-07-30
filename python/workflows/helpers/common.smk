# Helper functions
def get_key_for_datacard(datacard):
    # Extract the base datacard name without any potential path components
    datacard_base = os.path.basename(datacard)
    for key, info in config['cases'].items():
        if info['datacard'] == datacard_base:
            return key
    raise ValueError(f"No key found for datacard {datacard}")

# Override the get_case_param function to work with our dictionary structure
def get_case_param(wildcards, key):
    # For each case in our config
    for case_key, case_info in config["cases"].items():
        # Match by datacard name
        if case_info["datacard"] == wildcards.datacard:
            # If we also need to match workspace, check if it's a substring
            if hasattr(wildcards, 'workspace'):
                # If the workspace directory contains our case workspace directory, it's a match
                if case_info["workspace"].rstrip('/') in wildcards.workspace.rstrip('/'):
                    return case_info[key]
            else:
                # If we don't need to match workspace, just return the value
                return case_info[key]
            
    # If we get here, no match was found
    workspace_val = getattr(wildcards, 'workspace', 'N/A')
    raise ValueError(f"No matching case for datacard={wildcards.datacard}, workspace={workspace_val}")