import base64
from dataclasses import dataclass
from datetime import datetime
import io
import itertools
import os
import PIL.Image
from typing import ClassVar, List


@dataclass
class Date:
    PRESENT: ClassVar[str] = "Present"

    year: int|None = None
    month: int|None = None

    def __str__(self):
        if self.year and self.month:
            return f"{self.month:02d}/{self.year}"
        if self.year:
            return str(self.year)
        if self.month:
            return self.month_name
        return ""

    @property
    def month_name(self):
        return datetime(2000, self.month, 1).strftime("%b") if self.month else ""


@dataclass
class WithDatePeriod:
    start_date: Date|str|None = None
    end_date: Date|str|None = None

    @property
    def date_range(self):
        start_str = str(self.start_date) if self.start_date else None
        end_str = str(self.end_date) if self.end_date else None
        if start_str and end_str:
            return f"{start_str} - {end_str}"
        if start_str:
            return f"Since {start_str}"
        if end_str:
            return f"Until {end_str}"
        return ""


@dataclass
class BaseSection:
    TYPE: ClassVar[str] = "none"
    title: str
    column: int = 0


@dataclass
class TextEntry:
    text: str|None = None
    bullets: List[str]|None = None


@dataclass
class TextSection(BaseSection):
    TYPE = "text"
    entries: List[TextEntry]|None = None


@dataclass
class JobEntry(WithDatePeriod):
    title: str|None = None
    company: str|None = None
    location: str|None = None
    link: str|None = None
    description: str|None = None
    bullets: List[str]|None = None


@dataclass
class JobSection(BaseSection):
    TYPE = "job"
    entries: List[JobEntry]|None = None


@dataclass
class EducationEntry(WithDatePeriod):
    field: str|None = None
    school: str|None = None
    location: str|None = None
    grade: str|None = None
    bullets: List[str]|None = None


@dataclass
class EducationSection(BaseSection):
    TYPE = "education"
    entries: List[EducationEntry]|None = None


@dataclass
class SkillEntry:
    name: str|None = None
    # rating: float|None = None
    # description: str|None = None


@dataclass
class SkillsGroup:
    title: str|None = None
    entries: List[SkillEntry]|None = None


@dataclass
class SkillsSection(BaseSection):
    TYPE = "skills"
    groups: List[str]|None = None


@dataclass
class ProjectEntry(WithDatePeriod):
    title: str|None = None
    link: str|None = None
    description: str|None = None
    bullets: List[str]|None = None


@dataclass
class ProjectSection(BaseSection):
    TYPE = "project"
    entries: List[ProjectEntry]|None = None


@dataclass
class Profile:
    name: str|None = None
    title: str|None = None
    template: str = "default"
    custom_css: str|None = None
    base_color: str = "rgb(0, 43, 127)"
    accent_color: str = "rgb(86, 172, 242)"
    text_color: str = "rgb(61, 58, 58)"
    phone: str|None = None
    email: str|None = None
    birthdate: Date|None = None
    location: str|None = None
    link: str|None = None
    photo_file: str|None = None
    sections: List[BaseSection]|None = None

    @property
    def first_name(self):
        return self.name.split(" ")[0]
    
    @property
    def last_name(self):
        return " ".join(self.name.split(" ")[1:])

    @property
    def has_photo(self):
        path = self.photo_path
        return path is not None and os.path.exists(path)

    @property
    def photo_path(self):
        if self.photo_file:
            return os.path.join("input", self.photo_file)

    @property
    def photo_base64(self):
        path = self.photo_path
        if path and os.path.exists(path):
            with open(self.photo_path, "rb") as fh:
                image = PIL.Image.open(fh)
                image.thumbnail((200, 200))
                image = image.convert("RGB")
            buffer = io.BytesIO()
            image.save(buffer, format="JPEG")
            b64 = base64.b64encode(buffer.getvalue())
            return "data:image/jpeg;base64," + b64.decode("utf-8")
    
    @property
    def sections_by_column(self):
        return itertools.groupby(self.sections, key=lambda s: s.column)
