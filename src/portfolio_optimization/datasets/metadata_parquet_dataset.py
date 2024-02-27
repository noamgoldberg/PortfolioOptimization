from typing import Optional, Any, Dict
import pandas as pd
from kedro.extras.datasets.pandas import ParquetDataSet
from kedro.io.core import (
    DataSetError,
    get_filepath_str,
)
from pathlib import Path
import pyarrow as pa
import pyarrow.parquet as pq

class MetadataParquetDataSet(ParquetDataSet):
    def __init__(
        self,
        *args,
        metadata: Optional[Dict[Any, Any]] = None,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.metadata = metadata

    def _save(self, data: pd.DataFrame) -> None:
        save_path = get_filepath_str(self._get_save_path(), self._protocol)

        if Path(save_path).is_dir():
            raise DataSetError(
                f"Saving {self.__class__.__name__} to a directory is not supported."
            )

        if "partition_cols" in self._save_args:
            raise DataSetError(
                f"{self.__class__.__name__} does not support save argument "
                f"'partition_cols'. Please use 'kedro.io.PartitionedDataSet' instead."
            )

        # Convert the DataFrame to a PyArrow Table
        table = pa.Table.from_pandas(data, preserve_index=True)

        # Prepare the metadata
        if self.metadata is not None:
            # Ensure existing metadata is preserved and updated with new metadata
            existing_metadata = table.schema.metadata or {}
            updated_metadata = {
                **existing_metadata,
                **{key.encode('utf-8'): str(value).encode('utf-8') for key, value in self.metadata.items()}
            }
            table = table.replace_schema_metadata(updated_metadata)

        # Use PyArrow to save the table directly to the file system, including metadata
        with self._fs.open(save_path, mode="wb") as fs_file:
            pq.write_table(table, fs_file, **self._save_args)

        self._invalidate_cache()
