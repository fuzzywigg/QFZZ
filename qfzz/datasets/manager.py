"""
Dataset management with quality scoring and validation.
"""

import logging
import os
from typing import Any

from .models import Dataset, DatasetLicense

logger = logging.getLogger(__name__)


class DatasetManager:
    """
    Manages music datasets with quality scoring and license validation.
    """

    def __init__(self, allowed_licenses: list[str] | None = None):
        """
        Initialize Dataset Manager.

        Args:
            allowed_licenses: List of allowed license types
        """
        self._datasets: dict[str, Dataset] = {}
        self._allowed_licenses = allowed_licenses or ["CC-BY", "CC-BY-SA", "CC0"]
        logger.info(f"Dataset Manager initialized with licenses: {self._allowed_licenses}")

    def add_dataset(self, dataset: Dataset) -> bool:
        """
        Add a dataset to the manager.

        Args:
            dataset: Dataset to add

        Returns:
            True if added successfully, False otherwise
        """
        # Validate license
        if not dataset.license.is_compatible_with(self._allowed_licenses):
            logger.warning(
                f"Dataset {dataset.dataset_id} license not compatible: {dataset.license.license_type}"
            )
            return False

        # Calculate quality score
        quality_score = self.calculate_quality_score(dataset)
        dataset.quality_score = quality_score

        # Add to collection
        self._datasets[dataset.dataset_id] = dataset
        logger.info(f"Added dataset {dataset.dataset_id} (quality: {quality_score:.2f})")
        return True

    def remove_dataset(self, dataset_id: str) -> bool:
        """
        Remove a dataset from the manager.

        Args:
            dataset_id: Dataset identifier

        Returns:
            True if removed, False if not found
        """
        if dataset_id in self._datasets:
            del self._datasets[dataset_id]
            logger.info(f"Removed dataset {dataset_id}")
            return True

        logger.warning(f"Dataset {dataset_id} not found")
        return False

    def get_dataset(self, dataset_id: str) -> Dataset | None:
        """
        Get a dataset by ID.

        Args:
            dataset_id: Dataset identifier

        Returns:
            Dataset if found, None otherwise
        """
        return self._datasets.get(dataset_id)

    def list_datasets(self, min_quality: float | None = None) -> list[Dataset]:
        """
        List all datasets, optionally filtered by minimum quality.

        Args:
            min_quality: Minimum quality score filter

        Returns:
            List of datasets
        """
        datasets = list(self._datasets.values())

        if min_quality is not None:
            datasets = [d for d in datasets if d.quality_score >= min_quality]

        return sorted(datasets, key=lambda d: d.quality_score, reverse=True)

    def calculate_quality_score(self, dataset: Dataset) -> float:
        """
        Calculate quality score for a dataset.

        The score is based on multiple factors:
        - Completeness of metadata
        - Consistency of data
        - Size and diversity
        - License permissiveness

        Args:
            dataset: Dataset to score

        Returns:
            Quality score from 0.0 to 1.0
        """
        score = 0.0
        weights_sum = 0.0

        # Metadata completeness (weight: 0.3)
        metadata_weight = 0.3
        metadata_score = self._score_metadata_completeness(dataset)
        score += metadata_score * metadata_weight
        weights_sum += metadata_weight

        # Data consistency (weight: 0.25)
        consistency_weight = 0.25
        consistency_score = self._score_data_consistency(dataset)
        score += consistency_score * consistency_weight
        weights_sum += consistency_weight

        # Dataset size (weight: 0.2)
        size_weight = 0.2
        size_score = self._score_dataset_size(dataset)
        score += size_score * size_weight
        weights_sum += size_weight

        # Diversity (weight: 0.15)
        diversity_weight = 0.15
        diversity_score = self._score_diversity(dataset)
        score += diversity_score * diversity_weight
        weights_sum += diversity_weight

        # License permissiveness (weight: 0.1)
        license_weight = 0.1
        license_score = self._score_license(dataset.license)
        score += license_score * license_weight
        weights_sum += license_weight

        # Normalize
        if weights_sum > 0:
            score = score / weights_sum

        return min(1.0, max(0.0, score))

    def build_streamable_playlist(
        self,
        content_dir: str,
        dataset_ids: list[str] | None = None,
        min_quality: float = 0.0,
    ) -> list[dict[str, Any]]:
        """
        Build a playlist of tracks that can be streamed from local content.

        Args:
            content_dir: Base directory for relative track filenames
            dataset_ids: Optional list of dataset ids to include
            min_quality: Minimum dataset quality threshold

        Returns:
            List of normalized track dictionaries that are stream-ready
        """
        selected_ids = set(dataset_ids) if dataset_ids else None
        base_dir = os.path.abspath(content_dir)
        streamable: list[dict[str, Any]] = []

        for dataset in self.list_datasets(min_quality=min_quality):
            if selected_ids and dataset.dataset_id not in selected_ids:
                continue

            for index, track in enumerate(dataset.tracks):
                filename = track.get("filename")
                filepath = track.get("filepath")

                resolved_path = ""
                if filepath:
                    resolved_path = (
                        filepath
                        if os.path.isabs(filepath)
                        else os.path.join(base_dir, filepath)
                    )
                elif filename:
                    resolved_path = os.path.join(base_dir, filename)

                if not resolved_path or not os.path.isfile(resolved_path):
                    continue

                normalized_filename = os.path.basename(resolved_path)
                streamable.append(
                    {
                        "title": track.get("title", normalized_filename),
                        "artist": track.get("artist", "Unknown Artist"),
                        "genre": track.get("genre", "Unknown"),
                        "duration": int(track.get("duration", 0) or 0),
                        "filename": normalized_filename,
                        "filepath": resolved_path,
                        "dataset_id": dataset.dataset_id,
                        "dataset_track_index": index,
                    }
                )

        return streamable

    def _score_metadata_completeness(self, dataset: Dataset) -> float:
        """
        Score metadata completeness.

        Args:
            dataset: Dataset to score

        Returns:
            Score from 0.0 to 1.0
        """
        if not dataset.tracks:
            return 0.0

        required_fields = ["title", "artist", "genre", "duration"]
        optional_fields = ["album", "year", "mood", "energy", "tempo"]

        total_score = 0.0
        for track in dataset.tracks:
            track_score = 0.0

            # Required fields (70% of score)
            required_present = sum(
                1 for field in required_fields if field in track and track[field]
            )
            track_score += (required_present / len(required_fields)) * 0.7

            # Optional fields (30% of score)
            optional_present = sum(
                1 for field in optional_fields if field in track and track[field]
            )
            track_score += (optional_present / len(optional_fields)) * 0.3

            total_score += track_score

        return total_score / len(dataset.tracks)

    def _score_data_consistency(self, dataset: Dataset) -> float:
        """
        Score data consistency.

        Args:
            dataset: Dataset to score

        Returns:
            Score from 0.0 to 1.0
        """
        if not dataset.tracks:
            return 0.0

        # Check consistency of fields across tracks
        fields_consistency = 0.0
        sample_track = dataset.tracks[0]
        sample_fields = set(sample_track.keys())

        for track in dataset.tracks:
            track_fields = set(track.keys())
            # Calculate field overlap
            if sample_fields:
                overlap = len(sample_fields & track_fields) / len(sample_fields)
                fields_consistency += overlap

        fields_consistency /= len(dataset.tracks)

        # Check for valid values
        valid_values_score = 0.0
        for track in dataset.tracks:
            track_score = 1.0

            # Check duration is positive
            if "duration" in track and track["duration"] <= 0:
                track_score -= 0.2

            # Check energy is in valid range
            if "energy" in track and not 0.0 <= track["energy"] <= 1.0:
                track_score -= 0.2

            valid_values_score += max(0.0, track_score)

        valid_values_score /= len(dataset.tracks)

        return fields_consistency * 0.5 + valid_values_score * 0.5

    def _score_dataset_size(self, dataset: Dataset) -> float:
        """
        Score dataset size.

        Args:
            dataset: Dataset to score

        Returns:
            Score from 0.0 to 1.0
        """
        track_count = len(dataset.tracks)

        # Logarithmic scoring: good datasets have 100+ tracks
        if track_count == 0:
            return 0.0
        elif track_count < 10:
            return 0.2
        elif track_count < 50:
            return 0.4
        elif track_count < 100:
            return 0.6
        elif track_count < 500:
            return 0.8
        else:
            return 1.0

    def _score_diversity(self, dataset: Dataset) -> float:
        """
        Score dataset diversity (genres, artists, etc.).

        Args:
            dataset: Dataset to score

        Returns:
            Score from 0.0 to 1.0
        """
        if not dataset.tracks:
            return 0.0

        # Genre diversity
        genres = set()
        artists = set()

        for track in dataset.tracks:
            if "genre" in track:
                genres.add(track["genre"])
            if "artist" in track:
                artists.add(track["artist"])

        track_count = len(dataset.tracks)

        # Score based on unique genres and artists
        genre_diversity = min(1.0, len(genres) / 10.0)  # 10+ genres = full score
        artist_diversity = min(
            1.0, len(artists) / max(1, track_count / 5)
        )  # Avg 5 tracks per artist

        return genre_diversity * 0.5 + artist_diversity * 0.5

    def _score_license(self, license: DatasetLicense) -> float:
        """
        Score license permissiveness.

        Args:
            license: Dataset license

        Returns:
            Score from 0.0 to 1.0
        """
        score = 0.5  # Base score

        if license.commercial_use:
            score += 0.2

        if license.derivative_works:
            score += 0.2

        if not license.share_alike:
            score += 0.1

        return min(1.0, score)

    def validate_license(self, license: DatasetLicense) -> bool:
        """
        Validate if a license is acceptable.

        Args:
            license: License to validate

        Returns:
            True if valid, False otherwise
        """
        return license.is_compatible_with(self._allowed_licenses)

    def get_statistics(self) -> dict[str, Any]:
        """
        Get statistics about managed datasets.

        Returns:
            Dictionary of statistics
        """
        total_datasets = len(self._datasets)
        total_tracks = sum(d.get_track_count() for d in self._datasets.values())

        avg_quality = 0.0
        if total_datasets > 0:
            avg_quality = sum(d.quality_score for d in self._datasets.values()) / total_datasets

        all_genres = set()
        all_artists = set()
        for dataset in self._datasets.values():
            all_genres.update(dataset.get_genres())
            all_artists.update(dataset.get_artists())

        return {
            "total_datasets": total_datasets,
            "total_tracks": total_tracks,
            "average_quality_score": round(avg_quality, 3),
            "unique_genres": len(all_genres),
            "unique_artists": len(all_artists),
            "allowed_licenses": self._allowed_licenses,
        }
