"""
Edge Device Optimization
Supports running AI radio station on edge devices with 6G connectivity
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class EdgeDeviceConfig:
    """Configuration for edge device deployment"""
    device_id: str
    device_type: str  # e.g., "smartphone", "smart_speaker", "embedded"
    max_memory_mb: int = 512
    max_model_size_mb: int = 100
    enable_6g: bool = False
    network_bandwidth_mbps: int = 100
    storage_available_gb: float = 1.0
    

class EdgeOptimizer:
    """
    Optimizes QFZZ for edge device deployment
    
    Features:
    - Model size optimization
    - Memory management
    - 6G network optimization
    - Bandwidth-aware streaming
    - Local caching
    """
    
    def __init__(self, config: EdgeDeviceConfig):
        self.config = config
        self.cache: Dict[str, Any] = {}
        self.compression_enabled = True
        
        logger.info(f"Edge optimizer initialized for {config.device_type} (6G: {config.enable_6g})")
        
    def optimize_model(self, model_size_mb: float) -> Dict[str, Any]:
        """
        Optimize LLM for edge device constraints
        
        Args:
            model_size_mb: Original model size
            
        Returns:
            Optimization recommendations
        """
        recommendations = {
            'original_size_mb': model_size_mb,
            'optimizations': []
        }
        
        if model_size_mb > self.config.max_model_size_mb:
            recommendations['optimizations'].append('quantization')
            recommendations['optimizations'].append('pruning')
            recommendations['target_size_mb'] = self.config.max_model_size_mb
        else:
            recommendations['target_size_mb'] = model_size_mb
            recommendations['status'] = 'no_optimization_needed'
            
        return recommendations
        
    def optimize_streaming(self, bitrate_kbps: int) -> Dict[str, Any]:
        """
        Optimize audio streaming for current network conditions
        
        Args:
            bitrate_kbps: Desired audio bitrate
            
        Returns:
            Streaming configuration
        """
        max_bitrate = self.config.network_bandwidth_mbps * 1000 * 0.7  # 70% of bandwidth
        
        if self.config.enable_6g:
            # 6G provides high bandwidth and low latency
            recommended_bitrate = min(bitrate_kbps, 320)  # High quality
            buffer_ms = 100  # Low latency buffer
        else:
            recommended_bitrate = min(bitrate_kbps, max_bitrate)
            buffer_ms = 1000  # Conservative buffer
            
        return {
            'recommended_bitrate_kbps': int(recommended_bitrate),
            'buffer_ms': buffer_ms,
            'enable_compression': self.compression_enabled,
            'adaptive_quality': not self.config.enable_6g
        }
        
    def can_cache_locally(self, size_mb: float) -> bool:
        """
        Check if content can be cached locally
        
        Args:
            size_mb: Size of content to cache
            
        Returns:
            True if caching is possible
        """
        current_cache_size = sum(
            item.get('size_mb', 0) 
            for item in self.cache.values()
        )
        
        available_space_mb = self.config.storage_available_gb * 1024
        
        return (current_cache_size + size_mb) < available_space_mb * 0.8  # Use up to 80%
        
    def add_to_cache(self, key: str, data: Any, size_mb: float):
        """
        Add content to local cache
        
        Args:
            key: Cache key
            data: Data to cache
            size_mb: Size of data
        """
        if self.can_cache_locally(size_mb):
            self.cache[key] = {
                'data': data,
                'size_mb': size_mb
            }
            logger.debug(f"Cached {key} ({size_mb}MB)")
        else:
            logger.warning(f"Cannot cache {key}: insufficient storage")
            
    def get_from_cache(self, key: str) -> Optional[Any]:
        """Get content from cache"""
        if key in self.cache:
            return self.cache[key]['data']
        return None
        
    def clear_cache(self):
        """Clear local cache"""
        self.cache.clear()
        logger.info("Cache cleared")
        
    def get_device_status(self) -> Dict[str, Any]:
        """Get edge device status"""
        cache_size = sum(item.get('size_mb', 0) for item in self.cache.values())
        
        return {
            'device_id': self.config.device_id,
            'device_type': self.config.device_type,
            '6g_enabled': self.config.enable_6g,
            'cache_size_mb': cache_size,
            'cache_items': len(self.cache),
            'memory_limit_mb': self.config.max_memory_mb,
            'network_bandwidth_mbps': self.config.network_bandwidth_mbps
        }
