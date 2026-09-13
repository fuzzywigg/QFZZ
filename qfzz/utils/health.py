"""
Health check endpoints for QFZZ.

Provides health status for monitoring and load balancers.
"""

import json
import logging
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import psutil

logger = logging.getLogger(__name__)


@dataclass
class HealthStatus:
    """Health status response."""
    status: str  # "healthy", "degraded", "unhealthy"
    timestamp: str
    uptime_seconds: float
    version: str
    checks: dict[str, Any]


class HealthChecker:
    """Performs health checks for QFZZ services."""

    def __init__(self):
        """Initialize health checker."""
        self.start_time = time.time()
        self.version = self._get_version()

    def _get_version(self) -> str:
        """Get application version."""
        try:
            version_file = Path(__file__).parent.parent / "VERSION"
            if version_file.exists():
                return version_file.read_text().strip()
        except Exception:
            pass
        return "1.0.0"

    def check_disk_space(self, path: str = ".", min_free_gb: float = 1.0) -> dict[str, Any]:
        """
        Check disk space.

        Args:
            path: Path to check
            min_free_gb: Minimum free space in GB

        Returns:
            Dict with status and details
        """
        try:
            usage = psutil.disk_usage(path)
            free_gb = usage.free / (1024 ** 3)

            return {
                "status": "healthy" if free_gb >= min_free_gb else "degraded",
                "free_gb": round(free_gb, 2),
                "total_gb": round(usage.total / (1024 ** 3), 2),
                "percent_used": usage.percent,
                "threshold_gb": min_free_gb,
            }
        except Exception as e:
            logger.error(f"Disk space check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
            }

    def check_memory(self, max_percent: float = 90.0) -> dict[str, Any]:
        """
        Check memory usage.

        Args:
            max_percent: Maximum memory usage percentage

        Returns:
            Dict with status and details
        """
        try:
            memory = psutil.virtual_memory()

            return {
                "status": "healthy" if memory.percent < max_percent else "degraded",
                "percent_used": memory.percent,
                "available_mb": round(memory.available / (1024 ** 2), 2),
                "total_mb": round(memory.total / (1024 ** 2), 2),
                "threshold_percent": max_percent,
            }
        except Exception as e:
            logger.error(f"Memory check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
            }

    def check_cpu(self, max_percent: float = 90.0) -> dict[str, Any]:
        """
        Check CPU usage.

        Args:
            max_percent: Maximum CPU usage percentage

        Returns:
            Dict with status and details
        """
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()

            return {
                "status": "healthy" if cpu_percent < max_percent else "degraded",
                "percent_used": cpu_percent,
                "cpu_count": cpu_count,
                "threshold_percent": max_percent,
            }
        except Exception as e:
            logger.error(f"CPU check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
            }

    def check_file_exists(self, filepath: str, name: str) -> dict[str, Any]:
        """
        Check if a file exists.

        Args:
            filepath: Path to file
            name: Friendly name for check

        Returns:
            Dict with status and details
        """
        try:
            path = Path(filepath)
            exists = path.exists()

            result = {
                "status": "healthy" if exists else "degraded",
                "exists": exists,
                "path": str(path.absolute()),
            }

            if exists:
                result["size_bytes"] = path.stat().st_size
                result["modified"] = datetime.fromtimestamp(path.stat().st_mtime).isoformat()

            return result
        except Exception as e:
            logger.error(f"File check failed for {name}: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
            }

    def check_ledger_integrity(self, ledger_path: str = "qfzz_ledger.json") -> dict[str, Any]:
        """
        Check ledger file integrity.

        Args:
            ledger_path: Path to ledger file

        Returns:
            Dict with status and details
        """
        try:
            # Basic existence check
            path = Path(ledger_path)
            if not path.exists():
                return {
                    "status": "unhealthy",
                    "error": "Ledger file not found",
                }

            # Load and validate JSON
            with open(path) as f:
                data = json.load(f)

            # Check structure
            if not isinstance(data, list) and 'chain' not in data:
                return {
                    "status": "degraded",
                    "error": "Unexpected ledger format",
                }

            blocks = data if isinstance(data, list) else data.get('chain', [])

            return {
                "status": "healthy",
                "blocks": len(blocks),
                "size_bytes": path.stat().st_size,
                "last_modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat(),
            }

        except json.JSONDecodeError as e:
            logger.error(f"Ledger JSON parse error: {e}")
            return {
                "status": "unhealthy",
                "error": f"Invalid JSON: {e}",
            }
        except Exception as e:
            logger.error(f"Ledger check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
            }

    def check_all(self) -> HealthStatus:
        """
        Run all health checks.

        Returns:
            HealthStatus object
        """
        checks = {
            "disk_space": self.check_disk_space(),
            "memory": self.check_memory(),
            "cpu": self.check_cpu(),
            "ledger": self.check_ledger_integrity(),
            "knowledge_graph": self.check_file_exists("qfzz_knowledge_graph.json", "knowledge_graph"),
            "audio_content": self.check_file_exists("qfzz_audio_content", "audio_content"),
        }

        # Determine overall status
        statuses = [check["status"] for check in checks.values()]

        if all(s == "healthy" for s in statuses):
            overall_status = "healthy"
        elif any(s == "unhealthy" for s in statuses):
            overall_status = "unhealthy"
        else:
            overall_status = "degraded"

        return HealthStatus(
            status=overall_status,
            timestamp=datetime.now().isoformat(),
            uptime_seconds=time.time() - self.start_time,
            version=self.version,
            checks=checks,
        )

    def to_dict(self, status: HealthStatus) -> dict[str, Any]:
        """Convert HealthStatus to dictionary."""
        return asdict(status)

    def to_json(self, status: HealthStatus) -> str:
        """Convert HealthStatus to JSON string."""
        return json.dumps(self.to_dict(status), indent=2)


# Singleton instance
_health_checker = None


def get_health_checker() -> HealthChecker:
    """Get or create health checker singleton."""
    global _health_checker
    if _health_checker is None:
        _health_checker = HealthChecker()
    return _health_checker


def health_check() -> HealthStatus:
    """Convenience function to perform health check."""
    checker = get_health_checker()
    return checker.check_all()


if __name__ == "__main__":
    # CLI usage
    checker = HealthChecker()
    status = checker.check_all()
    print(checker.to_json(status))

    # Exit code based on status
    import sys
    exit_codes = {"healthy": 0, "degraded": 1, "unhealthy": 2}
    sys.exit(exit_codes.get(status.status, 2))
