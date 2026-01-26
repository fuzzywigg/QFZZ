# DatasetManager and Dataset API Reference

## Overview

The datasets module provides comprehensive management of music datasets with quality scoring, license validation, and metadata analysis. The `DatasetManager` class orchestrates multiple datasets with quality assurance, while the `Dataset` class represents individual music collections with track management and analytics. The `DatasetLicense` class handles open-source license compatibility and restrictions.

## Table of Contents

- [DatasetManager Class](#datasetmanager-class)
  - [Constructor](#constructor)
  - [Dataset Operations](#dataset-operations)
  - [Quality Scoring](#quality-scoring)
  - [License Management](#license-management)
  - [Statistics](#statistics)
- [Dataset Class](#dataset-class)
  - [Constructor](#constructor-1)
  - [Track Management](#track-management)
  - [Metadata Retrieval](#metadata-retrieval)
  - [Validation](#validation)
- [DatasetLicense Class](#datasetlicense-class)
  - [Constructor](#constructor-2)
  - [License Validation](#license-validation)
- [Code Examples](#code-examples)
- [Quality Scoring Algorithm](#quality-scoring-algorithm)

---

## DatasetManager Class

### Constructor

```python
def __init__(self, allowed_licenses: Optional[List[str]] = None) -> None
```

Initialize the Dataset Manager with license configuration.

**Parameters:**

- `allowed_licenses` (Optional[List[str]]): List of allowed license types.
  Default: `['CC-BY', 'CC-BY-SA', 'CC0']`

  Supported licenses:
  - `"CC0"`: Public domain
  - `"CC-BY"`: Attribution required
  - `"CC-BY-SA"`: Attribution and Share-Alike
  - `"CC-BY-NC"`: Non-commercial
  - `"CC-BY-NC-SA"`: Non-commercial and Share-Alike
  - `"MIT"`: MIT License
  - `"Apache-2.0"`: Apache License
  - `"GPL-3.0"`: GNU General Public License
  - `"Public-Domain"`: Public domain

**Returns:** None

**Side Effects:**
- Initializes empty datasets dictionary
- Sets allowed licenses
- Logs initialization

**Example:**

```python
from qfzz.datasets.manager import DatasetManager

# Use default licenses
manager1 = DatasetManager()

# Use custom allowed licenses
manager2 = DatasetManager(allowed_licenses=[
    "CC-BY",
    "CC-BY-SA",
    "MIT",
    "Apache-2.0"
])
```

---

## Dataset Operations

### add_dataset()

```python
def add_dataset(self, dataset: Dataset) -> bool
```

Add a dataset to the manager with license and quality validation.

**Parameters:**

- `dataset` (Dataset): Dataset object to add

**Returns:** bool - True if added successfully, False if license not compatible

**Raises:**
- `ValueError`: If dataset validation fails

**Side Effects:**
- Validates dataset license compatibility
- Calculates and assigns quality score
- Stores dataset in internal registry
- Logs dataset addition

**Example:**

```python
from qfzz.datasets.models import Dataset, DatasetLicense

license = DatasetLicense(
    license_type="CC-BY",
    license_url="https://creativecommons.org/licenses/by/4.0/",
    attribution_required=True,
    commercial_use=True,
    derivative_works=True,
    share_alike=False
)

dataset = Dataset(
    dataset_id="dataset_001",
    name="Jazz Classics",
    description="A collection of classic jazz recordings",
    version="1.0.0",
    license=license,
    creator_id="creator_jazz"
)

# Add tracks to dataset
dataset.add_track({
    "track_id": "track_001",
    "title": "Autumn Leaves",
    "artist": "Bill Evans",
    "album": "Sunday at the Village Vanguard",
    "genre": "jazz",
    "mood": "mellow",
    "energy": 0.5,
    "tempo": "slow",
    "duration": 480
})

# Add to manager
success = manager.add_dataset(dataset)
if success:
    print(f"Dataset added with quality score: {dataset.quality_score:.3f}")
else:
    print("License not compatible with allowed licenses")
```

---

### remove_dataset()

```python
def remove_dataset(self, dataset_id: str) -> bool
```

Remove a dataset from the manager.

**Parameters:**

- `dataset_id` (str): Dataset identifier

**Returns:** bool - True if removed, False if not found

**Side Effects:**
- Removes dataset from internal registry
- Logs removal

**Example:**

```python
removed = manager.remove_dataset("dataset_001")
if removed:
    print("Dataset removed successfully")
else:
    print("Dataset not found")
```

---

### get_dataset()

```python
def get_dataset(self, dataset_id: str) -> Optional[Dataset]
```

Retrieve a dataset by ID.

**Parameters:**

- `dataset_id` (str): Dataset identifier

**Returns:** Dataset if found, None otherwise

**Example:**

```python
dataset = manager.get_dataset("dataset_001")
if dataset:
    print(f"Dataset: {dataset.name}")
    print(f"Tracks: {dataset.get_track_count()}")
    print(f"Quality: {dataset.quality_score:.3f}")
else:
    print("Dataset not found")
```

---

### list_datasets()

```python
def list_datasets(self, min_quality: Optional[float] = None) -> List[Dataset]
```

List all datasets with optional quality filtering.

**Parameters:**

- `min_quality` (Optional[float]): Minimum quality score filter (0.0-1.0)

**Returns:** List[Dataset] - Datasets sorted by quality (highest first)

**Example:**

```python
# Get all datasets
all_datasets = manager.list_datasets()
print(f"Total datasets: {len(all_datasets)}")

# Get high-quality datasets only
high_quality = manager.list_datasets(min_quality=0.8)
for dataset in high_quality:
    print(f"  {dataset.name}: {dataset.quality_score:.3f}")

# Get medium-quality datasets
medium_quality = manager.list_datasets(min_quality=0.5)
print(f"Medium+ quality: {len(medium_quality)} datasets")
```

---

## Quality Scoring

### calculate_quality_score()

```python
def calculate_quality_score(self, dataset: Dataset) -> float
```

Calculate comprehensive quality score for a dataset.

**Parameters:**

- `dataset` (Dataset): Dataset to score

**Returns:** float - Quality score (0.0-1.0)

**Scoring Factors:**

| Factor | Weight | Criteria |
|--------|--------|----------|
| Metadata Completeness | 30% | Required/optional fields present |
| Data Consistency | 25% | Field consistency across tracks, valid values |
| Dataset Size | 20% | Number of tracks (logarithmic scale) |
| Diversity | 15% | Genre and artist variety |
| License Permissiveness | 10% | Commercial use, derivatives allowed |

**Metadata Completeness Scoring:**

Required fields (70% of score):
- title, artist, genre, duration

Optional fields (30% of score):
- album, year, mood, energy, tempo

**Example:**

```python
# Create a high-quality dataset
license = DatasetLicense(
    license_type="CC-BY",
    license_url="https://example.com/license",
    commercial_use=True,
    derivative_works=True
)

dataset = Dataset(
    dataset_id="high_quality",
    name="Complete Jazz Collection",
    description="1000 jazz tracks with full metadata",
    version="2.0",
    license=license,
    creator_id="jazz_curator"
)

# Add 500+ tracks with complete metadata
for i in range(500):
    dataset.add_track({
        "track_id": f"track_{i:04d}",
        "title": f"Track {i}",
        "artist": f"Artist {i % 20}",
        "album": f"Album {i // 50}",
        "genre": ["jazz", "blues", "soul", "funk"][i % 4],
        "mood": ["calm", "upbeat", "energetic", "mellow"][i % 4],
        "energy": (i % 10) / 10.0,
        "tempo": ["slow", "medium", "fast"][i % 3],
        "duration": 200 + (i % 200)
    })

quality = manager.calculate_quality_score(dataset)
print(f"Quality score: {quality:.3f}")  # ~0.85-0.95
```

---

## License Management

### validate_license()

```python
def validate_license(self, license: DatasetLicense) -> bool
```

Validate if a license is acceptable.

**Parameters:**

- `license` (DatasetLicense): License to validate

**Returns:** bool - True if valid, False otherwise

**Example:**

```python
# Valid license
valid_license = DatasetLicense(
    license_type="CC-BY",
    license_url="https://example.com/cc-by"
)

if manager.validate_license(valid_license):
    print("License accepted")

# Invalid license
invalid_license = DatasetLicense(
    license_type="Proprietary",
    license_url="https://example.com/proprietary"
)

if not manager.validate_license(invalid_license):
    print("License not in allowed list")
```

---

## Statistics

### get_statistics()

```python
def get_statistics(self) -> Dict[str, Any]
```

Get comprehensive statistics about managed datasets.

**Parameters:** None

**Returns:** Dict containing:
- `total_datasets` (int): Number of managed datasets
- `total_tracks` (int): Total tracks across all datasets
- `average_quality_score` (float): Mean quality score
- `unique_genres` (int): Count of unique genres
- `unique_artists` (int): Count of unique artists
- `allowed_licenses` (List[str]): Configured allowed licenses

**Example:**

```python
stats = manager.get_statistics()
print(f"=== Dataset Statistics ===")
print(f"Datasets: {stats['total_datasets']}")
print(f"Total tracks: {stats['total_tracks']}")
print(f"Average quality: {stats['average_quality_score']:.3f}")
print(f"Unique genres: {stats['unique_genres']}")
print(f"Unique artists: {stats['unique_artists']}")
```

---

## Dataset Class

### Constructor

```python
@dataclass
class Dataset:
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
```

Create a music dataset with tracks and metadata.

**Parameters:**

- `dataset_id` (str): Unique dataset identifier
- `name` (str): Human-readable dataset name
- `description` (str): Dataset description
- `version` (str): Version string (e.g., "1.0.0")
- `license` (DatasetLicense): License information
- `creator_id` (str): Creator identifier
- `tracks` (List): Track list, default empty
- `metadata` (Dict): Additional metadata, default empty
- `quality_score` (float): Quality score (0.0-1.0), default 0.0
- `created_at` (str): ISO-8601 creation timestamp
- `updated_at` (str): ISO-8601 update timestamp

**Raises:** ValueError if validation fails

**Example:**

```python
from qfzz.datasets.models import Dataset, DatasetLicense

license = DatasetLicense(
    license_type="CC-BY-SA",
    license_url="https://creativecommons.org/licenses/by-sa/4.0/",
    attribution_required=True,
    commercial_use=True,
    derivative_works=True,
    share_alike=True
)

dataset = Dataset(
    dataset_id="rock_anthems",
    name="Rock Anthems Collection",
    description="Essential rock music tracks",
    version="1.5.0",
    license=license,
    creator_id="curator_rock",
    metadata={
        "category": "rock",
        "year_range": "1970-2023",
        "language": "en"
    }
)
```

---

## Track Management

### add_track()

```python
def add_track(self, track: Dict[str, Any]) -> None
```

Add a track to the dataset.

**Parameters:**

- `track` (Dict[str, Any]): Track dictionary with fields:
  - `track_id` (str): Unique track ID
  - `title` (str): Track title
  - `artist` (str): Artist name
  - `genre` (str): Music genre
  - Plus any optional fields (album, year, mood, energy, tempo, etc.)

**Returns:** None

**Side Effects:**
- Appends track to tracks list
- Updates `updated_at` timestamp

**Example:**

```python
dataset.add_track({
    "track_id": "track_001",
    "title": "Stairway to Heaven",
    "artist": "Led Zeppelin",
    "album": "Led Zeppelin IV",
    "genre": "rock",
    "year": 1971,
    "mood": "epic",
    "energy": 0.8,
    "tempo": "varied",
    "duration": 482
})
```

---

### remove_track()

```python
def remove_track(self, track_id: str) -> bool
```

Remove a track from the dataset.

**Parameters:**

- `track_id` (str): Track identifier

**Returns:** bool - True if removed, False if not found

**Side Effects:**
- Removes track from tracks list
- Updates `updated_at` timestamp if successful

**Example:**

```python
if dataset.remove_track("track_001"):
    print("Track removed")
else:
    print("Track not found")
```

---

## Metadata Retrieval

### get_track_count()

```python
def get_track_count(self) -> int
```

Get the number of tracks in the dataset.

**Parameters:** None

**Returns:** int - Number of tracks

**Example:**

```python
count = dataset.get_track_count()
print(f"Dataset contains {count} tracks")
```

---

### get_total_duration()

```python
def get_total_duration(self) -> int
```

Get total duration of all tracks in seconds.

**Parameters:** None

**Returns:** int - Total duration in seconds

**Example:**

```python
total_seconds = dataset.get_total_duration()
hours = total_seconds / 3600
print(f"Total duration: {hours:.1f} hours")
```

---

### get_genres()

```python
def get_genres(self) -> List[str]
```

Get unique genres in dataset.

**Parameters:** None

**Returns:** List[str] - Sorted list of unique genre names

**Example:**

```python
genres = dataset.get_genres()
print(f"Genres ({len(genres)}): {', '.join(genres)}")
```

---

### get_artists()

```python
def get_artists(self) -> List[str]
```

Get unique artists in dataset.

**Parameters:** None

**Returns:** List[str] - Sorted list of unique artist names

**Example:**

```python
artists = dataset.get_artists()
print(f"Artists ({len(artists)}): {', '.join(artists[:10])}...")
```

---

### to_dict()

```python
def to_dict(self) -> Dict[str, Any]
```

Convert dataset to dictionary representation.

**Parameters:** None

**Returns:** Dict with all dataset attributes plus computed fields:
- `track_count` (int): Number of tracks
- `total_duration` (int): Total duration in seconds

**Example:**

```python
dataset_dict = dataset.to_dict()
print(dataset_dict)
# {
#     'dataset_id': 'rock_anthems',
#     'name': 'Rock Anthems Collection',
#     'track_count': 250,
#     'total_duration': 54000,
#     'quality_score': 0.82,
#     ...
# }
```

---

## Validation

### validate()

```python
def validate(self) -> None
```

Validate dataset parameters.

**Parameters:** None

**Returns:** None

**Raises:** ValueError if any parameter invalid

**Validation Rules:**

- `dataset_id`: Must be non-empty
- `name`: Must be non-empty
- `version`: Must be non-empty
- `creator_id`: Must be non-empty
- `quality_score`: Must be 0.0-1.0

**Example:**

```python
try:
    dataset = Dataset(
        dataset_id="",  # Invalid!
        name="Test",
        description="Test",
        version="1.0",
        license=license,
        creator_id="test"
    )
except ValueError as e:
    print(f"Validation error: {e}")
```

---

## DatasetLicense Class

### Constructor

```python
@dataclass
class DatasetLicense:
    license_type: str
    license_url: str
    attribution_required: bool = True
    commercial_use: bool = True
    derivative_works: bool = True
    share_alike: bool = False
    additional_terms: str = ""
```

Create license information for a dataset.

**Parameters:**

- `license_type` (str): License type identifier
- `license_url` (str): URL to license text
- `attribution_required` (bool): Attribution requirement, default True
- `commercial_use` (bool): Commercial use allowed, default True
- `derivative_works` (bool): Derivative works allowed, default True
- `share_alike` (bool): Share-alike requirement, default False
- `additional_terms` (str): Additional terms text, default ""

**Example:**

```python
from qfzz.datasets.models import DatasetLicense

# Creative Commons BY license
cc_by = DatasetLicense(
    license_type="CC-BY",
    license_url="https://creativecommons.org/licenses/by/4.0/",
    attribution_required=True,
    commercial_use=True,
    derivative_works=True,
    share_alike=False
)

# Creative Commons BY-SA license
cc_by_sa = DatasetLicense(
    license_type="CC-BY-SA",
    license_url="https://creativecommons.org/licenses/by-sa/4.0/",
    attribution_required=True,
    commercial_use=True,
    derivative_works=True,
    share_alike=True,
    additional_terms="Derivative works must use CC-BY-SA"
)

# MIT License
mit = DatasetLicense(
    license_type="MIT",
    license_url="https://opensource.org/licenses/MIT",
    attribution_required=False,
    commercial_use=True,
    derivative_works=True,
    share_alike=False
)
```

---

## License Validation

### is_compatible_with()

```python
def is_compatible_with(self, allowed_licenses: List[str]) -> bool
```

Check if license is compatible with allowed licenses.

**Parameters:**

- `allowed_licenses` (List[str]): List of allowed license type strings

**Returns:** bool - True if compatible, False otherwise

**Example:**

```python
cc_by = DatasetLicense(
    license_type="CC-BY",
    license_url="https://example.com/cc-by"
)

allowed = ["CC-BY", "CC-BY-SA", "CC0"]
if cc_by.is_compatible_with(allowed):
    print("License is compatible")

proprietary = DatasetLicense(
    license_type="Proprietary",
    license_url="https://example.com/proprietary"
)

if not proprietary.is_compatible_with(allowed):
    print("License not in allowed list")
```

---

### to_dict()

```python
def to_dict(self) -> Dict[str, Any]
```

Convert license to dictionary representation.

**Parameters:** None

**Returns:** Dict with all license attributes

---

## Code Examples

### Complete Dataset Management Workflow

```python
from qfzz.datasets.manager import DatasetManager
from qfzz.datasets.models import Dataset, DatasetLicense

# Initialize manager with allowed licenses
manager = DatasetManager(allowed_licenses=[
    "CC-BY",
    "CC-BY-SA",
    "CC0",
    "MIT"
])

# Create three datasets
datasets = []
for i in range(3):
    license_type = ["CC-BY", "CC-BY-SA", "CC0"][i]

    license = DatasetLicense(
        license_type=license_type,
        license_url=f"https://example.com/{license_type}",
        commercial_use=True,
        derivative_works=True
    )

    dataset = Dataset(
        dataset_id=f"dataset_{i:03d}",
        name=f"Collection {i+1}",
        description=f"Music collection {i+1}",
        version="1.0.0",
        license=license,
        creator_id=f"curator_{i}"
    )

    # Add tracks
    for j in range(100):
        dataset.add_track({
            "track_id": f"track_{i:03d}_{j:04d}",
            "title": f"Track {j}",
            "artist": f"Artist {j % 10}",
            "genre": ["rock", "pop", "jazz"][j % 3],
            "mood": ["upbeat", "calm", "energetic"][j % 3],
            "energy": (j % 10) / 10.0,
            "tempo": ["slow", "medium", "fast"][j % 3],
            "duration": 200 + (j % 200)
        })

    datasets.append(dataset)

# Add datasets to manager
for dataset in datasets:
    if manager.add_dataset(dataset):
        print(f"✓ {dataset.name}: {dataset.quality_score:.3f}")
    else:
        print(f"✗ {dataset.name}: License not compatible")

# Get statistics
stats = manager.get_statistics()
print(f"\n=== Statistics ===")
print(f"Total datasets: {stats['total_datasets']}")
print(f"Total tracks: {stats['total_tracks']}")
print(f"Average quality: {stats['average_quality_score']:.3f}")
print(f"Unique genres: {stats['unique_genres']}")
print(f"Unique artists: {stats['unique_artists']}")

# List high-quality datasets
print(f"\n=== High Quality Datasets ===")
high_quality = manager.list_datasets(min_quality=0.75)
for dataset in high_quality:
    print(f"  {dataset.name}")
    print(f"    Tracks: {dataset.get_track_count()}")
    print(f"    Genres: {', '.join(dataset.get_genres()[:3])}")
    print(f"    Quality: {dataset.quality_score:.3f}")
```

---

## Quality Scoring Algorithm Details

### Metadata Completeness (30%)

```
Score = (Required Fields × 0.7) + (Optional Fields × 0.3)

Required: title, artist, genre, duration
Optional: album, year, mood, energy, tempo
```

### Data Consistency (25%)

```
Score = (Field Consistency × 0.5) + (Value Validity × 0.5)

Field Consistency: How many tracks have same fields
Value Validity: Check duration > 0, energy in [0.0, 1.0], etc.
```

### Dataset Size (20%)

Logarithmic scoring:
- 0 tracks: 0.0
- <10 tracks: 0.2
- <50 tracks: 0.4
- <100 tracks: 0.6
- <500 tracks: 0.8
- 500+ tracks: 1.0

### Diversity (15%)

```
Score = (Genre Diversity × 0.5) + (Artist Diversity × 0.5)

Genre: min(1.0, unique_genres / 10)
Artist: min(1.0, unique_artists / (tracks / 5))
```

### License Permissiveness (10%)

```
Base Score: 0.5
+ 0.2 if commercial_use allowed
+ 0.2 if derivative_works allowed
+ 0.1 if share_alike NOT required
= 0.0 to 1.0
```

---

## Version Information

- **Module**: `qfzz.datasets.manager`, `qfzz.datasets.models`
- **Classes**: `DatasetManager`, `Dataset`, `DatasetLicense`
- **Python**: 3.8+
- **Dependencies**: dataclasses, typing, datetime, enum
