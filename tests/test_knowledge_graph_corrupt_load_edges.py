"""Knowledge graph corrupt JSON load soft-recovers to empty MultiDiGraph."""

from qfzz.knowledge.graph import QFZZKnowledgeGraph


def test_corrupt_persistence_file_starts_empty_graph(tmp_path):
    path = tmp_path / "kg.json"
    path.write_text("{not-json", encoding="utf-8")
    kg = QFZZKnowledgeGraph(str(path))
    assert kg.graph.number_of_nodes() == 0
    assert kg.graph.number_of_edges() == 0
    assert kg.loaded is False
