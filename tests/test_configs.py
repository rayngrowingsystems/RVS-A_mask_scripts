# This is just a configuration check, the mask scripts are not executed. Functionality is tested trough RVS analytics
# tests.
# Here is what's checked:
# 1. Do the config file follow the correct structure
# 2. Compare settings called in the mask scripts with the config file
# 3. Check if all functions referenced in the config file are in the mask scripts

import json
import os
import re

import pytest

REPO_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)  # Set REPO_DIR to the directory of the test file
print(REPO_DIR)
EXCLUDED_DIRS = {
    ".git",
    ".idea",
    "tests",
    ".github",
    ".pytest_cache",
    ".ruff_cache",
}  # Add any other unwanted directories

# Find all script/config folders, **excluding hidden and test directories**
script_dirs = [d for d in os.listdir(REPO_DIR) if os.path.isdir(os.path.join(REPO_DIR, d)) and d not in EXCLUDED_DIRS]

print(script_dirs)


@pytest.mark.parametrize("config_path", [os.path.join(REPO_DIR, d, f"{d}.config") for d in script_dirs])
def test_config_structure(config_path):
    """Test if config files contain the correct 'mask' structure."""

    assert os.path.exists(config_path), f"Config file missing: {config_path}"

    with open(config_path, "r") as f:
        config_data = json.load(f)

    # Required keys in the config file
    required_keys = [
        "mask",
        "mask.info",
        "mask.options",
        "mask.options.sections",
    ]

    # Traverse and validate required keys dynamically
    for key in required_keys:
        parts = key.split(".")
        value = config_data
        try:
            for part in parts:
                if "[" in part:  # Handling lists like "sections[0].settings"
                    list_key, index = part[:-1].split("[")
                    index = int(index)
                    assert list_key in value, f"Missing key: {list_key} in {config_path}"
                    value = value[list_key][index]
                else:
                    assert part in value, f"Missing key: {key} in {config_path}"
                    value = value[part]
        except (KeyError, IndexError):
            pytest.fail(f"Config {config_path} is missing expected structure: {key}")


script_config_pairs = [
    (os.path.join(REPO_DIR, d, f"{d}.py"), os.path.join(REPO_DIR, d, f"{d}.config"))
    for d in script_dirs
    if os.path.exists(os.path.join(REPO_DIR, d, f"{d}.py")) and os.path.exists(os.path.join(REPO_DIR, d, f"{d}.config"))
]

# Regular expressions
settings_assignment_pattern = re.compile(r'(\w+)\s*=\s*settings\["experimentSettings"\]\["analysis"\]\["maskOptions"\]')
settings_access_pattern = re.compile(r'settings\["experimentSettings"\]\["analysis"\]\["maskOptions"\]\["(.*?)"\]')
variable_access_pattern = None  # Will be set dynamically based on assignment


def extract_settings_from_script(script_path):
    """Extract settings keys used in the script."""
    with open(script_path, "r") as file:
        content = file.read()

    # Step 1: Detect variable assignment (e.g., mask_options = settings[...])
    match = settings_assignment_pattern.search(content)
    assigned_variable = match.group(1) if match else None

    # Step 2: If a variable was assigned, adjust regex to track it
    global variable_access_pattern
    if assigned_variable:
        variable_access_pattern = re.compile(rf'{assigned_variable}\["(.*?)"\]')

    # Step 3: Extract direct accesses via settings[...] and assigned variable
    settings_keys = set(settings_access_pattern.findall(content))

    if assigned_variable and variable_access_pattern:
        settings_keys.update(variable_access_pattern.findall(content))

    return settings_keys


@pytest.mark.parametrize("script_path, config_path", script_config_pairs)
def test_script_settings_vs_config(script_path, config_path):
    """Test that each script only references settings that exist in its corresponding config file."""

    # Extract all settings keys from script using regex and tracked variable names
    script_keys = extract_settings_from_script(script_path)

    # Ensure that only actual setting names are translated
    translated_script_keys = {f"mask.options.sections.settings.{key}" for key in script_keys}

    # Extract keys from config
    with open(config_path, "r") as file:
        config_data = json.load(file)

    # Extract available settings from all sections dynamically
    section_keys = set()
    if "mask" in config_data and "options" in config_data["mask"] and "sections" in config_data["mask"]["options"]:
        for section in config_data["mask"]["options"]["sections"]:
            if "settings" in section:
                for setting in section["settings"]:
                    if "name" in setting:
                        section_keys.add(f"mask.options.sections.settings.{setting['name']}")

    # Find missing keys after translation
    missing_keys = translated_script_keys - section_keys

    assert not missing_keys, f"Missing keys in {config_path}: {missing_keys}"


# Regex patterns
function_def_pattern = re.compile(r"def (\w+)\((\w+),")  # Extract function name + first parameter


def extract_functions_and_parameters(script_path):
    """Extract all function names and their first parameter from the script."""
    with open(script_path, "r") as file:
        content = file.read()

    # Extract function names and first parameters
    function_params = {match[0]: match[1] for match in function_def_pattern.findall(content)}

    return function_params, content


def extract_ui_elements_from_config(config_path):
    """
    Extract UI element references (getValuesFor, getRangesFor) from the config.
    Returns a dictionary mapping function names to the expected setting check.
    """
    with open(config_path, "r") as file:
        config_data = json.load(file)

    function_mapping = {}

    if "mask" in config_data and "options" in config_data["mask"] and "sections" in config_data["mask"]["options"]:
        for section in config_data["mask"]["options"]["sections"]:
            if "settings" in section:
                for setting in section["settings"]:
                    if "getValuesFor" in setting:
                        function_mapping["dropdown_values"] = setting["getValuesFor"]
                    if "getRangesFor" in setting:
                        function_mapping["range_values"] = setting["getRangesFor"]

    return function_mapping


@pytest.mark.parametrize("script_path, config_path", script_config_pairs)
def test_script_functions_vs_config(script_path, config_path):
    """Test that all functions referenced in the config file exist in the script and contain the correct conditions."""

    # Extract function names and parameter names
    script_functions, script_content = extract_functions_and_parameters(script_path)

    # Extract required function mappings (e.g., "dropdown_values" -> "index_list")
    function_mapping = extract_ui_elements_from_config(config_path)

    # Check if functions exist in the script
    missing_functions = {func for func in function_mapping.keys() if func not in script_functions}
    assert not missing_functions, f"Missing functions in {script_path}: {missing_functions}"

    # Check if required conditions exist inside the correct function
    for function_name, expected_setting in function_mapping.items():
        if function_name in script_functions:
            parameter_name = script_functions[function_name]  # Get the actual parameter used in the function

            # Build regex patterns to check different condition formats
            condition_patterns = [
                re.compile(rf'if {parameter_name}\s*==\s*["\']{expected_setting}["\']'),  # Single condition
                re.compile(
                    rf'if {parameter_name}\s*in\s*\[.*?["\']{expected_setting}["\'].*?\]'
                ),  # List-based condition
                re.compile(
                    rf'if {parameter_name}\s*==\s*["\'].*?["\']\s*or\s*{parameter_name}\s*==\s*["\']{expected_setting}["\']' # noqa: E501
                ),  # Multiple OR conditions
            ]

            # Check if at least one pattern matches
            condition_found = any(pattern.search(script_content) for pattern in condition_patterns)

            assert condition_found, (
                f"Missing valid condition for '{expected_setting}' in {function_name}() in {script_path}"
            )
