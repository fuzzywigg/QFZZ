#!/usr/bin/env python3
"""
Simple example showing QFZZ DJ interaction
"""

import sys
from pathlib import Path

# Add parent directory to path so we can import qfzz
sys.path.insert(0, str(Path(__file__).parent.parent))

from qfzz import PersonalizedDJ

def main():
    print("=" * 60)
    print("QFZZ DJ Interaction Example")
    print("=" * 60)
    
    # Create a DJ
    dj = PersonalizedDJ(name="DJ Quantum", edge_mode=True)
    
    # Simulate a conversation
    user_id = "example_user"
    
    print("\n1. First time user")
    greeting = dj.greet_user(user_id, "Jordan")
    print(f"DJ: {greeting}")
    
    print("\n2. Ask for music recommendation")
    response = dj.interact(user_id, "What music should I listen to?")
    print(f"User: What music should I listen to?")
    print(f"DJ: {response}")
    
    print("\n3. Update preferences")
    dj.update_preferences(user_id, ["jazz", "hip-hop", "electronic"])
    print("Updated preferences: jazz, hip-hop, electronic")
    
    print("\n4. Ask for music again")
    response = dj.interact(user_id, "Play something for me")
    print(f"User: Play something for me")
    print(f"DJ: {response}")
    
    print("\n5. Express mood")
    response = dj.interact(user_id, "I'm feeling happy and energetic!")
    print(f"User: I'm feeling happy and energetic!")
    print(f"DJ: {response}")
    
    print("\n6. Check trust score")
    trust = dj.get_trust_score(user_id)
    print(f"Your trust score: {trust:.2f}")
    
    print("\n" + "=" * 60)
    print("Conversation complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
