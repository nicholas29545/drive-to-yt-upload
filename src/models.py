from dataclasses import dataclass
from pathlib import Path

@dataclass
class VideoMetadata:
    id: int
    title: str
    description: str
    tags: list
    thumbnail_path: Path
    schedule_time: str
    category_id: str
    privacy_status: str
    is_downloaded: bool
    is_uploaded: bool