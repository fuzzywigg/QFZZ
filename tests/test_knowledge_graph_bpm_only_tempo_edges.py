"""Knowledge graph bpm-only fingerprint creates tempo node + HAS_TEMPO."""

from qfzz.knowledge.graph import QFZZKnowledgeGraph


def test_bpm_only_fingerprint_creates_tempo_node(tmp_path):
    kg = QFZZKnowledgeGraph(str(tmp_path / "kg.json"))
    kg.add_track_node("t-bpm", {"title": "Pulse", "fingerprint": {"bpm": 124}})
    assert kg.graph.has_node("tempo:120s BPM")
    key_nodes = [n for n in kg.graph.nodes if str(n).startswith("key:")]
    assert key_nodes == []
    assert kg.graph.has_edge("t-bpm", "tempo:120s BPM")
    edge_data = kg.graph.get_edge_data("t-bpm", "tempo:120s BPM")
    assert any(d.get("relationship") == "HAS_TEMPO" for d in edge_data.values())
