"""QuantumProvider._initialize_qsharp with empty *.qs glob still marks available."""

from unittest.mock import MagicMock, patch

from qfzz.quantum.provider import QuantumProvider


def test_qsharp_empty_glob_initializes_without_eval():
    qs = MagicMock()
    p = QuantumProvider.__new__(QuantumProvider)
    p._initialized = False
    p._qsharp_available = True
    p._qsharp = None

    with patch("qfzz.quantum.provider._QSHARP_SRC_DIR") as src_dir:
        src_dir.glob.return_value = []
        with patch.dict("sys.modules", {"qsharp": qs}):
            QuantumProvider._initialize_qsharp(p)

    qs.eval.assert_not_called()
    assert p._initialized is True
    assert p.is_available is True
    assert p.backend_name == "microsoft-qdk"
