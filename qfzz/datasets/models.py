"""
Data models for dataset management.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum


class LicenseType(Enum):
    """Supported open source license types."""
    CC0 = "CC0"
    CC_BY = "CC-BY"
    CC_BY_SA = "CC-BY-SA"
    CC_BY_NC = "CC-BY-NC"
    CC_BY_NC_SA = "CC-BY-NC-SA"
    MIT = "MIT"
    APACHE_2 = "Apache-2.0"
    GPL_3 = "GPL-3.0"
    PUBLIC_DOMAIN = "Public-Domain"


@dataclass
class DatasetLicense:
    """
    License information for a dataset.
    
    Attributes:
        license_type: Type of license
        license_url: URL to license text
        attribution_required: Whether attribution is required
        commercial_use: Whether commercial use is allowed
        derivative_works: Whether derivative works are allowed
        share_alike: Whether derivative works must use same license
        additional_terms: Additional license terms
    """
    
    license_type: str
    license_url: str
    attribution_required: bool = True
    commercial_use: bool = True
    derivative_works: bool = True
    share_alike: bool = False
    additional_terms: str = ""
    
    def is_compatible_with(self, allowed_licenses: List[str]) -> bool:
        """
        Check if license is compatible with allowed licenses.
        
        Args:
            allowed_licenses: List of allowed license types
            
        Returns:
            True if compatible, False otherwise
        """
        return self.license_type in allowed_licenses
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert license to dictionary."""
        return {
            'license_type': self.license_type,
            'license_url': self.license_url,
            'attribution_required': self.attribution_required,
            'commercial_use': self.commercial_use,
            'derivative_works': self.derivative_works,
            'share_alike': self.share_alike,
            'additional_terms': self.additional_terms
        }


@dataclass
class Dataset:
    """
    Dataset containing music tracks and metadata.
    
    Attributes:
        dataset_id: Unique dataset identifier
        name: Dataset name
        description: Dataset description
        version: Dataset version
        license: Dataset license information
        creator_id: Creator identifier
        tracks: List of track dictionaries
        metadata: Additional metadata
        quality_score: Quality score (0.0-1.0)
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    
    dataset_id: str
    name: str
    description: str
    version: str
    license: DatasetLicense
    creator_id: str
    tracks: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    quality_score: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def __post_init__(self):
        """Validate dataset after initialization."""
        self.validate()
    
    def validate(self) -> None:
        """
        Validate dataset parameters.
        
        Raises:
            ValueError: If any parameter is invalid
        """
        if not self.dataset_id:
            raise ValueError("dataset_id must be non-empty")
        
        if not self.name:
            raise ValueError("name must be non-empty")
        
        if not self.version:
            raise ValueError("version must be non-empty")
        
        if not self.creator_id:
            raise ValueError("creator_id must be non-empty")
        
        if not 0.0 <= self.quality_score <= 1.0:
            raise ValueError("quality_score must be between 0.0 and 1.0")
    
    def add_track(self, track: Dict[str, Any]) -> None:
        """
        Add a track to the dataset.
        
        Args:
            track: Track dictionary with metadata
        """
        self.tracks.append(track)
        self.updated_at = datetime.now().isoformat()
    
    def remove_track(self, track_id: str) -> bool:
        """
        Remove a track from the dataset.
        
        Args:
            track_id: Track identifier
            
        Returns:
            True if removed, False if not found
        """
        initial_len = len(self.tracks)
        self.tracks = [t for t in self.tracks if t.get('track_id') != track_id]
        
        if len(self.tracks) < initial_len:
            self.updated_at = datetime.now().isoformat()
            return True
        
        return False
    
    def get_track_count(self) -> int:
        """Get number of tracks in dataset."""
        return len(self.tracks)
    
    def get_total_duration(self) -> int:
        """
        Get total duration of all tracks in seconds.
        
        Returns:
            Total duration in seconds
        """
        return sum(track.get('duration', 0) for track in self.tracks)
    
    def get_genres(self) -> List[str]:
        """
        Get unique genres in dataset.
        
        Returns:
            List of unique genre names
        """
        genres = set()
        for track in self.tracks:
            if 'genre' in track:
                genres.add(track['genre'])
        return sorted(list(genres))
    
    def get_artists(self) -> List[str]:
        """
        Get unique artists in dataset.
        
        Returns:
            List of unique artist names
        """
        artists = set()
        for track in self.tracks:
            if 'artist' in track:
                artists.add(track['artist'])
        return sorted(list(artists))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert dataset to dictionary."""
        return {
            'dataset_id': self.dataset_id,
            'name': self.name,
            'description': self.description,
            'version': self.version,
            'license': self.license.to_dict(),
            'creator_id': self.creator_id,
            'tracks': self.tracks,
            'metadata': self.metadata,
            'quality_score': self.quality_score,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'track_count': self.get_track_count(),
            'total_duration': self.get_total_duration()
        }
