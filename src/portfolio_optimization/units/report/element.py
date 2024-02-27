from typing import Union
from pathlib import PosixPath
import pandas as pd


##################################  ELEMENT CLASS  ###################################

class Element:
    def to_markdown(self):
        raise NotImplementedError("Subclass must implement abstract method")

#############################  ELEMENT-SPECIFIC CLASSES  #############################

class Header(Element):
    def __init__(self, text: str, level: int = 2):
        self.text = text
        self.level = level

    def to_markdown(self):
        return f"{'#' * self.level} {self.text}\n"

class Text(Element):
    def __init__(self, text: str):
        self.text = text

    def to_markdown(self):
        return f"{self.text}\n"

class Dict(Element):
    def __init__(self, dictionary: dict):
        self.dictionary = dictionary

    def to_markdown(self):
        return "\n".join([f"- **{k}**: {v}" for k, v in self.dictionary.items()]) + "\n"

class Table(Element):
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def to_markdown(self):
        header = "| " + " | ".join(self.df.columns) + " |\n"
        alignment = "|:" + "---|:" * (len(self.df.columns) - 1) + "---|\n"
        data_rows = ""
        for _, row in self.df.iterrows():
            data_rows += "| " + " | ".join(str(value) for value in row) + " |\n"
        return header + alignment + data_rows


class Image(Element):
    def __init__(self, image_path: Union[PosixPath], alt_text: str = None):
        self.image_path = image_path
        self.alt_text = alt_text or ""

    def to_markdown(self):
        return f"![{self.alt_text}]({self.image_path})\n"

class Break(Element):
    def to_markdown(self):
        return "<br>"