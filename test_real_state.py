"""
Test the honeycomb state management system.
"""

from qfzz.core.state import StateManager

print("🍯 Testing Honeycomb State Management")
print("="*50 + "\n")

# Create state manager
state_manager = StateManager(honeycomb_dir="honeycomb")

# Add a track
print("📀 Setting current track...")
state_manager.set_current_track(
    track_id="track_001",
    title="Test Drive",
    artist="Test Artist",
    genre="Electronic",
    duration=180.0
)

# Get it back
track = state_manager.get_current_track()
print(f"✅ Current Track: {track['title']} by {track['artist']}")

# Add to playlist
print("\n📋 Adding songs to playlist...")
state_manager.add_to_playlist(
    track_id="track_002",
    title="Another Song",
    artist="Another Artist",
    priority=5
)
state_manager.add_to_playlist(
    track_id="track_003",
    title="Third Song",
    artist="Third Artist",
    priority=8
)

playlist = state_manager.get_playlist()
print(f"✅ Playlist has {len(playlist['queue'])} tracks")

# Update listener count
print("\n👥 Updating listener count...")
state_manager.update_listener_count(42)
listener_state = state_manager.get_listener_state()
print(f"✅ Active listeners: {listener_state['active_listeners']}")

print("\n" + "="*50)
print("🎉 State management test complete!")
print(f"📂 Check the 'honeycomb' directory for JSON files")
print("="*50)