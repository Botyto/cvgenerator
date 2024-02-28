import base64
from dataclasses import dataclass
from datetime import datetime
import io
import itertools
import os
import PIL.Image
import re
from typing import ClassVar, List

# Common types


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


class BaseEntry:
    TYPE: ClassVar[str] = "none"


@dataclass
class Section:
    title: str
    column: int = 0
    columns_count: int = 1
    entries: List[BaseEntry]|None = None


@dataclass
class TextEntry(BaseEntry):
    """
    A simple text entry with optional bullets.

    Used for summary, about, etc.
    """
    TYPE = "text"
    text: str|None = None
    bullets: List[str]|None = None


@dataclass
class QuoteEntry(BaseEntry):
    """
    A quote entry with optional author.

    Used for phylosophy, testimonials, etc.
    """
    TYPE = "quote"
    text: str|None = None
    author: str|None = None


@dataclass
class ExperienceEntry(WithDatePeriod, BaseEntry):
    """
    A single experience entry with optional bullets.

    Used for work experience, education, personal projects, volunteering, etc.
    """
    TYPE = "experience"
    title: str|None = None
    subtitle: str|None = None
    location: str|None = None
    link: str|None = None
    description: str|None = None
    bullets: List[str]|None = None


@dataclass
class SkillsEntry(BaseEntry):
    """
    A group of skills with optional title.
    The skills are arranged on a wrapping line.

    Used for skills, tools, etc.

    For option with sliders use SlidersEntry.
    """
    TYPE = "skills"
    title: str|None = None
    skills: List[str]|None = None


@dataclass
class SliderEntry(BaseEntry):
    """
    An entry with a slider and an optional title.

    Used for skills, languages, etc.
    """
    TYPE = "slider"
    title: str|None = None
    subtitle: str|None = None
    value: float|None = None


@dataclass
class IconAndTextEntry(BaseEntry):
    """
    General purpose entry with an icon, title and description (all optional).

    Used for references, achievements, awards, certificates, courses,
    strengths, social media profiles, etc.
    """
    TYPE = "icon_and_text"
    title: str|None = None
    icon: str|None = None
    description: str|None = None


@dataclass
class PieChartValue:
    name: str|None = None
    weight: float|None = None


@dataclass
class PieChartEntry(BaseEntry):
    """
    An entry with a pie chart and an optional title.
    Used for languages, frameworks, etc.
    """
    TYPE = "pie_chart"
    values: List[PieChartValue]|None = None

    @property
    def total_weight(self):
        return sum(v.weight for v in self.values if v.weight is not None)
    
    def normalized_weight(self, idx: int):
        return self.values[idx].weight / self.total_weight if self.total_weight else 0
    
    RGB_PATTERN = r"rgb\((\d+), (\d+), (\d+)\)"
    def lerp_color(self, a: str, b: str, idx: int):
        a_match = re.match(self.RGB_PATTERN, a)
        b_match = re.match(self.RGB_PATTERN, b)
        w = self.values[idx].weight / max(v.weight for v in self.values if v.weight is not None)
        if a_match and b_match:
            ar, ag, ab = map(int, a_match.groups())
            br, bg, bb = map(int, b_match.groups())
            r = int(ar + (br - ar) * w)
            g = int(ag + (bg - ag) * w)
            b = int(ab + (bb - ab) * w)
            return f"rgb({r}, {g}, {b})"
        else:
            return a
        
    PI = 3.14159265358979323846
    def angles(self, idx: int):
        weights = [self.normalized_weight(i) for i in range(idx + 1)]
        weights_before = sum(weights[:idx])
        weights_after = sum(weights)
        angle_start = self.PI * 2 * weights_before
        angle_end = self.PI * 2 * weights_after
        return angle_start, angle_end


# Profile


@dataclass
class Profile:
    name: str|None = None
    title: str|None = None
    template: str = "default"
    custom_css: str|None = None
    base_color: str = "rgb(0, 43, 127)"
    accent_color: str = "rgb(86, 172, 242)"
    text_color: str = "rgb(61, 58, 58)"
    page_color: str = "rgb(255, 255, 255)"
    background_color: str = "rgb(119, 119, 119)"
    page_image: str|None = None
    phone: str|None = None
    email: str|None = None
    birthdate: Date|None = None
    location: str|None = None
    link: str|None = None
    photo_file: str|None = None
    sections: List[Section]|None = None

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
        by_column = sorted(self.sections, key=lambda s: s.column)
        return itertools.groupby(by_column, key=lambda s: s.column)
