"""
Quantum provider abstraction for Microsoft QDK integration.

Manages initialization of the qsharp runtime and provides a unified
interface for quantum operations used by QFZZ components.
"""

import logging
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Q# source directory relative to this file
_QSHARP_SRC_DIR = Path(__file__).parent / "qsharp_src"


def _is_qsharp_available() -> bool:
    """Check if the qsharp package is installed."""
    try:
        import qsharp  # noqa: F401

        return True
    except ImportError:
        return False


class QuantumProvider:
    """
    Abstraction layer for Microsoft QDK quantum operations.

    Initializes the qsharp runtime and provides access to Q# operations.
    Falls back gracefully when the qsharp package is not installed.
    """

    def __init__(self):
        """Initialize the quantum provider."""
        self._initialized = False
        self._qsharp_available = _is_qsharp_available()
        self._qsharp = None

        if self._qsharp_available:
            self._initialize_qsharp()
        else:
            logger.info(
                "qsharp package not installed. Quantum features will use classical fallback. "
                "Install with: pip install qsharp"
            )

    def _initialize_qsharp(self) -> None:
        """Initialize the qsharp runtime with QFZZ Q# sources."""
        try:
            import qsharp

            self._qsharp = qsharp

            # Load the Q# source files
            for qs_file in _QSHARP_SRC_DIR.glob("*.qs"):
                code = qs_file.read_text()
                qsharp.eval(code)

            self._initialized = True
            logger.info("Microsoft QDK quantum provider initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize qsharp runtime: {e}")
            self._initialized = False

    @property
    def is_available(self) -> bool:
        """Check if quantum operations are available."""
        return self._initialized

    @property
    def backend_name(self) -> str:
        """Get the name of the active quantum backend."""
        if self._initialized:
            return "microsoft-qdk"
        return "classical-fallback"

    def eval(self, qsharp_code: str) -> Any:
        """
        Evaluate Q# code directly.

        Args:
            qsharp_code: Q# code to evaluate

        Returns:
            Result from the Q# evaluation

        Raises:
            RuntimeError: If qsharp is not available
        """
        if not self._initialized:
            raise RuntimeError(
                "Quantum provider is not initialized. Install qsharp: pip install qsharp"
            )
        return self._qsharp.eval(qsharp_code)

    def get_status(self) -> dict[str, Any]:
        """
        Get quantum provider status information.

        Returns:
            Dictionary of provider status details
        """
        status: dict[str, Any] = {
            "backend": self.backend_name,
            "available": self.is_available,
            "qsharp_installed": self._qsharp_available,
        }

        if self._initialized and self._qsharp is not None:
            try:
                status["qsharp_version"] = self._qsharp.__version__
            except AttributeError:
                status["qsharp_version"] = "unknown"

        return status
