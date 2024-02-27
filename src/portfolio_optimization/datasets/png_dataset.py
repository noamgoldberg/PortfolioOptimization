import os
from typing import Any, Dict
from kedro.io import AbstractDataSet
from pathlib import Path
import plotly.graph_objects as go
import plotly.io as pio


class PNGDataSet(AbstractDataSet):
    
    def __init__(
        self,
        filepath: str,
    ):
        filepath_stripped = filepath.rstrip(Path(filepath).suffix)
        self.filepaths = {suffix: f"{filepath_stripped}.{suffix}" for suffix in ['png', 'json']}

    def _load(self):
        with open(self.filepaths['json'], 'r') as f:
            return pio.from_json(f.read())

    def _save(self, data: go.Figure) -> None:
        os.makedirs(os.path.dirname(self.filepaths['png']), exist_ok=True)
        
        # Save PNG
        pio.write_image(data, self.filepaths['png'], format='png')
        
        # Save JSON
        json_data = data.to_json()
        with open(self.filepaths['json'], 'w') as json_file:
            json_file.write(json_data)

    def _exists(self) -> Dict[str, Any]:
        return os.path.exists(self.filepaths['json'])

    def _describe(self) -> Dict[str, Any]:
        return {
            "filepaths": self.filepaths,
            "type": "PNGDataSet",
        }
