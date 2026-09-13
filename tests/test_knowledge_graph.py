"""Tests for QFZZKnowledgeGraph."""

from qfzz.knowledge.graph import QFZZKnowledgeGraph


class TestKnowledgeGraph:
    def test_add_track_links_artist_genre_concepts(self, tmp_path):
        path = tmp_path / "kg.json"
        kg = QFZZKnowledgeGraph(str(path))
        kg.add_track_node(
            "track:1",
            {
                "title": "Cosmic Waves Forever",
                "artist": "Nova Band",
                "genre": "Ambient",
                "fingerprint": {"bpm": 124, "key": "Am"},
            },
        )
        assert kg.graph.has_node("track:1")
        assert kg.graph.has_node("artist:nova_band")
        assert kg.graph.has_node("genre:ambient")
        assert kg.graph.has_node("tempo:120s BPM")
        assert kg.graph.has_node("key:Am")
        assert path.exists()

    def test_related_tracks_via_artist_and_sequence(self, tmp_path):
        path = tmp_path / "kg.json"
        kg = QFZZKnowledgeGraph(str(path))
        meta = {"title": "Alpha Song", "artist": "Same Artist", "genre": "Jazz"}
        kg.add_track_node("t1", meta)
        kg.add_track_node("t2", {"title": "Beta Song", "artist": "Same Artist", "genre": "Jazz"})
        kg.record_listening_event("t1", "t2")
        related = kg.find_related_tracks("t1", limit=5)
        assert "t2" in related
        assert kg.find_related_tracks("missing") == []

    def test_reload_and_export(self, tmp_path):
        path = tmp_path / "kg.json"
        kg = QFZZKnowledgeGraph(str(path))
        kg.add_track_node("t1", {"title": "Hello World", "artist": "A", "genre": "Rock"})
        reloaded = QFZZKnowledgeGraph(str(path))
        assert reloaded.graph.has_node("t1")
        exported = reloaded.export_d3_json()
        assert "nodes" in exported or "links" in exported or "edges" in exported
