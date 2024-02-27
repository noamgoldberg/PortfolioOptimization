import json

def convert_dict_from_binary(binary_dict: dict):
    """
    Convert a dictionary with binary keys and values to a standard dictionary with
    string keys and values. Attempts to parse JSON-encoded values into Python objects.

    Parameters:
    - binary_dict: A dictionary with binary keys and/or values.

    Returns:
    - A dictionary with string keys and values, with JSON-encoded strings parsed into Python objects.
    """
    converted_dict = {}
    for key, value in binary_dict.items():
        # Decode the key from binary to string
        str_key = key.decode('utf-8')

        # Attempt to decode the value; if it's JSON, parse it
        try:
            # First, decode the binary value to string
            str_value = value.decode('utf-8')
            # Then, try to parse it as JSON
            converted_dict[str_key] = json.loads(str_value)
        except json.JSONDecodeError:
            # If it's not JSON, just keep the decoded string
            converted_dict[str_key] = str_value
        except AttributeError:
            # If value is not binary (e.g., already a string or a different type), keep it as is
            converted_dict[str_key] = value

    return converted_dict
