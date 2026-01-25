"""
Personalized DJ Agent System
Implements the AI DJ that knows users and is part of their community of trust
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class UserProfile:
    """User profile for personalization"""
    user_id: str
    name: str
    music_preferences: List[str] = field(default_factory=list)
    interaction_history: List[Dict[str, Any]] = field(default_factory=list)
    trust_score: float = 0.5
    community_connections: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


class PersonalizedDJ:
    """
    AI DJ that provides personalized music curation and interaction
    
    Features:
    - Learns user preferences over time
    - Provides conversational interaction
    - Curates music based on mood and context
    - Part of user's community of trust
    - Supports edge device deployment
    """
    
    def __init__(self, name: str = "DJ Quantum", edge_mode: bool = True):
        self.name = name
        self.edge_mode = edge_mode
        self.user_profiles: Dict[str, UserProfile] = {}
        self.conversation_context: Dict[str, List[str]] = {}
        
        logger.info(f"Initialized {self.name} in {'edge' if edge_mode else 'cloud'} mode")
        
    def greet_user(self, user_id: str, user_name: Optional[str] = None) -> str:
        """Greet a user, personalizing based on history"""
        if user_id not in self.user_profiles:
            # New user
            profile = UserProfile(user_id=user_id, name=user_name or "Friend")
            self.user_profiles[user_id] = profile
            return f"Hey {profile.name}! Welcome to QFZZ! I'm {self.name}, your personal DJ. Let's discover some great music together!"
        
        profile = self.user_profiles[user_id]
        interactions = len(profile.interaction_history)
        return f"Welcome back, {profile.name}! Great to see you again. We've shared {interactions} sessions together. What's your vibe today?"
        
    def interact(self, user_id: str, message: str) -> str:
        """
        Handle user interaction with the DJ
        
        Args:
            user_id: Unique user identifier
            message: User's message to the DJ
            
        Returns:
            DJ's response
        """
        if user_id not in self.user_profiles:
            self.greet_user(user_id)
            
        profile = self.user_profiles[user_id]
        
        # Track conversation
        if user_id not in self.conversation_context:
            self.conversation_context[user_id] = []
        self.conversation_context[user_id].append(message)
        
        # Record interaction
        profile.interaction_history.append({
            'timestamp': datetime.now(),
            'message': message,
            'type': 'user_message'
        })
        
        # Build trust over time
        profile.trust_score = min(1.0, profile.trust_score + 0.01)
        
        # Generate contextual response
        response = self._generate_response(profile, message)
        
        profile.interaction_history.append({
            'timestamp': datetime.now(),
            'message': response,
            'type': 'dj_response'
        })
        
        return response
        
    def _generate_response(self, profile: UserProfile, message: str) -> str:
        """
        Generate a contextual response based on user profile and message
        
        This is a simplified implementation. In production, this would use
        a personalized LLM running on edge device.
        """
        message_lower = message.lower()
        
        # Music recommendation request
        if any(word in message_lower for word in ['recommend', 'suggest', 'play', 'music']):
            if profile.music_preferences:
                prefs = ", ".join(profile.music_preferences[:3])
                return f"Based on your taste for {prefs}, I've got the perfect track queued up! Let me play something special for you."
            return "I'm learning your taste! Let's start with something smooth. Tell me what genres you're into?"
            
        # Mood-based interaction
        if any(word in message_lower for word in ['happy', 'excited', 'energetic']):
            return "I love that energy! Let me bring up the tempo with some uplifting beats!"
            
        if any(word in message_lower for word in ['sad', 'down', 'chill', 'relax']):
            return "I hear you. Let me create a calming atmosphere with some mellow vibes."
            
        # Community and trust
        if any(word in message_lower for word in ['community', 'friends', 'trust']):
            connections = len(profile.community_connections)
            return f"You're part of a trusted community of {connections} music lovers. Together we're discovering amazing sounds!"
            
        # Default personalized response
        interactions = len(profile.interaction_history)
        return f"I'm here for you! We've built great rapport through {interactions // 2} conversations. How can I help you discover music today?"
        
    def update_preferences(self, user_id: str, preferences: List[str]):
        """Update user music preferences"""
        if user_id in self.user_profiles:
            profile = self.user_profiles[user_id]
            profile.music_preferences.extend(preferences)
            profile.music_preferences = list(set(profile.music_preferences))  # Remove duplicates
            logger.info(f"Updated preferences for {profile.name}")
            
    def add_to_community(self, user_id: str, friend_id: str):
        """Connect users in the trust community"""
        if user_id in self.user_profiles:
            profile = self.user_profiles[user_id]
            if friend_id not in profile.community_connections:
                profile.community_connections.append(friend_id)
                logger.info(f"Added {friend_id} to {profile.name}'s community")
                
    def get_trust_score(self, user_id: str) -> float:
        """Get user's trust score in the community"""
        if user_id in self.user_profiles:
            return self.user_profiles[user_id].trust_score
        return 0.0
