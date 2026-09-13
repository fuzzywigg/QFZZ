"""Edge coverage for knowledge graph save failures, metadata-less tracks, related lookup."""

from pathlib import Path
from unittest.mock import patch

from qfzz.knowledge.graph import QFZZKnowledgeGraph


def test_save_graph_oserror_swallowed(tmp_path: Path):
    path = tmp_path / "kg.json"
    kg = QFZZKnowledgeGraph(str(path))
    kg.add_entity_node("artist:a", "artist", {"name": "A"})
    with patch("builtins.open", side_effect=OSError("ro fs")):
        kg.save_graph()  # must not raise


def test_add_track_without_artist_genre_skips_short_words(tmp_path: Path):
    path = tmp_path / "kg.json"
    kg = QFZZKnowledgeGraph(str(path))
    kg.add_track_node("t1", {"title": "a Big Journey"})
    assert kg.graph.has_node("t1")
    # "a" and "Big" length<=4 skipped; "Journey" (>4) creates concept
    assert kg.graph.has_node("concept:journey")
    assert not any(n.startswith("artist:") for n in kg.graph.nodes)
    assert not any(n.startswith("genre:") for n in kg.graph.nodes)


def test_fingerprint_tempo_and_key_nodes(tmp_path: Path):
    path = tmp_path / "kg.json"
    kg = QFZZKnowledgeGraph(str(path))
    kg.add_track_node(
        "t2",
        {
            "title": "Pulse",
            "artist": "Nova",
            "genre": "Ambient",
            "fingerprint": {"bpm": 128, "key": "Am"},
        },
    )
    assert kg.graph.has_node("tempo:120s BPM")
    assert kg.graph.has_node("key:Am")
    # IN_KEY edge exists
    edge = kg.graph.get_edge_data("t2", "key:Am")
    assert edge is not None
    assert any(v.get("relationship") == "IN_KEY" for v in edge.values())


def test_find_related_unknown_and_shared_artist(tmp_path: Path):
    path = tmp_path / "kg.json"
    kg = QFZZKnowledgeGraph(str(path))
    assert kg.find_related_tracks("missing") == []
    kg.add_track_node("t_a", {"title": "One", "artist": "Shared", "genre": "Rock"})
    kg.add_track_node("t_b", {"title": "Two", "artist": "Shared", "genre": "Pop"})
    related = kg.find_related_tracks("t_a")
    assert "t_b" in related
