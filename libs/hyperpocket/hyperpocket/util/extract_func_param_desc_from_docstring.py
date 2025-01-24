import inspect
import re

from hyperpocket.config import pocket_logger


def extract_param_docstring_mapping(func) -> dict[str, str]:
    """
    Extracts a mapping between function parameters and their descriptions
    from the Google-style docstring.

    Args:
        func (function): The function whose docstring needs to be parsed.

    Returns:
        list: A list of tuples where each tuple contains a parameter name
              and its description.
    """
    # Get the docstring of the function
    docstring = inspect.getdoc(func)
    func_params = inspect.signature(func).parameters.keys()

    if not docstring:
        return {}

    param_mapping = extract_param_desc_by_google_stype_docstring(docstring, func_params)
    if param_mapping:
        pocket_logger.debug(
            f"success extract docstring of {func.__name__} by google style!"
        )
        return param_mapping
    pocket_logger.debug(f"not found param desc of {func.__name__} by google style..")

    param_mapping = extract_param_desc_by_other_styles(docstring, func_params)
    if param_mapping:
        pocket_logger.debug(
            f"success extract docstring of {func.__name__} by other style!"
        )
        return param_mapping
    pocket_logger.debug(f"not found param desc of {func.__name__} by other styles..")

    # Plain Text Style matching
    param_descriptions = []
    for line in docstring.split("\n"):
        split_line = line.strip().split(":")
        if len(split_line) < 2:
            continue

        param_name = split_line[0]
        cleaned_param_name = clean_string(param_name)
        cleaned_param_name = clean_bracket_content(cleaned_param_name)
        description = ":".join(split_line[1:]).strip()
        if cleaned_param_name in func_params:
            param_descriptions.append((cleaned_param_name, description))

    # Ensure no duplicates and match with function parameters
    param_mapping = {
        param: desc for param, desc in param_descriptions if param in func_params
    }
    pocket_logger.debug(f"final param_mapping of {func.__name__} : {param_mapping}")

    return param_mapping


def clean_string(input_string):
    cleaned = re.sub(r"^[^a-zA-Z_]*|[^a-zA-Z0-9_()\s]*$", "", input_string)
    return cleaned.strip()


def clean_bracket_content(content):
    return re.sub(r"[(\[{<].*?[)\]}>]", "", content)


def extract_param_desc_by_other_styles(docstring, func_params) -> dict[str, str]:
    param_descriptions = []
    # Pattern for Sphinx-style or Javadoc-style `:param`, `@param`, `:arg`, `@arg`
    param_pattern = r"^\s*(?:@param|:param|:arg|@arg):?\s+(\w+)(?:\((.*?)\))?:?\s*(.*)"
    matches = re.findall(param_pattern, docstring, re.MULTILINE)
    for param, _, desc in matches:
        cleaned_param = clean_bracket_content(param)
        param_descriptions.append((cleaned_param, desc.strip()))
    # Ensure no duplicates and match with function parameters
    param_mapping = {
        param: desc for param, desc in param_descriptions if param in func_params
    }
    return param_mapping


def extract_param_desc_by_google_stype_docstring(
    docstring, func_params
) -> dict[str, str]:
    # Regex pattern to extract parameter descriptions in Google style
    param_pattern = r"Args:\n(.*?)(?=\n\S|$)"  # Matches the Args: section
    match = re.search(param_pattern, docstring, re.DOTALL)
    if not match:
        return {}
    param_section = match.group(1)
    # Parse the parameter names and descriptions
    param_lines = param_section.split("\n")
    param_descriptions = {}
    for line in param_lines:
        # Match parameter line with "name (type): description"
        param_match = re.match(
            r"^[^a-zA-Z_]*([a-zA-Z_]\w*)\s*[\(\[]\s*(.*?)\s*[\)\]]\s*:\s*(.*)", line
        )
        if param_match:
            param, _, desc = param_match.groups()
            cleaned_param = clean_bracket_content(param)
            param_descriptions[cleaned_param] = desc.strip()
    # Match parameters to descriptions
    param_mapping = {
        param: desc
        for param, desc in param_descriptions.items()
        if param in func_params
    }
    return param_mapping
