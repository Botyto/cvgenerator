from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum
from typing import List


class WithDateRange:
    start_datetime: datetime
    end_datetime: datetime|None

    def __lt__(self, other):
        return self.start_datetime > other.start_datetime
    
    @property
    def start_date(self):
        return self.start_datetime.strftime("%d %b %Y")
    
    @property
    def end_date(self):
        return self.end_datetime.strftime("%d %b %Y") if self.end_datetime else "Present"
    
    @property
    def start_month(self):
        return self.start_datetime.strftime("%B")
    
    @property
    def end_month(self):
        return self.end_datetime.strftime("%B") if self.end_datetime else "Present"
    
    @property
    def start_year(self):
        return self.start_datetime.strftime("%Y")
    
    @property
    def end_year(self):
        return self.end_datetime.strftime("%Y") if self.end_datetime else "Present"
    
    @property
    def range(self):
        return f"{self.start_month} {self.start_year} - {self.end_month} {self.end_year}"
    
    @property
    def years(self):
        diff = self.end_datetime - self.start_datetime if self.end_datetime else datetime.now() - self.start_datetime
        return diff.days // 365
    
    @property
    def months(self):
        diff = self.end_datetime - self.start_datetime if self.end_datetime else datetime.now() - self.start_datetime
        return (diff.days % 365) // 30

    @property
    def duration(self):
        diff = self.end_datetime - self.start_datetime if self.end_datetime else datetime.now() - self.start_datetime
        years = diff.days // 365
        months = (diff.days % 365) // 30
        if years == 0:
            return f"{months} months"
        if months == 0:
            return f"{years} years"
        return f"{diff.days // 365} years {(diff.days % 365) // 30} months"
    
    @property
    def duration_short(self):
        diff = self.end_datetime - self.start_datetime if self.end_datetime else datetime.now() - self.start_datetime
        years = diff.days // 365
        months = (diff.days % 365) // 30
        if years == 0:
            return f"{months}m"
        if months == 0:
            return f"{years}y"
        return f"{diff.days // 365}y {(diff.days % 365) // 30}m"


class LinkType(IntEnum):
    HOMEPAGE = 1
    YOUTUBE = 2
    GITHUB = 3


@dataclass
class Link:
    url: str
    title: str
    type: LinkType

    @classmethod
    def github(cls, url: str, title: str = "GitHub"):
        return cls(url, title, LinkType.GITHUB)
    
    @classmethod
    def youtube(cls, url: str, title: str = "YouTube"):
        return cls(url, title, LinkType.YOUTUBE)
    
    @classmethod
    def homepage(cls, url: str, title: str = "Homepage"):
        return cls(url, title, LinkType.HOMEPAGE)
    
    def __lt__(self, other):
        return self.type.value < other.type.value


@dataclass
class Project(WithDateRange):
    start_datetime: datetime
    end_datetime: datetime|None
    name: str
    description: str
    links: List[Link]|None = None


@dataclass
class Experience(WithDateRange):
    start_datetime: datetime
    end_datetime: datetime|None
    workplace: str
    position: str
    projects: List[Project]
    description: str|None = None
    links: List[Link]|None = None


class EducationType(IntEnum):
    MASTER = 1
    BACHELOR = 2
    SECONDARY_EDUCATION = 3


@dataclass
class Education(WithDateRange):
    start_datetime: datetime
    end_datetime: datetime|None
    school: str
    type: EducationType
    field: str|None = None
    description: str|None = None
    links: List[Link]|None = None

    @property
    def degree(self):
        return self.type.name.replace("_", " ").title()


@dataclass
class HardSkill:
    name: str
    level: float
    description: str|None = None

    def __lt__(self, other):
        return self.level > other.level
    
    def scaled_level(self, scale: int):
        return round(self.level * scale)
    
    def level_ratio(self, scale: int):
        return f"{self.scaled_level(scale)}/{scale}"
    
    def level_stars(self, scale: int, full: str = "★", empty: str = "☆"):
        return full * self.scaled_level(scale) + empty * (scale - self.scaled_level(scale))
    
    def level_dots(self, scale: int, full: str = "•", empty: str = "◦"):
        return full * self.scaled_level(scale) + empty * (scale - self.scaled_level(scale))


@dataclass
class SideProject:
    name: str
    description: str
    links: List[Link]|None = None

    def __lt__(self, other):
        return self.name < other.name


@dataclass
class Profile:
    name: str
    title: str

    @property
    def names(self):
        return self.name.split(" ")

    email: str
    address: str
    birthdate: datetime
    phone: str|None

    about: str
    experiences: List[Experience]
    education: List[Education]
    hard_skills: List[HardSkill]
    side_projects: List[SideProject]
