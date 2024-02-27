import pyarrow.parquet as pq
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
