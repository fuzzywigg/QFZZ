"""Dataset Data Structures"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class DatasetLicense(Enum):
    """Supported open source licenses"""

    GPL = "GPL"
    MIT = "MIT"
    APACHE = "Apache"
    BSD = "BSD"
    CC_BY = "CC-BY"
    CC_BY_SA = "CC-BY-SA"
    PUBLIC_DOMAIN = "Public Domain"


@dataclass
class Dataset:
    """Represents a GNU/OPENSOURCE dataset

    Attributes:
        id: Unique dataset identifier
        name: Dataset name
        description: Dataset description
        license: Open source license type
        source_url: URL to dataset source
        quality_score: Quality score from 0.0 to 1.0
        category: Dataset category (e.g., "music", "conversation", "knowledge")
        size_mb: Dataset size in megabytes
        created_at: Creation timestamp
        downloads: Number of downloads
        community_rating: Community rating score (0.0-1.0)
        verified: Whether dataset is blockchain verified
    """

    id: str
    name: str
    description: str
    license: DatasetLicense
    source_url: str
    quality_score: float
    category: str
    size_mb: float
    created_at: datetime = field(default_factory=datetime.now)
    downloads: int = 0
    community_rating: float = 0.0
    verified: bool = False
