"""Knowledge graph empty/falsy fingerprint skips tempo and key nodes."""

from qfzz.knowledge.graph import QFZZKnowledgeGraph


def test_empty_fingerprint_creates_no_tempo_or_key(tmp_path):
    kg = QFZZKnowledgeGraph(str(tmp_path / "kg.json"))
    kg.add_track_node(
        "t-empty-fp",
        {
            "title": "Quiet Song",
            "artist": "Art",
            "genre": "Ambient",
            "fingerprint": {},
        },
    )
    assert kg.graph.has_node("t-empty-fp")
    tempo_nodes = [n for n, d in kg.graph.nodes(data=True) if d.get("type") == "tempo"]
    key_nodes = [n for n, d in kg.graph.nodes(data=True) if d.get("type") == "musical_key"]
    assert tempo_nodes == []
    assert key_nodes == []


def test_falsy_bpm_and_key_skip_feature_nodes(tmp_path):
    kg = QFZZKnowledgeGraph(str(tmp_path / "kg2.json"))
    kg.add_track_node(
        "t-falsy",
        {
            "title": "Null Features",
            "artist": "Art",
            "genre": "Jazz",
            "fingerprint": {"bpm": None, "key": None},
        },
    )
    tempo_nodes = [n for n, d in kg.graph.nodes(data=True) if d.get("type") == "tempo"]
    key_nodes = [n for n, d in kg.graph.nodes(data=True) if d.get("type") == "musical_key"]
    assert tempo_nodes == []
    assert key_nodes == []


def test_followed_by_boosts_related_score(tmp_path):
    kg = QFZZKnowledgeGraph(str(tmp_path / "kg3.json"))
    kg.add_track_node("t1", {"title": "Alpha Tune", "artist": "X", "genre": "Pop"})
    kg.add_track_node("t2", {"title": "Beta Tune", "artist": "Y", "genre": "Rock"})
    kg.add_track_node("t3", {"title": "Gamma Tune", "artist": "Z", "genre": "Pop"})
    kg.record_listening_event("t1", "t2")
    related = kg.find_related_tracks("t1", limit=5)
    assert related[0] == "t2"
