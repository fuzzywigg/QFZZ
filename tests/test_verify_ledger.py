"""
Tests for ledger verification tool.
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from datetime import datetime

# Import the verifier module
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

try:
    import verify_ledger
    Block = verify_ledger.Block
    LedgerVerifier = verify_ledger.LedgerVerifier
except ImportError:
    # Fallback for different test execution contexts
    exec(open(Path(__file__).parent.parent / "scripts" / "verify-ledger.py").read())
    Block = globals()['Block']
    LedgerVerifier = globals()['LedgerVerifier']


class TestBlock(unittest.TestCase):
    """Test Block class."""
    
    def test_block_creation(self):
        """Test creating a block."""
        block = Block(
            index=0,
            timestamp="2026-01-01T00:00:00",
            data={"type": "genesis"},
            previous_hash="0",
            hash="abc123"
        )
        
        self.assertEqual(block.index, 0)
        self.assertEqual(block.data["type"], "genesis")
    
    def test_block_from_dict(self):
        """Test creating block from dictionary."""
        block_dict = {
            "index": 1,
            "timestamp": "2026-01-01T00:00:01",
            "data": {"message": "test"},
            "previous_hash": "abc123",
            "hash": "def456"
        }
        
        block = Block.from_dict(block_dict)
        self.assertEqual(block.index, 1)
        self.assertEqual(block.hash, "def456")
    
    def test_calculate_hash(self):
        """Test hash calculation."""
        block = Block(
            index=0,
            timestamp="2026-01-01T00:00:00",
            data={"type": "genesis"},
            previous_hash="0",
            hash=""
        )
        
        calculated = block.calculate_hash()
        self.assertIsInstance(calculated, str)
        self.assertEqual(len(calculated), 64)  # SHA-256 hex length
    
    def test_is_valid(self):
        """Test block validation."""
        block = Block(
            index=0,
            timestamp="2026-01-01T00:00:00",
            data={"type": "genesis"},
            previous_hash="0",
            hash=""
        )
        
        # Set correct hash
        block.hash = block.calculate_hash()
        self.assertTrue(block.is_valid())
        
        # Tamper with hash
        block.hash = "invalid_hash"
        self.assertFalse(block.is_valid())


class TestLedgerVerifier(unittest.TestCase):
    """Test LedgerVerifier class."""
    
    def create_valid_ledger(self) -> Path:
        """Create a valid test ledger file."""
        # Create blocks
        block0 = Block(
            index=0,
            timestamp="2026-01-01T00:00:00",
            data={"type": "genesis"},
            previous_hash="0",
            hash=""
        )
        block0.hash = block0.calculate_hash()
        
        block1 = Block(
            index=1,
            timestamp="2026-01-01T00:00:01",
            data={"message": "first"},
            previous_hash=block0.hash,
            hash=""
        )
        block1.hash = block1.calculate_hash()
        
        block2 = Block(
            index=2,
            timestamp="2026-01-01T00:00:02",
            data={"message": "second"},
            previous_hash=block1.hash,
            hash=""
        )
        block2.hash = block2.calculate_hash()
        
        # Write to temp file
        ledger_data = {
            "chain": [
                {
                    "index": b.index,
                    "timestamp": b.timestamp,
                    "data": b.data,
                    "previous_hash": b.previous_hash,
                    "hash": b.hash
                }
                for b in [block0, block1, block2]
            ]
        }
        
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        json.dump(ledger_data, temp_file)
        temp_file.close()
        
        return Path(temp_file.name)
    
    def create_invalid_ledger(self) -> Path:
        """Create an invalid test ledger file with broken chain."""
        # Create blocks
        block0 = Block(
            index=0,
            timestamp="2026-01-01T00:00:00",
            data={"type": "genesis"},
            previous_hash="0",
            hash=""
        )
        block0.hash = block0.calculate_hash()
        
        block1 = Block(
            index=1,
            timestamp="2026-01-01T00:00:01",
            data={"message": "tampered"},  # Changed data
            previous_hash=block0.hash,
            hash="wrong_hash"  # Wrong hash
        )
        
        # Write to temp file
        ledger_data = {
            "chain": [
                {
                    "index": b.index,
                    "timestamp": b.timestamp,
                    "data": b.data,
                    "previous_hash": b.previous_hash,
                    "hash": b.hash
                }
                for b in [block0, block1]
            ]
        }
        
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        json.dump(ledger_data, temp_file)
        temp_file.close()
        
        return Path(temp_file.name)
    
    def test_load_valid_ledger(self):
        """Test loading a valid ledger."""
        ledger_path = self.create_valid_ledger()
        
        try:
            verifier = LedgerVerifier(str(ledger_path))
            result = verifier.load_ledger()
            
            self.assertTrue(result)
            self.assertEqual(len(verifier.blocks), 3)
        finally:
            ledger_path.unlink()
    
    def test_load_nonexistent_ledger(self):
        """Test loading non-existent ledger."""
        verifier = LedgerVerifier("/nonexistent/ledger.json")
        result = verifier.load_ledger()
        
        self.assertFalse(result)
    
    def test_verify_valid_chain(self):
        """Test verification of valid chain."""
        ledger_path = self.create_valid_ledger()
        
        try:
            verifier = LedgerVerifier(str(ledger_path))
            result = verifier.verify_all()
            
            self.assertTrue(result)
            self.assertEqual(len(verifier.errors), 0)
        finally:
            ledger_path.unlink()
    
    def test_verify_invalid_chain(self):
        """Test verification of invalid chain."""
        ledger_path = self.create_invalid_ledger()
        
        try:
            verifier = LedgerVerifier(str(ledger_path))
            result = verifier.verify_all()
            
            self.assertFalse(result)
            self.assertGreater(len(verifier.errors), 0)
        finally:
            ledger_path.unlink()
    
    def test_get_statistics(self):
        """Test getting ledger statistics."""
        ledger_path = self.create_valid_ledger()
        
        try:
            verifier = LedgerVerifier(str(ledger_path))
            verifier.load_ledger()
            
            stats = verifier.get_statistics()
            
            self.assertEqual(stats["total_blocks"], 3)
            self.assertEqual(stats["first_index"], 0)
            self.assertEqual(stats["last_index"], 2)
        finally:
            ledger_path.unlink()
    
    def test_export_report(self):
        """Test exporting verification report."""
        ledger_path = self.create_valid_ledger()
        report_path = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        report_path.close()
        
        try:
            verifier = LedgerVerifier(str(ledger_path))
            verifier.verify_all()
            verifier.export_report(report_path.name)
            
            # Read report
            with open(report_path.name) as f:
                report = json.load(f)
            
            self.assertIn("verification_time", report)
            self.assertIn("statistics", report)
            self.assertTrue(report["valid"])
        finally:
            ledger_path.unlink()
            Path(report_path.name).unlink()


if __name__ == "__main__":
    unittest.main()
