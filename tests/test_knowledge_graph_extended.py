"""Expanded knowledge graph coverage: corrupt load, entities, listening events."""

from qfzz.knowledge.graph import QFZZKnowledgeGraph


class TestKnowledgeGraphExtended:
    def test_corrupt_file_starts_empty(self, tmp_path):
        path = tmp_path / "kg.json"
        path.write_text("{not valid json")
        kg = QFZZKnowledgeGraph(str(path))
        assert kg.graph.number_of_nodes() == 0

    def test_add_entity_and_relationship(self, tmp_path):
        kg = QFZZKnowledgeGraph(str(tmp_path / "kg.json"))
        kg.add_entity_node("artist:x", "artist", {"name": "X"})
        kg.add_entity_node("genre:y", "genre", {"name": "Y"})
        kg.add_relationship("artist:x", "genre:y", "ASSOCIATED_WITH", weight=0.5)
        assert kg.graph.has_edge("artist:x", "genre:y")
        kg.save_graph()
        reloaded = QFZZKnowledgeGraph(str(tmp_path / "kg.json"))
        assert reloaded.graph.has_node("artist:x")

    def test_record_listening_event_noop_for_missing(self, tmp_path):
        kg = QFZZKnowledgeGraph(str(tmp_path / "kg.json"))
        kg.record_listening_event("missing-a", "missing-b")
        assert kg.graph.number_of_edges() == 0

    def test_record_listening_event_strengthens_path(self, tmp_path):
        kg = QFZZKnowledgeGraph(str(tmp_path / "kg.json"))
        kg.add_track_node("t1", {"title": "One Song", "artist": "A", "genre": "Rock"})
        kg.add_track_node("t2", {"title": "Two Song", "artist": "B", "genre": "Rock"})
        kg.record_listening_event("t1", "t2")
        kg.record_listening_event("t1", "t2")
        related = kg.find_related_tracks("t1", limit=5)
        assert "t2" in related

    def test_concept_links_from_long_title_words(self, tmp_path):
        kg = QFZZKnowledgeGraph(str(tmp_path / "kg.json"))
        kg.add_track_node(
            "t3",
            {"title": "Cosmic Waves Forever", "artist": "Band", "genre": "Ambient"},
        )
        assert kg.graph.has_node("concept:cosmic")
        assert kg.graph.has_node("concept:waves")
        assert kg.graph.has_node("concept:forever")

    def test_export_d3_json_shape(self, tmp_path):
        kg = QFZZKnowledgeGraph(str(tmp_path / "kg.json"))
        kg.add_track_node("t1", {"title": "Hello", "artist": "A", "genre": "Jazz"})
        exported = kg.export_d3_json()
        assert "nodes" in exported
        assert isinstance(exported["nodes"], list)
        assert len(exported["nodes"]) >= 1

    def test_duplicate_track_node_ignored(self, tmp_path):
        path = tmp_path / "kg.json"
        kg = QFZZKnowledgeGraph(str(path))
        kg.add_track_node("t1", {"title": "First Title", "artist": "A", "genre": "Jazz"})
        before = kg.graph.number_of_nodes()
        kg.add_track_node("t1", {"title": "Second Title", "artist": "B", "genre": "Rock"})
        assert kg.graph.number_of_nodes() == before
        assert kg.graph.nodes["t1"]["title"] == "First Title"
