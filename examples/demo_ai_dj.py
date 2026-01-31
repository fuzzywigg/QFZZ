#!/usr/bin/env python3
"""
Demo script for AI DJ with multiple personas.

Shows different DJ personalities introducing tracks and responding to listeners.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from qfzz.dj.ai_dj import AIDJ


def demo_track_introductions():
    """Demonstrate track introductions with different personas."""
    print("\n" + "=" * 80)
    print("AI DJ TRACK INTRODUCTIONS DEMO")
    print("=" * 80)

    track = {
        "title": "Midnight City",
        "artist": "M83",
        "genre": "Electronic",
    }

    personas = ["energetic", "chill", "intellectual", "storyteller"]

    for persona in personas:
        print(f"\n--- {persona.upper()} DJ ---")
        try:
            dj = AIDJ(persona=persona)
            print(f"DJ Name: {dj.get_persona_name()}")
            print(f"Description: {dj.get_persona_description()}")
            print(f"\nIntroducing: {track['title']} by {track['artist']}")

            intro = dj.introduce_track(track)
            print(f"DJ: {intro}")
        except Exception as e:
            print(f"Error: {e}")


def demo_listener_responses():
    """Demonstrate listener responses with different personas."""
    print("\n" + "=" * 80)
    print("AI DJ LISTENER RESPONSES DEMO")
    print("=" * 80)

    listener_requests = [
        "Can you play some jazz next?",
        "Love this track!",
        "This station is awesome!",
    ]

    personas = ["energetic", "chill", "intellectual"]

    for persona in personas:
        print(f"\n--- {persona.upper()} DJ ---")
        try:
            dj = AIDJ(persona=persona)

            for request in listener_requests[:2]:  # Just show 2 requests per persona
                print(f"\nListener: {request}")
                response = dj.respond_to_listener(request)
                print(f"DJ: {response}")
        except Exception as e:
            print(f"Error: {e}")


def demo_track_transitions():
    """Demonstrate track transitions."""
    print("\n" + "=" * 80)
    print("AI DJ TRACK TRANSITIONS DEMO")
    print("=" * 80)

    current_track = {
        "title": "Midnight City",
        "artist": "M83",
        "genre": "Electronic",
    }

    next_track = {
        "title": "Digital Love",
        "artist": "Daft Punk",
        "genre": "Electronic",
    }

    personas = ["energetic", "chill", "storyteller"]

    for persona in personas:
        print(f"\n--- {persona.upper()} DJ ---")
        try:
            dj = AIDJ(persona=persona)

            print(f"Transitioning from: {current_track['title']}")
            print(f"                to: {next_track['title']}")

            transition = dj.generate_transition(current_track, next_track)
            print(f"DJ: {transition}")
        except Exception as e:
            print(f"Error: {e}")


def demo_station_ids():
    """Demonstrate station IDs."""
    print("\n" + "=" * 80)
    print("AI DJ STATION IDs DEMO")
    print("=" * 80)

    personas = ["energetic", "chill", "intellectual", "storyteller"]

    for persona in personas:
        print(f"\n--- {persona.upper()} DJ ---")
        try:
            dj = AIDJ(persona=persona)

            station_id = dj.generate_station_id()
            print(f"DJ: {station_id}")
        except Exception as e:
            print(f"Error: {e}")


def demo_tts():
    """Demonstrate text-to-speech (if available)."""
    print("\n" + "=" * 80)
    print("AI DJ TEXT-TO-SPEECH DEMO")
    print("=" * 80)

    print("\nAttempting to initialize TTS (requires OpenAI API key)...")

    try:
        dj = AIDJ(persona="energetic", enable_tts=True)

        if dj.tts_client and dj.tts_client.is_available():
            print("✓ TTS client initialized successfully")

            text = "Welcome to QFZZ FuzzyRadio! Let's get this party started!"
            print(f"\nGenerating audio for: '{text}'")

            audio_data = dj.synthesize_speech(text)

            if audio_data:
                print(f"✓ Generated {len(audio_data)} bytes of audio")
                print("  (In a real scenario, this would be played through speakers)")
            else:
                print("✗ Failed to generate audio")
        else:
            print("✗ TTS client not available (check API key configuration)")
    except Exception as e:
        print(f"✗ Error initializing TTS: {e}")


def demo_full_dj_session():
    """Demonstrate a full DJ session."""
    print("\n" + "=" * 80)
    print("FULL AI DJ SESSION DEMO")
    print("=" * 80)

    try:
        dj = AIDJ(persona="energetic")
        print(f"\nWelcome! Your DJ tonight is {dj.get_persona_name()}")
        print(f"{dj.get_persona_description()}\n")

        # Station ID
        station_id = dj.generate_station_id()
        print(f"DJ: {station_id}\n")

        # First track
        track1 = {
            "title": "Electric Feel",
            "artist": "MGMT",
            "genre": "Indie Rock",
        }
        intro1 = dj.introduce_track(track1)
        print(f"DJ: {intro1}")
        print(f"♪ Now Playing: {track1['title']} by {track1['artist']} ♪\n")

        # Listener interaction
        print("Listener: This is great! Can you play more like this?")
        response = dj.respond_to_listener("This is great! Can you play more like this?")
        print(f"DJ: {response}\n")

        # Second track with transition
        track2 = {
            "title": "Feel It Still",
            "artist": "Portugal. The Man",
            "genre": "Alternative",
        }
        transition = dj.generate_transition(track1, track2)
        print(f"DJ: {transition}")
        print(f"♪ Now Playing: {track2['title']} by {track2['artist']} ♪\n")

        print("--- Session Complete ---")
    except Exception as e:
        print(f"Error during session: {e}")


def main():
    """Run all demos."""
    print("\n" + "#" * 80)
    print("# QFZZ AI DJ SYSTEM DEMO")
    print("#" * 80)
    print("\nThis demo showcases the AI DJ system with multiple personas.")
    print("Each persona has a unique personality and style.\n")

    # Check if LLM is available
    from qfzz.core.llm_router import LLMRouter

    router = LLMRouter()
    available = router.get_stats()["available_providers"]

    if not available or available == []:
        print("⚠ WARNING: No LLM providers available!")
        print("  Configure at least one provider (Google Gemini, Groq, etc.)")
        print("  The demo will use fallback responses.\n")
    else:
        print(f"✓ Using LLM providers: {', '.join(available)}\n")

    # Run demos
    try:
        demo_track_introductions()
        demo_listener_responses()
        demo_track_transitions()
        demo_station_ids()
        demo_tts()
        demo_full_dj_session()

        print("\n" + "#" * 80)
        print("# DEMO COMPLETE")
        print("#" * 80)
        print("\nAll personas are ready to spin tracks on QFZZ FuzzyRadio! 🎵\n")
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n\nDemo error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
