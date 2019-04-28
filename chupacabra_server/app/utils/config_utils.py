import os
from typing import Dict, Any


def get_variable_with_fallback(
    variable_name: str,
    fallback_data: Dict[str, Any],
    is_required: bool = True
) -> Any:
    """Get a variable from the environment with a fallback dict."""
    value = os.getenv(variable_name) or fallback_data.get(variable_name)
    if value is None and is_required:
        raise AssertionError(
            'Required variable \'{}\' not found.'.format(variable_name))

    return value
