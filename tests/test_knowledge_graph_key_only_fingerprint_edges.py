"""Knowledge graph key-only fingerprint links IN_KEY without tempo."""

from pathlib import Path

from qfzz.knowledge.graph import QFZZKnowledgeGraph


def test_key_only_fingerprint_adds_in_key_without_tempo(tmp_path: Path):
    kg = QFZZKnowledgeGraph(persistence_path=str(tmp_path / "kg.json"))
    kg.add_track_node(
        "track:1",
        {
            "title": "KeyOnly",
            "artist": "Solo",
            "genre": "ambient",
            "fingerprint": {"key": "Am"},
        },
    )

    assert kg.graph.has_node("key:Am")
    assert kg.graph.has_edge("track:1", "key:Am")
    edge_data = list(kg.graph.get_edge_data("track:1", "key:Am").values())[0]
    assert edge_data.get("relationship") == "IN_KEY"

    tempo_nodes = [n for n in kg.graph.nodes if str(n).startswith("tempo:")]
    assert tempo_nodes == []
