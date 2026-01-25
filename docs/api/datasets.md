# Datasets API

The datasets module manages GNU/OPENSOURCE datasets with quality control.

## DatasetManager

::: qfzz.datasets.manager.DatasetManager
    options:
      show_root_heading: true
      show_source: true

## Dataset

::: qfzz.datasets.dataset.Dataset
    options:
      show_root_heading: true
      show_source: true

## DatasetLicense

::: qfzz.datasets.dataset.DatasetLicense
    options:
      show_root_heading: true
      show_source: true

## Usage Example

```python
from qfzz import DatasetManager, Dataset, DatasetLicense

# Create manager
manager = DatasetManager(opensource_only=True, min_quality=0.7)

# Register dataset
dataset = Dataset(
    id="ds_001",
    name="OpenMusic Dataset",
    description="High-quality open source music",
    license=DatasetLicense.CC_BY,
    source_url="https://example.com/dataset",
    quality_score=0.9,
    category="music",
    size_mb=150.0
)

success = manager.register_dataset(dataset)
if success:
    manager.verify_dataset_blockchain(dataset.id)
    
# Get high quality datasets
high_quality = manager.get_high_quality_datasets()
print(f"Found {len(high_quality)} high quality datasets")
```
