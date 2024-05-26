from typing import Optional, Union, Iterable
import pyarrow.parquet as pq
import os
import sys
from .dict_utils import convert_dict_from_binary


def read_parquet_metadata(filepath, return_binary: bool = False):
    table = pq.read_table(filepath)
    metadata = dict(table.schema.metadata or {})
    if return_binary:
        return metadata
    return convert_dict_from_binary(metadata)

def save_metadata_to_parquet(filepath: str, metadata: dict) -> None:
    """
    Adds custom metadata to a parquet file.

    Parameters:
    - filepath: The path to the parquet file.
    - metadata: A dictionary containing the metadata to add.
    """
    # Read the parquet file
    table = pq.read_table(filepath)
    
    # Update existing metadata with new metadata
    existing_metadata = dict(table.schema.metadata or {})
    existing_metadata.update(metadata)
    
    # Convert back to an immutable metadata for pyarrow
    updated_metadata = {k.encode('utf-8'): v.encode('utf-8') for k, v in existing_metadata.items()}
    
    # Update the table's schema with the new metadata
    table = table.replace_schema_metadata(updated_metadata)
    
    # Write the table back to the same file with updated metadata
    pq.write_table(table, filepath)


def map_directory(directory, prefix="", ignore_directories: Optional[Union[str, Iterable[str]]] = None, ignore_suffixes: Optional[Union[str, Iterable[str]]] = None):
    try:
        # Get the list of all files and directories in the specified directory
        items = os.listdir(directory)
    except PermissionError:
        print(f"{prefix}[ACCESS DENIED] {directory}")
        return
    
    if isinstance(ignore_directories, str):
        ignore_directories = [ignore_directories]
    
    if isinstance(ignore_suffixes, str):
        ignore_suffixes = [ignore_suffixes]

    for index, item in enumerate(items):
        # Join the directory path with the item name
        path = os.path.join(directory, item)
        is_last = index == len(items) - 1
        connector = "└── " if is_last else "├── "

        # Check if the item is in the list of directories to ignore
        if ignore_directories and item in ignore_directories:
            continue
        
        # Check if the item has a suffix to ignore
        if ignore_suffixes and any(item.endswith(suffix) for suffix in ignore_suffixes):
            continue

        print(f"{prefix}{connector}{item}")

        if os.path.isdir(path):
            # If the item is a directory, recursively call the function
            extension = "    " if is_last else "│   "
            map_directory(path, prefix + extension, ignore_directories, ignore_suffixes)
