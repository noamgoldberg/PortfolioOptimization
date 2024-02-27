from typing import Optional

from .section import Section


class AnalysisReport:
    def __init__(self, title: Optional[str] = None):
        self.sections = []
        if title:
            report_title_section = Section(dropdown=False)
            report_title_section.add_header(title, level=1)
            self.add_section(report_title_section)

    def add_section(self, section: Section):
        if isinstance(section, Section):
            self.sections.append(section)
        else:
            raise TypeError("Section must be an instance of Section")

    def generate_report(self):
        return '\n'.join([s.to_markdown() for s in self.sections])
    # def generate_report(self, file_path):
        # with open(file_path, 'w') as f:
        #     f.write(f"# {self.title}\n\n")
        #     for section in self.sections:
        #         f.write(section.to_markdown())
