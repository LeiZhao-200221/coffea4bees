
def get_case_param(wildcards, key):
    # Find the index of the current datacard in the config["cases"] list
    for case in config["cases"]:
        if case["datacard"] == wildcards.datacard and case["workspace"] == wildcards.workspace:
            return case[key]
    raise ValueError(f"No matching case for datacard={wildcards.datacard}, workspace={wildcards.workspace}")