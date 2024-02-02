from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum
from typing import List


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
class Project:
    from_date: datetime
    to_date: datetime|None
    name: str
    description: str
    links: List[Link]|None = None

    def __lt__(self, other):
        return self.from_date < other.from_date


@dataclass
class Experience:
    from_date: datetime
    to_date: datetime|None
    workplace: str
    position: str
    projects: List[Project]
    description: str|None = None
    links: List[Link]|None = None

    def __lt__(self, other):
        return self.from_date < other.from_date


class Degree(IntEnum):
    MASTER = 1
    BACHELOR = 2
    HIGH_SCHOOL = 3


@dataclass
class Education:
    from_date: datetime
    to_date: datetime|None
    school: str
    degree: Degree
    specialization: str|None = None
    description: str|None = None
    links: List[Link]|None = None

    def __lt__(self, other):
        return self.from_date < other.from_date


@dataclass
class HardSkill:
    name: str
    level: float

    def __lt__(self, other):
        return self.level < other.level


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
