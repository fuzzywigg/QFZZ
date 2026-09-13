"""Knowledge graph missing-track / listening-skip / export edges."""

from qfzz.knowledge.graph import QFZZKnowledgeGraph


def test_record_listening_skips_when_either_node_missing(tmp_path):
    kg = QFZZKnowledgeGraph(str(tmp_path / "kg.json"))
    kg.add_track_node("t1", {"title": "Only One", "artist": "Solo"})
    before = kg.graph.number_of_edges()
    kg.record_listening_event("t1", "ghost")
    kg.record_listening_event("ghost", "t1")
    assert kg.graph.number_of_edges() == before


def test_record_listening_links_existing_pair(tmp_path):
    kg = QFZZKnowledgeGraph(str(tmp_path / "kg.json"))
    kg.add_track_node("t1", {"title": "Alpha Wave", "artist": "A"})
    kg.add_track_node("t2", {"title": "Beta Wave", "artist": "B"})
    before = kg.graph.number_of_edges()
    kg.record_listening_event("t1", "t2")
    assert kg.graph.number_of_edges() == before + 1
    assert kg.graph.has_edge("t1", "t2")


def test_export_d3_json_empty_and_populated(tmp_path):
    kg = QFZZKnowledgeGraph(str(tmp_path / "kg.json"))
    empty = kg.export_d3_json()
    assert "nodes" in empty
    # networkx node_link_data uses "links" or "edges" depending on version
    edge_key = "links" if "links" in empty else "edges"
    assert edge_key in empty
    assert empty["nodes"] == []
    assert empty[edge_key] == []

    kg.add_track_node("t1", {"title": "Wave Pulse", "artist": "Qubit", "genre": "Ambient"})
    payload = kg.export_d3_json()
    assert len(payload["nodes"]) >= 1
    assert any(
        (n.get("id") == "t1" if isinstance(n, dict) else False)
        or (isinstance(n, dict) and n.get("type") == "track")
        for n in payload["nodes"]
    )
