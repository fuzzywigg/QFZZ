"""
Knowledge Graph Core for QFZZ.
Implements a network graph to link tracks, artists, genres, and concepts.
"""

import networkx as nx
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class QFZZKnowledgeGraph:
    """
    Semantic Knowledge Graph for Audio Content.
    Uses NetworkX to model relationships between entities.
    """
    
    def __init__(self, persistence_path: str = "qfzz_knowledge_graph.json"):
        self.persistence_path = persistence_path
        self.graph = nx.MultiDiGraph()
        self.loaded = False
        self._load_graph()
        
    def _load_graph(self):
        """Load graph from disk if exists."""
        if os.path.exists(self.persistence_path):
            try:
                with open(self.persistence_path, 'r') as f:
                    data = json.load(f)
                    self.graph = nx.node_link_graph(data)
                self.loaded = True
                logger.info(f"Loaded Knowledge Graph: {self.graph.number_of_nodes()} nodes, {self.graph.number_of_edges()} edges")
            except Exception as e:
                logger.error(f"Failed to load Knowledge Graph: {e}")
                self.graph = nx.MultiDiGraph()
        else:
            logger.info("Initializing new Knowledge Graph")
            self.graph = nx.MultiDiGraph()

    def save_graph(self):
        """Persist graph to disk."""
        try:
            data = nx.node_link_data(self.graph)
            with open(self.persistence_path, 'w') as f:
                json.dump(data, f, indent=2)
            logger.debug("Saved Knowledge Graph to disk")
        except Exception as e:
            logger.error(f"Failed to save Knowledge Graph: {e}")

    def add_track_node(self, track_id: str, metadata: Dict[str, Any]):
        """Add a track node and link it to its metadata entities."""
        if not self.graph.has_node(track_id):
            self.graph.add_node(track_id, type="track", **metadata)
            logger.info(f"Added Track Node: {track_id}")
            
            # Link to Artist
            artist = metadata.get('artist')
            if artist:
                artist_id = f"artist:{artist.lower().replace(' ', '_')}"
                self.add_entity_node(artist_id, "artist", {"name": artist})
                self.add_relationship(track_id, artist_id, "PERFORMED_BY")
                
            # Link to Genre
            genre = metadata.get('genre')
            if genre:
                genre_id = f"genre:{genre.lower().replace(' ', '_')}"
                self.add_entity_node(genre_id, "genre", {"name": genre})
                self.add_relationship(track_id, genre_id, "BELONGS_TO")

            # Link to Concepts (from title or explicit tags)
            title = metadata.get('title', '')
            # Simple keyword extraction (Mocking AI extraction)
            keywords = [w for w in title.split() if len(w) > 4] 
            for kw in keywords:
                concept_id = f"concept:{kw.lower()}"
                self.add_entity_node(concept_id, "concept", {"name": kw})
                self.add_relationship(track_id, concept_id, "EVOKES")
                
            # Deep Sonic Features (if available)
            fingerprint = metadata.get('fingerprint')
            if fingerprint:
                # Discretize Tempo (e.g., '120-130 BPM')
                bpm = fingerprint.get('bpm')
                if bpm:
                    tempo_range = f"{int(bpm // 10 * 10)}s BPM" # e.g. "120s BPM"
                    tempo_id = f"tempo:{tempo_range}"
                    self.add_entity_node(tempo_id, "tempo", {"name": tempo_range})
                    self.add_relationship(track_id, tempo_id, "HAS_TEMPO", weight=0.8)
                
                # Musical Key
                key = fingerprint.get('key')
                if key:
                    key_id = f"key:{key}"
                    self.add_entity_node(key_id, "musical_key", {"name": key})
                    self.add_relationship(track_id, key_id, "IN_KEY", weight=0.9)
                
            self.save_graph()

    def add_entity_node(self, node_id: str, node_type: str, props: Dict[str, Any]):
        """Add a generic entity node (Artist, Genre, Concept)."""
        if not self.graph.has_node(node_id):
            self.graph.add_node(node_id, type=node_type, **props)

    def add_relationship(self, source: str, target: str, rel_type: str, weight: float = 1.0):
        """Add a directed edge between nodes."""
        # Simple MultiDiGraph allows multiple edges, but we want to Update weight if exists?
        # For now, just add edge
        self.graph.add_edge(source, target, relationship=rel_type, weight=weight)

    def record_listening_event(self, track_id: str, next_track_id: str):
        """
        Create a temporal link between two tracks played in sequence.
        This builds a 'SongPath' or Markov Chain.
        """
        if self.graph.has_node(track_id) and self.graph.has_node(next_track_id):
            # Check if edge exists
            if self.graph.has_edge(track_id, next_track_id):
                # Strengthen the link? NetworkX multigraph adds NEW edge by default 
                # or we can assume simple graph behavior for this specific edge type
                # Let's just add it for now, can perform aggregate later
                self.graph.add_edge(track_id, next_track_id, relationship="FOLLOWED_BY", timestamp=datetime.now().isoformat())
            else:
                self.graph.add_edge(track_id, next_track_id, relationship="FOLLOWED_BY", timestamp=datetime.now().isoformat())
            
            self.save_graph()

    def find_related_tracks(self, track_id: str, limit: int = 5) -> List[str]:
        """
        Traverse graph to find related tracks.
        Strategy: 
        1. Direct 'FOLLOWED_BY' neighbors (Listening History)
        2. Siblings (Same Artist/Genre)
        3. Concept cousins (Share concepts)
        """
        if not self.graph.has_node(track_id):
            return []
            
        related_scores = {}
        
        # 1. Direct Neighbors (Outgoing)
        for neighbor in self.graph.successors(track_id):
            edge_data = self.graph.get_edge_data(track_id, neighbor)
            # Handle MultiDiGraph returning dict of edges
            for k, v in edge_data.items():
                if v.get('relationship') == 'FOLLOWED_BY':
                     related_scores[neighbor] = related_scores.get(neighbor, 0) + 2.0
        
        # 2. Neighbors of Neighbors (Concepts/Artists)
        # Track -> Artist -> Other Track
        # Track -> Concept -> Other Track
        for neighbor in self.graph.successors(track_id):
            edge_data = self.graph.get_edge_data(track_id, neighbor)
            for k, v in edge_data.items():
                 rel = v.get('relationship')
                 if rel in ['PERFORMED_BY', 'BELONGS_TO', 'EVOKES']:
                     # This neighbor is an Entity (Artist/Genre/Concept)
                     # Find tracks connected to THIS entity
                     # In our schema, Track -> Entity. So we look for PREDECESSORS of the entity
                     # (Who else points to this Artist?)
                     for other_track in self.graph.predecessors(neighbor):
                         if other_track != track_id:
                             # Boost score
                             boost = 1.0 if rel == 'PERFORMED_BY' else 0.5
                             related_scores[other_track] = related_scores.get(other_track, 0) + boost

        # Sort by score
        sorted_tracks = sorted(related_scores.items(), key=lambda x: x[1], reverse=True)
        return [t[0] for t in sorted_tracks[:limit]]

    def export_d3_json(self) -> Dict[str, Any]:
        """Export graph in D3.js compatible format for frontend visualization."""
        return nx.node_link_data(self.graph)
