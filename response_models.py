from dataclasses import dataclass
from typing import Optional


@dataclass
class GenerateResponsePpt:
    success: bool
    file_url: Optional[str] = None
    message: str = ""