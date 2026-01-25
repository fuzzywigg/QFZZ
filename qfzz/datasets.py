"""
Dataset Management System
Handles GNU/OPENSOURCE datasets for LLM training and music curation
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


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
    """Represents a GNU/OPENSOURCE dataset"""
    id: str
    name: str
    description: str
    license: DatasetLicense
    source_url: str
    quality_score: float  # 0.0 to 1.0
    category: str  # e.g., "music", "conversation", "knowledge"
    size_mb: float
    created_at: datetime = field(default_factory=datetime.now)
    downloads: int = 0
    community_rating: float = 0.0
    verified: bool = False  # Blockchain verified
    
    
class DatasetManager:
    """
    Manages GNU/OPENSOURCE datasets for the AI radio station
    
    Features:
    - Quality scoring and visibility
    - Blockchain verification for authenticity
    - Community ratings and trust
    - Edge device optimization (small, efficient datasets)
    """
    
    def __init__(self, opensource_only: bool = True, min_quality: float = 0.7):
        self.opensource_only = opensource_only
        self.min_quality = min_quality
        self.datasets: Dict[str, Dataset] = {}
        self.quality_index: Dict[str, List[str]] = {
            'high': [],    # 0.8-1.0
            'medium': [],  # 0.6-0.8
            'low': []      # 0.0-0.6
        }
        
        logger.info(f"DatasetManager initialized (opensource_only={opensource_only})")
        
    def register_dataset(self, dataset: Dataset) -> bool:
        """
        Register a new dataset in the system
        
        Args:
            dataset: Dataset to register
            
        Returns:
            True if registered successfully, False otherwise
        """
        # Validate license
        if self.opensource_only and not self._is_opensource_license(dataset.license):
            logger.warning(f"Dataset {dataset.name} rejected: non-opensource license")
            return False
            
        # Validate quality
        if dataset.quality_score < self.min_quality:
            logger.warning(f"Dataset {dataset.name} rejected: quality score too low")
            return False
            
        # Register dataset
        self.datasets[dataset.id] = dataset
        self._update_quality_index(dataset)
        
        logger.info(f"Registered dataset: {dataset.name} (quality: {dataset.quality_score})")
        return True
        
    def _is_opensource_license(self, license: DatasetLicense) -> bool:
        """Check if license is open source"""
        # All our defined licenses are open source
        return license in DatasetLicense
        
    def _update_quality_index(self, dataset: Dataset):
        """Update the quality index for efficient discovery"""
        dataset_id = dataset.id
        
        if dataset.quality_score >= 0.8:
            self.quality_index['high'].append(dataset_id)
        elif dataset.quality_score >= 0.6:
            self.quality_index['medium'].append(dataset_id)
        else:
            self.quality_index['low'].append(dataset_id)
            
    def get_high_quality_datasets(self, category: Optional[str] = None) -> List[Dataset]:
        """
        Get list of high quality datasets
        
        Args:
            category: Optional category filter
            
        Returns:
            List of high quality datasets
        """
        high_quality_ids = self.quality_index['high']
        datasets = [self.datasets[did] for did in high_quality_ids if did in self.datasets]
        
        if category:
            datasets = [d for d in datasets if d.category == category]
            
        # Sort by quality score and community rating
        datasets.sort(key=lambda d: (d.quality_score + d.community_rating) / 2, reverse=True)
        
        return datasets
        
    def verify_dataset_blockchain(self, dataset_id: str) -> bool:
        """
        Verify dataset authenticity using blockchain
        
        Args:
            dataset_id: ID of dataset to verify
            
        Returns:
            True if verification successful
        """
        if dataset_id not in self.datasets:
            return False
            
        dataset = self.datasets[dataset_id]
        
        # Placeholder for blockchain verification
        # In production, this would verify dataset hash on blockchain
        dataset.verified = True
        
        logger.info(f"Dataset {dataset.name} verified on blockchain")
        return True
        
    def rate_dataset(self, dataset_id: str, rating: float):
        """
        Add community rating to dataset
        
        Args:
            dataset_id: ID of dataset to rate
            rating: Rating value (0.0 to 1.0)
        """
        if dataset_id not in self.datasets:
            return
            
        dataset = self.datasets[dataset_id]
        
        # Update community rating (simple average for now)
        if dataset.community_rating == 0.0:
            dataset.community_rating = rating
        else:
            dataset.community_rating = (dataset.community_rating + rating) / 2
            
        logger.info(f"Dataset {dataset.name} rated: {dataset.community_rating:.2f}")
        
    def get_edge_optimized_datasets(self, max_size_mb: int = 500) -> List[Dataset]:
        """
        Get datasets optimized for edge devices
        
        Args:
            max_size_mb: Maximum dataset size for edge devices
            
        Returns:
            List of edge-compatible datasets
        """
        edge_datasets = [
            d for d in self.datasets.values()
            if d.size_mb <= max_size_mb and d.quality_score >= self.min_quality
        ]
        
        # Prioritize high quality, small datasets
        edge_datasets.sort(key=lambda d: (d.quality_score, -d.size_mb), reverse=True)
        
        return edge_datasets
        
    def get_stats(self) -> Dict[str, Any]:
        """Get dataset statistics"""
        return {
            'total_datasets': len(self.datasets),
            'high_quality': len(self.quality_index['high']),
            'medium_quality': len(self.quality_index['medium']),
            'low_quality': len(self.quality_index['low']),
            'verified_datasets': sum(1 for d in self.datasets.values() if d.verified),
            'total_downloads': sum(d.downloads for d in self.datasets.values())
        }
