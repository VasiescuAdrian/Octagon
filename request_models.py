from dataclasses import dataclass, field
from typing import Optional, Dict


@dataclass
class GenerateRequestPpt:
    org_id: str
    collection_name: str
    include_externals: bool = False
    include_trainees: bool = False
    template_name: str = "default"
    output_name: Optional[str] = None
    colors: Optional[Dict[str, str]] = field(default=None)