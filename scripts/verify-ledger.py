#!/usr/bin/env python3
"""
QFZZ Ledger Verification Tool

Verifies the integrity of the blockchain ledger by validating the SHA-256 hash chain.
"""

import argparse
import hashlib
import json
import logging
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, List, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class Block:
    """Represents a blockchain block."""
    index: int
    timestamp: str
    data: dict
    previous_hash: str
    hash: str
    event_type: Optional[str] = None
    
    @classmethod
    def from_dict(cls, d: dict) -> 'Block':
        """Create Block from dictionary."""
        # Handle both 'previous_hash' and 'prev_hash' formats
        prev_hash = d.get('previous_hash') or d.get('prev_hash', '0')
        
        return cls(
            index=d['index'],
            timestamp=d['timestamp'],
            data=d.get('data', {}),
            previous_hash=prev_hash,
            hash=d['hash'],
            event_type=d.get('event_type')
        )
    
    def calculate_hash(self) -> str:
        """Calculate the hash for this block."""
        # Include event_type if present (QFZZ ledger format)
        if self.event_type:
            block_string = f"{self.index}{self.timestamp}{self.event_type}{json.dumps(self.data, sort_keys=True)}{self.previous_hash}"
        else:
            block_string = f"{self.index}{self.timestamp}{json.dumps(self.data, sort_keys=True)}{self.previous_hash}"
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def is_valid(self) -> bool:
        """Check if block hash is valid."""
        return self.hash == self.calculate_hash()


class LedgerVerifier:
    """Verifies QFZZ blockchain ledger integrity."""
    
    def __init__(self, ledger_path: str):
        """
        Initialize verifier.
        
        Args:
            ledger_path: Path to ledger JSON file
        """
        self.ledger_path = Path(ledger_path)
        self.blocks: List[Block] = []
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def load_ledger(self) -> bool:
        """
        Load ledger from file.
        
        Returns:
            True if loaded successfully, False otherwise
        """
        if not self.ledger_path.exists():
            logger.error(f"Ledger file not found: {self.ledger_path}")
            return False
        
        try:
            with open(self.ledger_path, 'r') as f:
                data = json.load(f)
            
            # Check if it's the expected format
            if 'chain' in data:
                blocks_data = data['chain']
            elif isinstance(data, list):
                blocks_data = data
            else:
                logger.error("Unknown ledger format")
                return False
            
            # Parse blocks
            self.blocks = [Block.from_dict(b) for b in blocks_data]
            logger.info(f"Loaded {len(self.blocks)} blocks from ledger")
            return True
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in ledger: {e}")
            return False
        except Exception as e:
            logger.error(f"Error loading ledger: {e}")
            return False
    
    def verify_block_hash(self, block: Block) -> bool:
        """
        Verify a single block's hash.
        
        Args:
            block: Block to verify
            
        Returns:
            True if valid, False otherwise
        """
        calculated_hash = block.calculate_hash()
        if block.hash != calculated_hash:
            self.errors.append(
                f"Block {block.index}: Hash mismatch! "
                f"Expected {calculated_hash}, got {block.hash}"
            )
            return False
        return True
    
    def verify_chain_links(self) -> bool:
        """
        Verify that all blocks are properly linked.
        
        Returns:
            True if chain is valid, False otherwise
        """
        valid = True
        
        for i in range(1, len(self.blocks)):
            current = self.blocks[i]
            previous = self.blocks[i - 1]
            
            # Check if previous_hash matches
            if current.previous_hash != previous.hash:
                self.errors.append(
                    f"Block {current.index}: Chain break! "
                    f"Previous hash {current.previous_hash} doesn't match "
                    f"block {previous.index} hash {previous.hash}"
                )
                valid = False
            
            # Check index sequence
            if current.index != previous.index + 1:
                self.warnings.append(
                    f"Block {current.index}: Index gap detected "
                    f"(previous was {previous.index})"
                )
        
        return valid
    
    def verify_genesis_block(self) -> bool:
        """
        Verify the genesis block.
        
        Returns:
            True if valid, False otherwise
        """
        if not self.blocks:
            self.errors.append("No blocks in ledger")
            return False
        
        genesis = self.blocks[0]
        
        # Genesis block should have index 0
        if genesis.index != 0:
            self.warnings.append(
                f"Genesis block has index {genesis.index}, expected 0"
            )
        
        # Genesis block should have previous_hash of "0" or empty
        if genesis.previous_hash not in ["0", "", "genesis"]:
            self.warnings.append(
                f"Genesis block has non-standard previous_hash: {genesis.previous_hash}"
            )
        
        return True
    
    def verify_timestamps(self) -> bool:
        """
        Verify timestamp ordering.
        
        Returns:
            True if valid, False otherwise
        """
        valid = True
        
        for i in range(1, len(self.blocks)):
            try:
                current_time = datetime.fromisoformat(self.blocks[i].timestamp)
                previous_time = datetime.fromisoformat(self.blocks[i - 1].timestamp)
                
                if current_time < previous_time:
                    self.warnings.append(
                        f"Block {self.blocks[i].index}: Timestamp goes backwards "
                        f"(from {previous_time} to {current_time})"
                    )
            except (ValueError, TypeError) as e:
                self.warnings.append(
                    f"Block {self.blocks[i].index}: Invalid timestamp format: {e}"
                )
        
        return valid
    
    def verify_all(self) -> bool:
        """
        Run all verifications.
        
        Returns:
            True if ledger is valid, False otherwise
        """
        logger.info("Starting ledger verification...")
        logger.info("=" * 60)
        
        # Reset errors/warnings
        self.errors = []
        self.warnings = []
        
        # Load ledger
        if not self.load_ledger():
            return False
        
        # Verify genesis block
        self.verify_genesis_block()
        
        # Verify each block's hash
        logger.info("Verifying block hashes...")
        hash_valid = True
        for block in self.blocks:
            if not self.verify_block_hash(block):
                hash_valid = False
        
        # Verify chain links
        logger.info("Verifying chain links...")
        chain_valid = self.verify_chain_links()
        
        # Verify timestamps
        logger.info("Verifying timestamps...")
        self.verify_timestamps()
        
        # Report results
        logger.info("=" * 60)
        logger.info("VERIFICATION RESULTS")
        logger.info("=" * 60)
        logger.info(f"Total blocks: {len(self.blocks)}")
        logger.info(f"Errors: {len(self.errors)}")
        logger.info(f"Warnings: {len(self.warnings)}")
        
        if self.errors:
            logger.error("\nERRORS FOUND:")
            for error in self.errors:
                logger.error(f"  ✗ {error}")
        
        if self.warnings:
            logger.warning("\nWARNINGS:")
            for warning in self.warnings:
                logger.warning(f"  ⚠ {warning}")
        
        # Overall result
        is_valid = hash_valid and chain_valid and len(self.errors) == 0
        
        logger.info("=" * 60)
        if is_valid:
            logger.info("✓ LEDGER IS VALID - Chain integrity verified!")
        else:
            logger.error("✗ LEDGER IS INVALID - Chain integrity compromised!")
        logger.info("=" * 60)
        
        return is_valid
    
    def get_statistics(self) -> dict:
        """
        Get ledger statistics.
        
        Returns:
            Dictionary of statistics
        """
        if not self.blocks:
            return {}
        
        return {
            "total_blocks": len(self.blocks),
            "genesis_block": self.blocks[0].timestamp if self.blocks else None,
            "latest_block": self.blocks[-1].timestamp if self.blocks else None,
            "first_index": self.blocks[0].index if self.blocks else None,
            "last_index": self.blocks[-1].index if self.blocks else None,
            "has_gaps": len(self.warnings) > 0,
            "is_valid": len(self.errors) == 0,
        }
    
    def export_report(self, output_path: str) -> None:
        """
        Export verification report to file.
        
        Args:
            output_path: Path to output file
        """
        report = {
            "verification_time": datetime.now().isoformat(),
            "ledger_path": str(self.ledger_path),
            "statistics": self.get_statistics(),
            "errors": self.errors,
            "warnings": self.warnings,
            "valid": len(self.errors) == 0,
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Report exported to: {output_path}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Verify QFZZ blockchain ledger integrity"
    )
    parser.add_argument(
        "ledger",
        nargs="?",
        default="qfzz_ledger.json",
        help="Path to ledger file (default: qfzz_ledger.json)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Quiet mode (errors only)"
    )
    parser.add_argument(
        "-o", "--output",
        help="Export verification report to file"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show statistics only"
    )
    
    args = parser.parse_args()
    
    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    elif args.quiet:
        logging.getLogger().setLevel(logging.ERROR)
    
    # Create verifier
    verifier = LedgerVerifier(args.ledger)
    
    # Show stats only
    if args.stats:
        if verifier.load_ledger():
            stats = verifier.get_statistics()
            print(json.dumps(stats, indent=2))
        return 0
    
    # Run verification
    is_valid = verifier.verify_all()
    
    # Export report if requested
    if args.output:
        verifier.export_report(args.output)
    
    # Exit with appropriate code
    return 0 if is_valid else 1


if __name__ == "__main__":
    sys.exit(main())
