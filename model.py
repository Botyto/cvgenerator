import base64
from dataclasses import dataclass
from datetime import datetime
import itertools
import os
from typing import ClassVar, List


@dataclass
class Date:
    PRESENT: ClassVar[str] = "Present"

    year: int|None = None
    month: int|None = None
    # day: int|None = None

    def __str__(self):
        if self.year and self.month:
            return f"{self.month_name} {self.year}"
        if self.year:
            return str(self.year)
        return self.month_name

    @property
    def month_name(self):
        return datetime(2000, self.month, 1).strftime("%B") if self.month else ""


@dataclass
class WithDatePeriod:
    start_date: Date|str|None = None
    end_date: Date|str|None = None

    def __str__(self):
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
class Link:
    url: str
    text: str|None = None
    icon: str|None = None

    @property
    def svg(self):
        icon = self.icon or "link"
        path = os.path.join("includes", icon.lower() + ".svg")
        if not os.path.exists(path):
            path = os.path.join("includes/link.svg")
            assert os.path.exists(path), "Fallback link icon not found"
        with open(path, "rt", encoding="utf-8") as fh:
            return fh.read()
        
    @classmethod
    def linkedin(cls, url: str):
        return cls(url, "LinkedIn", "linkedin")
    
    @classmethod
    def github(cls, url: str):
        return cls(url, "GitHub", "github")
    
    @classmethod
    def youtube(cls, url: str):
        return cls(url, "YouTube", "youtube")
    
    @classmethod
    def homepage(cls, url: str):
        return cls(url, "Homepage", "homepage")


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
    link: Link|None = None
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
    skills: List[SkillEntry]|None = None


@dataclass
class SkillsSection(BaseSection):
    TYPE = "skills"
    groups: List[str]|None = None


@dataclass
class ProjectEntry(WithDatePeriod):
    title: str
    link: Link|None = None
    description: str|None = None
    bullets: List[str]|None = None


@dataclass
class ProjectSection(BaseSection):
    TYPE = "project"
    entries: List[ProjectEntry]|None = None


@dataclass
class Profile:
    name: str
    title: str|None = None
    phone: str|None = None
    email: str|None = None
    birth_date: Date|None = None
    location: str|None = None
    links: List[Link]|None = None
    photo_file: str|None = None
    sections: List[BaseSection]|None

    @property
    def first_name(self):
        return self.name.split(" ")[0]
    
    @property
    def last_name(self):
        return " ".join(self.name.split(" ")[1:])
    
    @property
    def photo_path(self):
        return os.path.join("input", self.photo_file)

    @property
    def photo_base64(self):
        assert self.photo_path.endswith(".png"), "Only PNG images are supported"
        with open(self.photo_path, "rb") as fh:
            return "data:image/png;base64," + base64.b64encode(fh.read()).decode("utf-8")
    
    @property
    def sections_by_column(self):
        return itertools.groupby(self.sections, key=lambda s: s.column)
