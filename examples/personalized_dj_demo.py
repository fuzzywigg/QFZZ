#!/usr/bin/env python3
"""Personalized DJ Demo

Demonstrates the AI DJ interaction and personalization features.
"""

import logging
from qfzz import PersonalizedDJ

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Run personalized DJ demo"""
    logger.info("\n" + "=" * 60)
    logger.info("QFZZ Personalized DJ - Demo")
    logger.info("=" * 60)
    
    # Create DJ
    dj = PersonalizedDJ(name="DJ Quantum", edge_mode=True)
    
    # Simulate user interaction
    user_id = "user_001"
    
    # First interaction
    greeting = dj.greet_user(user_id, "Alex")
    logger.info(f"\nDJ: {greeting}")
    
    # User asks for music
    response = dj.interact(user_id, "Can you recommend some music?")
    logger.info(f"\nUser: Can you recommend some music?")
    logger.info(f"DJ: {response}")
    
    # Update preferences
    dj.update_preferences(user_id, ["jazz", "electronic", "ambient"])
    
    # Ask again
    response = dj.interact(user_id, "Play something for me")
    logger.info(f"\nUser: Play something for me")
    logger.info(f"DJ: {response}")
    
    # Check trust score
    trust = dj.get_trust_score(user_id)
    logger.info(f"\nUser Trust Score: {trust:.2f}")
    
    logger.info("\n" + "=" * 60)
    logger.info("Personalized DJ demo completed successfully!")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
