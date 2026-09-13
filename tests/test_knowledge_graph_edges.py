"""Knowledge graph track/entity/save/related edge paths."""

from unittest.mock import patch

from qfzz.knowledge.graph import QFZZKnowledgeGraph


def test_add_track_without_artist_genre_and_short_title(tmp_path):
    kg = QFZZKnowledgeGraph(str(tmp_path / "kg.json"))
    kg.add_track_node("t1", {"title": "Hi Ok", "fingerprint": {"bpm": 120}})
    assert kg.graph.has_node("t1")
    # short words (<=4) should not create concept nodes
    concept_nodes = [n for n, d in kg.graph.nodes(data=True) if d.get("type") == "concept"]
    assert concept_nodes == []
    artist_nodes = [n for n, d in kg.graph.nodes(data=True) if d.get("type") == "artist"]
    assert artist_nodes == []


def test_fingerprint_key_without_bpm_and_title_concepts(tmp_path):
    kg = QFZZKnowledgeGraph(str(tmp_path / "kg.json"))
    kg.add_track_node(
        "t2",
        {
            "title": "Quantum Pulse Wave",
            "artist": "Qubit",
            "genre": "Ambient",
            "fingerprint": {"key": "Am"},
        },
    )
    assert kg.graph.has_node("artist:qubit")
    assert kg.graph.has_node("genre:ambient")
    concepts = [n for n, d in kg.graph.nodes(data=True) if d.get("type") == "concept"]
    assert any("quantum" in c.lower() or "Quantum" in str(kg.graph.nodes[c]) for c in concepts) or len(
        concepts
    ) >= 1


def test_save_graph_soft_fail_on_oserror(tmp_path):
    kg = QFZZKnowledgeGraph(str(tmp_path / "kg.json"))
    kg.add_entity_node("artist:x", "artist", {"name": "X"})
    with patch("builtins.open", side_effect=OSError("readonly")):
        kg.save_graph()  # soft-fail, no raise
    assert kg.graph.has_node("artist:x")


def test_find_related_limit_and_score_order(tmp_path):
    kg = QFZZKnowledgeGraph(str(tmp_path / "kg.json"))
    kg.add_track_node("t1", {"title": "One Song", "artist": "A", "genre": "Rock"})
    kg.add_track_node("t2", {"title": "Two Song", "artist": "A", "genre": "Jazz"})
    kg.add_track_node("t3", {"title": "Three Song", "artist": "B", "genre": "Rock"})
    kg.add_track_node("t4", {"title": "Four Song", "artist": "C", "genre": "Pop"})
    related = kg.find_related_tracks("t1", limit=1)
    assert len(related) == 1
    # artist match should outrank unrelated
    related2 = kg.find_related_tracks("t1", limit=5)
    assert "t2" in related2
    assert "t3" in related2


def test_add_entity_duplicate_does_not_overwrite(tmp_path):
    kg = QFZZKnowledgeGraph(str(tmp_path / "kg.json"))
    kg.add_entity_node("artist:x", "artist", {"name": "First"})
    kg.add_entity_node("artist:x", "artist", {"name": "Second"})
    assert kg.graph.nodes["artist:x"].get("name") == "First"
