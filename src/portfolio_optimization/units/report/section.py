from typing import Optional, Union
from pathlib import PosixPath
import pandas as pd

from .element import Element, Text, Dict, Table, Image, Break, Header


class Section:
    def __init__(self, title: Optional[str] = None, dropdown: bool = False):

        self.elements = []
        self.title = title
        self.dropdown = dropdown

    def add_element(self, element: Element):
        if isinstance(element, Element):
            self.elements.append(element)
        else:
            raise TypeError("Element must be an instance of Element or its subclasses")

    def add_header(self, text: str, level: int = 1):
        self.add_element(Header(text, level=level))

    def add_text(self, text: str):
        self.add_element(Text(text))

    def add_dict(self, dictionary: dict):
        self.add_element(Dict(dictionary))
        
    def add_table(self, df: pd.DataFrame):
        self.add_element(Table(df))
                
    def add_image(self, image_path: Union[str, PosixPath], alt_text: Optional[str] = None):
        self.add_element(Image(image_path, alt_text=alt_text))

    def add_break(self):
        self.add_element(Break())

    def to_markdown(self) -> str:
        section_txt = f"## {self.title}\n\n" if self.title else ""
        if self.dropdown:
            section_txt += f"<details>\n<summary>Click here to view</summary>\n\n"
            for element in self.elements:
                section_txt += element.to_markdown()
            section_txt += "\n</details>\n"
        else:
            for element in self.elements:
                section_txt += element.to_markdown()
        return section_txt
