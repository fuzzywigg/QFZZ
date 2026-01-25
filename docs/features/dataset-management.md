# Dataset Management: Quality Scoring and License Validation

The `DatasetManager` provides comprehensive music dataset management with intelligent quality scoring, license validation, and metadata consistency checking. It ensures datasets meet quality standards and comply with legal requirements before usage.

## Overview

The DatasetManager enables:

- **Quality Scoring**: Multi-factor scoring system based on 5 key metrics
- **License Validation**: Automatic verification of license compatibility
- **Metadata Analysis**: Comprehensive metadata completeness and consistency checks
- **Dataset Organization**: Efficient management of large dataset collections
- **Content Diversity**: Measurement of genre, artist, and style diversity
- **Statistical Insights**: Detailed analytics about dataset characteristics

!!! info "Quality Assurance"
    The quality scoring system uses a weighted multi-factor approach to objectively assess dataset quality. This ensures your recommendation engine trains on high-quality data.

## Architecture

### Core Components

The DatasetManager consists of three main components:

```python
from qfzz.datasets.manager import DatasetManager
from qfzz.datasets.models import Dataset, DatasetLicense, LicenseType

# Initialize with allowed licenses
manager = DatasetManager(
    allowed_licenses=['CC-BY', 'CC-BY-SA', 'CC0']
)
```

**Key Classes**:

| Component | Purpose | Role |
|-----------|---------|------|
| `DatasetManager` | Orchestrator | Manages datasets, scoring, validation |
| `Dataset` | Data container | Holds tracks and metadata |
| `DatasetLicense` | License info | Validates license compatibility |

## Dataset Models

### Creating Datasets

Create a dataset with tracks and metadata:

```python
from datetime import datetime

# Create dataset with license
license = DatasetLicense(
    license_type='CC-BY',
    license_url='https://creativecommons.org/licenses/by/4.0/',
    attribution_required=True,
    commercial_use=True,
    derivative_works=True,
    share_alike=False
)

dataset = Dataset(
    dataset_id='dataset_electronic_2024',
    name='Electronic Music Collection',
    description='High-quality electronic and dance tracks',
    version='1.0.0',
    license=license,
    creator_id='curator_001',
    tracks=[
        {
            'track_id': 'track_001',
            'title': 'Neon Dreams',
            'artist': 'SynthWave Artist',
            'genre': 'electronic',
            'mood': 'energetic',
            'energy': 0.8,
            'tempo': 120,
            'duration': 240,
            'album': 'Digital Horizons',
            'year': 2024
        },
        # ... more tracks
    ]
)

# Add to manager
if manager.add_dataset(dataset):
    print("✓ Dataset added successfully")
    print(f"Quality Score: {dataset.quality_score:.3f}")
else:
    print("✗ Dataset rejected due to license incompatibility")
```

!!! note "License Compatibility"
    The manager validates that dataset licenses are compatible with the allowed licenses list before acceptance. Incompatible licenses are automatically rejected.

### Track Structure

Each track in a dataset should include:

```python
track = {
    # Required fields
    'track_id': 'unique_id',
    'title': 'Track Title',
    'artist': 'Artist Name',
    'genre': 'electronic',
    'duration': 300,  # seconds
    
    # Recommended fields
    'mood': 'energetic',
    'energy': 0.7,  # 0.0-1.0
    'tempo': 128,   # BPM
    'album': 'Album Name',
    'year': 2024,
    
    # Optional fields
    'isrc': 'USRC17607839',
    'composer': 'Composer Name',
    'key': 'C',
    'key_confidence': 0.95
}
```

## Quality Scoring System

### Understanding Quality Factors

The quality score is calculated from 5 weighted factors:

```python
def calculate_quality_score(dataset):
    """
    Quality Score = (
        metadata_completeness * 0.30 +
        data_consistency * 0.25 +
        dataset_size * 0.20 +
        diversity * 0.15 +
        license_permissiveness * 0.10
    )
    """
    pass
```

**Quality Factor Weights**:

| Factor | Weight | Description | Impact |
|--------|--------|-------------|--------|
| Metadata Completeness | 30% | Richness of track metadata | Highest |
| Data Consistency | 25% | Uniformity and validity of data | High |
| Dataset Size | 20% | Number and duration of tracks | Moderate |
| Diversity | 15% | Genre/artist variety | Moderate |
| License Permissiveness | 10% | Freedom of use and modification | Low |

### 1. Metadata Completeness (30% weight)

Measures the completeness and richness of track metadata:

```python
required_fields = ['title', 'artist', 'genre', 'duration']
optional_fields = ['album', 'year', 'mood', 'energy', 'tempo']

# Scoring formula:
# Required fields: 70% of completeness score
# Optional fields: 30% of completeness score

def analyze_metadata_completeness(dataset):
    """Analyze metadata completeness of a dataset."""
    
    if not dataset.tracks:
        return 0.0
    
    scores = []
    for track in dataset.tracks:
        # Count required fields
        required_present = sum(1 for field in required_fields 
                              if field in track and track[field])
        required_score = (required_present / len(required_fields)) * 0.7
        
        # Count optional fields
        optional_present = sum(1 for field in optional_fields 
                              if field in track and track[field])
        optional_score = (optional_present / len(optional_fields)) * 0.3
        
        track_score = required_score + optional_score
        scores.append(track_score)
    
    return sum(scores) / len(scores)

completeness = analyze_metadata_completeness(dataset)
print(f"Metadata Completeness: {completeness:.1%}")
```

!!! tip "Improve Completeness"
    - Add all required fields to every track
    - Include optional fields like mood, energy, and tempo
    - Use consistent field names and formats

### 2. Data Consistency (25% weight)

Measures uniformity and validity of data across tracks:

```python
def analyze_data_consistency(dataset):
    """Analyze data consistency of a dataset."""
    
    if not dataset.tracks:
        return 0.0
    
    # Field consistency
    sample_fields = set(dataset.tracks[0].keys())
    field_scores = []
    
    for track in dataset.tracks:
        track_fields = set(track.keys())
        overlap = len(sample_fields & track_fields) / len(sample_fields)
        field_scores.append(overlap)
    
    field_consistency = sum(field_scores) / len(field_scores)
    
    # Value validity
    validity_scores = []
    for track in dataset.tracks:
        score = 1.0
        
        # Validate duration
        if 'duration' in track and track['duration'] <= 0:
            score -= 0.2
        
        # Validate energy
        if 'energy' in track and not 0.0 <= track['energy'] <= 1.0:
            score -= 0.2
        
        # Validate tempo
        if 'tempo' in track and not 40 <= track['tempo'] <= 300:
            score -= 0.2
        
        validity_scores.append(max(0.0, score))
    
    value_validity = sum(validity_scores) / len(validity_scores)
    
    return (field_consistency * 0.5 + value_validity * 0.5)

consistency = analyze_data_consistency(dataset)
print(f"Data Consistency: {consistency:.1%}")
```

**Consistency Checks**:

| Check | Impact | Resolution |
|-------|--------|-----------|
| Missing required fields | -20% per field | Add missing fields |
| Invalid duration (≤0) | -20% | Ensure positive duration |
| Invalid energy (not 0-1) | -20% | Normalize energy to 0-1 |
| Inconsistent field structure | -percentage | Standardize track structure |

### 3. Dataset Size (20% weight)

Evaluates the scale and scope of the dataset:

```python
def analyze_dataset_size(dataset):
    """Analyze size scoring for a dataset."""
    
    track_count = len(dataset.tracks)
    
    # Logarithmic scoring
    if track_count == 0:
        return 0.0
    elif track_count < 10:
        return 0.2   # Very small
    elif track_count < 50:
        return 0.4   # Small
    elif track_count < 100:
        return 0.6   # Medium
    elif track_count < 500:
        return 0.8   # Large
    else:
        return 1.0   # Very large

size_score = analyze_dataset_size(dataset)
print(f"Dataset Size Score: {size_score:.1%}")
```

**Size Tiers**:

| Tracks | Score | Category | Notes |
|--------|-------|----------|-------|
| 0-10 | 0.2 | Tiny | Too small for reliable recommendations |
| 10-50 | 0.4 | Small | Adequate for focused use |
| 50-100 | 0.6 | Medium | Good for most applications |
| 100-500 | 0.8 | Large | Very useful, diverse |
| 500+ | 1.0 | Very Large | Excellent for training |

### 4. Diversity (15% weight)

Measures variety of genres, artists, and styles:

```python
def analyze_diversity(dataset):
    """Analyze diversity of a dataset."""
    
    if not dataset.tracks:
        return 0.0
    
    # Genre diversity
    genres = set(track.get('genre') for track in dataset.tracks if 'genre' in track)
    
    # Artist diversity
    artists = set(track.get('artist') for track in dataset.tracks if 'artist' in track)
    
    track_count = len(dataset.tracks)
    
    # Scores
    genre_diversity = min(1.0, len(genres) / 10.0)
    artist_diversity = min(1.0, len(artists) / max(1, track_count / 5))
    
    return (genre_diversity * 0.5 + artist_diversity * 0.5)

diversity = analyze_diversity(dataset)
print(f"Diversity Score: {diversity:.1%}")
```

!!! tip "Improve Diversity"
    - Include tracks from multiple genres
    - Include tracks from many different artists
    - Aim for 10+ genres and artists with even distribution
    - Avoid over-representation of single genres or artists

### 5. License Permissiveness (10% weight)

Evaluates freedom of use and modification:

```python
def analyze_license_permissiveness(license):
    """Analyze license permissiveness scoring."""
    
    score = 0.5  # Base score
    
    # Commercial use allowed: +0.2
    if license.commercial_use:
        score += 0.2
    
    # Derivative works allowed: +0.2
    if license.derivative_works:
        score += 0.2
    
    # No share-alike requirement: +0.1
    if not license.share_alike:
        score += 0.1
    
    return min(1.0, score)

license_score = analyze_license_permissiveness(dataset.license)
print(f"License Permissiveness: {license_score:.1%}")
```

**License Scoring**:

| License Type | Commercial | Derivatives | Share-Alike | Score |
|--------------|------------|-------------|-------------|-------|
| CC0 | Yes | Yes | No | 0.9 |
| CC-BY | Yes | Yes | No | 0.9 |
| CC-BY-SA | Yes | Yes | Yes | 0.7 |
| CC-BY-NC | No | Yes | No | 0.5 |
| Proprietary | No | No | No | 0.1 |

## License Validation

### Supported Licenses

```python
from qfzz.datasets.models import LicenseType

supported_licenses = [
    LicenseType.CC0,                    # Public domain
    LicenseType.CC_BY,                  # Attribution required
    LicenseType.CC_BY_SA,               # Attribution + Share-Alike
    LicenseType.CC_BY_NC,               # Attribution + Non-Commercial
    LicenseType.CC_BY_NC_SA,            # All restrictions
    LicenseType.MIT,                    # Permissive code license
    LicenseType.APACHE_2,               # Permissive code license
    LicenseType.GPL_3,                  # Copyleft code license
    LicenseType.PUBLIC_DOMAIN           # No restrictions
]
```

### License Compatibility

```python
# Define allowed licenses for your use case
allowed_licenses_commercial = ['CC-BY', 'CC0', 'MIT', 'Apache-2.0']
allowed_licenses_research = ['CC-BY', 'CC-BY-SA', 'CC0', 'GPL-3.0']

manager_commercial = DatasetManager(allowed_licenses=allowed_licenses_commercial)
manager_research = DatasetManager(allowed_licenses=allowed_licenses_research)

# Validate license
license = DatasetLicense(
    license_type='CC-BY',
    license_url='https://creativecommons.org/licenses/by/4.0/',
    attribution_required=True,
    commercial_use=True,
    derivative_works=True,
    share_alike=False
)

is_valid = manager_commercial.validate_license(license)
print(f"License valid for commercial use: {is_valid}")
```

!!! warning "License Compliance"
    Always ensure datasets comply with license requirements:
    - Provide attribution when required
    - Respect non-commercial use restrictions
    - Include license text with distributed datasets
    - Track derivative works for share-alike licenses

## Managing Datasets

### Add Datasets

```python
manager = DatasetManager()

# Create and add a dataset
dataset = Dataset(
    dataset_id='jazz_collection_2024',
    name='Jazz Standards Collection',
    description='Curated jazz standards for music analysis',
    version='2.0.0',
    license=DatasetLicense(
        license_type='CC-BY',
        license_url='https://creativecommons.org/licenses/by/4.0/',
        attribution_required=True,
        commercial_use=True,
        derivative_works=True,
        share_alike=False
    ),
    creator_id='jazz_curator'
)

# Add tracks
for i in range(100):
    dataset.add_track({
        'track_id': f'jazz_{i:03d}',
        'title': f'Jazz Track {i}',
        'artist': f'Jazz Artist {i % 10}',
        'genre': 'jazz',
        'mood': 'mellow' if i % 2 else 'upbeat',
        'energy': 0.3 + (i % 7) * 0.1,
        'tempo': 80 + (i % 60),
        'duration': 180 + (i % 120),
        'album': f'Album {i // 20}'
    })

# Add to manager
success = manager.add_dataset(dataset)
print(f"Dataset added: {success}")
print(f"Quality Score: {dataset.quality_score:.3f}")
```

### Remove Datasets

```python
# Remove a dataset
removed = manager.remove_dataset('jazz_collection_2024')

if removed:
    print("✓ Dataset removed")
else:
    print("✗ Dataset not found")
```

### Retrieve Datasets

```python
# Get specific dataset
dataset = manager.get_dataset('jazz_collection_2024')

if dataset:
    print(f"Dataset: {dataset.name}")
    print(f"Tracks: {dataset.get_track_count()}")
    print(f"Quality Score: {dataset.quality_score:.3f}")
else:
    print("Dataset not found")
```

## Querying Datasets

### List All Datasets

```python
# Get all datasets
all_datasets = manager.list_datasets()

# Get high-quality datasets only
high_quality = manager.list_datasets(min_quality=0.7)

# Print summary
for dataset in high_quality:
    print(f"{dataset.name}: {dataset.quality_score:.3f} "
          f"({dataset.get_track_count()} tracks)")
```

### Filter by Quality

```python
# Get datasets with specific quality thresholds
premium_datasets = manager.list_datasets(min_quality=0.8)
acceptable_datasets = manager.list_datasets(min_quality=0.6)
all_datasets = manager.list_datasets(min_quality=0.0)

print(f"Premium datasets: {len(premium_datasets)}")
print(f"Acceptable datasets: {len(acceptable_datasets)}")
print(f"All datasets: {len(all_datasets)}")
```

## Dataset Analysis

### Get Statistics

```python
stats = manager.get_statistics()

print("Dataset Manager Statistics:")
print(f"  Total Datasets: {stats['total_datasets']}")
print(f"  Total Tracks: {stats['total_tracks']}")
print(f"  Average Quality: {stats['average_quality_score']:.3f}")
print(f"  Unique Genres: {stats['unique_genres']}")
print(f"  Unique Artists: {stats['unique_artists']}")
print(f"  Allowed Licenses: {', '.join(stats['allowed_licenses'])}")
```

### Detailed Dataset Analysis

```python
def analyze_dataset(dataset):
    """Perform comprehensive dataset analysis."""
    
    return {
        'name': dataset.name,
        'track_count': dataset.get_track_count(),
        'total_duration_hours': dataset.get_total_duration() / 3600,
        'quality_score': dataset.quality_score,
        'genres': dataset.get_genres(),
        'artists': dataset.get_artists(),
        'unique_genres': len(dataset.get_genres()),
        'unique_artists': len(dataset.get_artists()),
        'license': dataset.license.license_type,
        'created': dataset.created_at,
        'updated': dataset.updated_at
    }

analysis = analyze_dataset(dataset)
print(f"Dataset Analysis: {analysis['name']}")
print(f"  Tracks: {analysis['track_count']}")
print(f"  Duration: {analysis['total_duration_hours']:.1f} hours")
print(f"  Quality: {analysis['quality_score']:.3f}")
print(f"  Genres: {analysis['unique_genres']}")
print(f"  Artists: {analysis['unique_artists']}")
```

## Track Management

### Adding Tracks

```python
# Add individual tracks
dataset.add_track({
    'track_id': 'new_track_001',
    'title': 'New Jazz Standard',
    'artist': 'New Artist',
    'genre': 'jazz',
    'energy': 0.5,
    'mood': 'contemplative',
    'tempo': 90,
    'duration': 240,
    'album': 'New Album',
    'year': 2024
})

# Bulk add tracks
new_tracks = [
    {'track_id': f'track_{i}', 'title': f'Track {i}', ...}
    for i in range(100)
]

for track in new_tracks:
    dataset.add_track(track)

print(f"Dataset now has {dataset.get_track_count()} tracks")
```

### Removing Tracks

```python
# Remove a track
removed = dataset.remove_track('track_001')

if removed:
    print("✓ Track removed")
    # Re-calculate quality score
    quality = manager.calculate_quality_score(dataset)
    dataset.quality_score = quality
else:
    print("✗ Track not found")
```

### Track Validation

```python
def validate_track(track):
    """Validate track data integrity."""
    
    required = ['track_id', 'title', 'artist', 'genre', 'duration']
    issues = []
    
    # Check required fields
    for field in required:
        if field not in track or not track[field]:
            issues.append(f"Missing required field: {field}")
    
    # Check value ranges
    if 'energy' in track and not 0.0 <= track['energy'] <= 1.0:
        issues.append("Energy must be between 0.0 and 1.0")
    
    if 'duration' in track and track['duration'] <= 0:
        issues.append("Duration must be positive")
    
    if 'tempo' in track and not (40 <= track['tempo'] <= 300):
        issues.append("Tempo should be between 40 and 300 BPM")
    
    return {
        'valid': len(issues) == 0,
        'issues': issues
    }

# Validate a track
result = validate_track(dataset.tracks[0])
if result['valid']:
    print("✓ Track is valid")
else:
    for issue in result['issues']:
        print(f"✗ {issue}")
```

## Advanced Patterns

### Dataset Merging

```python
def merge_datasets(manager, dataset1_id, dataset2_id, new_id):
    """Merge two datasets into one."""
    
    ds1 = manager.get_dataset(dataset1_id)
    ds2 = manager.get_dataset(dataset2_id)
    
    if not ds1 or not ds2:
        return None
    
    # Create merged dataset
    merged = Dataset(
        dataset_id=new_id,
        name=f"{ds1.name} + {ds2.name}",
        description=f"Merged from {dataset1_id} and {dataset2_id}",
        version='1.0.0',
        license=ds1.license,  # Use first dataset's license
        creator_id=ds1.creator_id,
        tracks=ds1.tracks + ds2.tracks
    )
    
    # Calculate quality for merged dataset
    quality = manager.calculate_quality_score(merged)
    merged.quality_score = quality
    
    return merged

# Merge datasets
merged = merge_datasets(manager, 'dataset1', 'dataset2', 'merged_dataset')
if merged:
    manager.add_dataset(merged)
    print(f"✓ Merged dataset quality: {merged.quality_score:.3f}")
```

### Quality Improvement Recommendations

```python
def get_quality_recommendations(dataset):
    """Generate recommendations to improve dataset quality."""
    
    recommendations = []
    
    # Check size
    if dataset.get_track_count() < 50:
        recommendations.append("Add more tracks (currently < 50)")
    
    # Check metadata completeness
    completeness_score = 0
    required_fields = ['title', 'artist', 'genre', 'duration']
    optional_fields = ['album', 'year', 'mood', 'energy', 'tempo']
    
    for track in dataset.tracks:
        required_present = sum(1 for f in required_fields if f in track and track[f])
        if required_present < len(required_fields):
            recommendations.append(f"Track {track.get('track_id')} missing required fields")
            break
    
    for track in dataset.tracks:
        optional_present = sum(1 for f in optional_fields if f in track and track[f])
        if optional_present < 2:
            recommendations.append("Add more optional fields (mood, energy, tempo) to tracks")
            break
    
    # Check diversity
    genres = dataset.get_genres()
    if len(genres) < 5:
        recommendations.append(f"Increase genre diversity (currently {len(genres)} genres)")
    
    artists = dataset.get_artists()
    if len(artists) < dataset.get_track_count() / 5:
        recommendations.append("Increase artist diversity")
    
    return recommendations

# Get recommendations
recs = get_quality_recommendations(dataset)
for rec in recs:
    print(f"💡 {rec}")
```

### Dataset Versioning

```python
def version_dataset(manager, dataset_id, new_version):
    """Create a new version of a dataset."""
    
    original = manager.get_dataset(dataset_id)
    if not original:
        return None
    
    # Create versioned copy
    versioned = Dataset(
        dataset_id=f"{dataset_id}_v{new_version}",
        name=f"{original.name} (v{new_version})",
        description=original.description,
        version=new_version,
        license=original.license,
        creator_id=original.creator_id,
        tracks=original.tracks.copy(),
        metadata={**original.metadata, 'parent_version': dataset_id}
    )
    
    quality = manager.calculate_quality_score(versioned)
    versioned.quality_score = quality
    
    return versioned

# Create new version
v2 = version_dataset(manager, 'dataset_001', '2.0.0')
if v2:
    manager.add_dataset(v2)
    print(f"✓ Created version {v2.version}")
```

## Integration with Other Features

### With Blockchain Trust Network

```python
from qfzz.blockchain.trust_network import BlockchainTrustNetwork

network = BlockchainTrustNetwork()

# Record dataset quality on blockchain
for dataset in manager.list_datasets(min_quality=0.7):
    network.add_trust_record(
        content_id=dataset.dataset_id,
        creator_id=dataset.creator_id,
        initial_score=dataset.quality_score,
        metadata={
            'dataset_name': dataset.name,
            'tracks': dataset.get_track_count(),
            'genres': len(dataset.get_genres())
        }
    )

# Mine records
network.mine_pending_records()
```

### With Edge Optimization

```python
from qfzz.edge.optimizer import EdgeOptimizer

optimizer = EdgeOptimizer()

def get_dataset_for_device(manager, device_id):
    """Select appropriate dataset for device capabilities."""
    
    device = optimizer.get_device_config(device_id)
    if not device:
        return None
    
    # Select dataset based on device
    if device.device_type.value == 'smartphone':
        # Smaller, high-quality datasets
        datasets = manager.list_datasets(min_quality=0.8)
    else:
        # All datasets
        datasets = manager.list_datasets(min_quality=0.6)
    
    # Prefer smaller datasets for bandwidth-constrained devices
    if device.bandwidth_mbps < 5.0:
        datasets = sorted(datasets, key=lambda d: d.get_track_count())
    
    return datasets[0] if datasets else None
```

## Best Practices

### 1. Ensure Complete Metadata

```python
# Good: Rich metadata
track = {
    'track_id': 'track_001',
    'title': 'Song Name',
    'artist': 'Artist Name',
    'genre': 'electronic',
    'mood': 'energetic',
    'energy': 0.8,
    'tempo': 128,
    'duration': 240,
    'album': 'Album Name',
    'year': 2024
}

# Suboptimal: Minimal metadata
track = {
    'track_id': 'track_001',
    'title': 'Song',
    'artist': 'Artist'
}
```

### 2. Maintain Data Consistency

```python
# Ensure all tracks have consistent structure
required_structure = ['track_id', 'title', 'artist', 'genre', 'duration']

for track in dataset.tracks:
    for field in required_structure:
        if field not in track:
            print(f"⚠️ Track missing {field}")
```

### 3. Validate Licenses Upfront

```python
# Always validate license before adding dataset
license = DatasetLicense(...)
if manager.validate_license(license):
    manager.add_dataset(dataset)
else:
    print("✗ License not compatible")
```

### 4. Monitor Quality Scores

```python
# Regularly check quality scores
stats = manager.get_statistics()

if stats['average_quality_score'] < 0.6:
    print("⚠️ Average quality is low - consider dataset review")
```

## Performance Optimization

### Efficient Querying

```python
# Cached queries
high_quality_cache = {}

def get_high_quality_datasets(manager, threshold=0.8):
    """Get high-quality datasets with caching."""
    
    if threshold not in high_quality_cache:
        high_quality_cache[threshold] = manager.list_datasets(min_quality=threshold)
    
    return high_quality_cache[threshold]
```

### Batch Operations

```python
# Batch dataset operations
def batch_add_datasets(manager, dataset_list):
    """Add multiple datasets efficiently."""
    
    added = 0
    rejected = 0
    
    for dataset in dataset_list:
        if manager.add_dataset(dataset):
            added += 1
        else:
            rejected += 1
    
    return {'added': added, 'rejected': rejected}
```

## Testing Datasets

```python
def test_dataset_quality():
    """Test dataset quality scoring."""
    
    manager = DatasetManager()
    
    # Create test dataset
    license = DatasetLicense(
        license_type='CC-BY',
        license_url='https://creativecommons.org/licenses/by/4.0/',
        attribution_required=True,
        commercial_use=True,
        derivative_works=True,
        share_alike=False
    )
    
    dataset = Dataset(
        dataset_id='test_dataset',
        name='Test Dataset',
        description='For testing',
        version='1.0.0',
        license=license,
        creator_id='test_creator'
    )
    
    # Add quality tracks
    for i in range(100):
        dataset.add_track({
            'track_id': f'test_track_{i:03d}',
            'title': f'Test Track {i}',
            'artist': f'Artist {i % 10}',
            'genre': ['pop', 'rock', 'jazz', 'electronic'][i % 4],
            'mood': ['energetic', 'calm'][i % 2],
            'energy': 0.5 + (i % 10) * 0.05,
            'tempo': 90 + (i % 60),
            'duration': 180 + (i % 120),
            'album': f'Album {i // 20}',
            'year': 2024
        })
    
    # Test adding dataset
    assert manager.add_dataset(dataset)
    assert dataset.quality_score > 0.7
    
    # Test retrieval
    retrieved = manager.get_dataset('test_dataset')
    assert retrieved is not None
    assert retrieved.get_track_count() == 100
    
    # Test statistics
    stats = manager.get_statistics()
    assert stats['total_datasets'] >= 1
    
    print("✓ All dataset tests passed")

test_dataset_quality()
```

## Troubleshooting

### Issue: Low Quality Score

```python
# Diagnose quality issues
def diagnose_low_quality(manager, dataset_id):
    """Diagnose why a dataset has low quality."""
    
    dataset = manager.get_dataset(dataset_id)
    if not dataset:
        return None
    
    metadata = manager._score_metadata_completeness(dataset)
    consistency = manager._score_data_consistency(dataset)
    size = manager._score_dataset_size(dataset)
    diversity = manager._score_diversity(dataset)
    license = manager._score_license(dataset.license)
    
    print(f"Quality Breakdown:")
    print(f"  Metadata: {metadata:.1%} (target: 100%)")
    print(f"  Consistency: {consistency:.1%} (target: 100%)")
    print(f"  Size: {size:.1%} (target: 100%)")
    print(f"  Diversity: {diversity:.1%} (target: 100%)")
    print(f"  License: {license:.1%} (target: 100%)")
    
    return {
        'metadata': metadata,
        'consistency': consistency,
        'size': size,
        'diversity': diversity,
        'license': license
    }
```

## Roadmap

See [Roadmap](../roadmap.md) for planned enhancements:

- [ ] Automatic metadata enrichment
- [ ] Audio fingerprint analysis
- [ ] Audio feature extraction (MIR)
- [ ] Duplicate detection
- [ ] Genre auto-classification
- [ ] Mood detection via machine learning
- [ ] Multi-language metadata support
- [ ] Dataset version control

---

**Next**: [Edge Optimization →](edge-optimization.md) | [Blockchain Trust →](quantum-security.md) | [API Reference →](../api-reference/datasets.md)
