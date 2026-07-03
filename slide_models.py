from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class BoxModel:
    title: str
    subtitle: str
    box_type: str
    is_changed: bool = False
    target_org_id: Optional[str] = None


@dataclass
class SlideModel:
    title: str
    hierarchy_level: str
    head_of_unit: BoxModel
    type: str = "org_chart"
    assistant: Optional[BoxModel] = None
    columns: List[List[BoxModel]] = field(default_factory=list)
    org_id: Optional[str] = None


@dataclass
class PresentationModel:
    slides: List[SlideModel] = field(default_factory=list)