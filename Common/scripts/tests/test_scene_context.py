import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import scene_context as sc

GRAPH = {
    "scenes": {"DT_X": {"name": "DT_X", "source": "s.assets", "entry": "0", "nodes": [
        {"id": "0", "type": "EventInfoNode", "uid": None, "actor": None, "cht": None, "text": "", "out": ["1"]},
        {"id": "1", "type": "StatementNode", "uid": "u1", "actor": "Actor_Jun", "cht": "李莫", "text": "A", "out": ["2"]},
        {"id": "2", "type": "StatementNode", "uid": "u2", "actor": "Actor_Guard", "cht": "大魁", "text": "B", "out": ["3"]},
        {"id": "3", "type": "StatementNode", "uid": "u3", "actor": "Actor_Eda", "cht": "艾妲", "text": "C", "out": []},
    ]}},
    "uid_index": {"u1": {"scene": "DT_X", "id": "1"}, "u2": {"scene": "DT_X", "id": "2"},
                  "u3": {"scene": "DT_X", "id": "3"}},
}
STORY = {"u1": "가", "u2": "나", "u3": "다"}

def test_context_before_after():
    ctx = sc.load_context("u2", GRAPH, STORY, hops=6)
    assert ctx["scene"] == "DT_X"
    assert ctx["target"]["kr"] == "나" and ctx["target"]["actor"] == "Actor_Guard"
    assert [n["uid"] for n in ctx["before"]] == ["u1"]
    assert ctx["before"][0]["kr"] == "가"
    assert [n["uid"] for n in ctx["after"]] == ["u3"]


# Regression: cycle in flow graph (u1 -> u2(target) -> u3 -> u2) must not
# re-collect the queried node itself into `after`.
GRAPH_CYCLE = {
    "scenes": {"CY_X": {"name": "CY_X", "source": "s.assets", "entry": "1", "nodes": [
        {"id": "1", "type": "StatementNode", "uid": "cu1", "actor": "Actor_Jun", "cht": "李莫", "text": "A", "out": ["2"]},
        {"id": "2", "type": "StatementNode", "uid": "cu2", "actor": "Actor_Guard", "cht": "大魁", "text": "B", "out": ["3"]},
        {"id": "3", "type": "StatementNode", "uid": "cu3", "actor": "Actor_Eda", "cht": "艾妲", "text": "C", "out": ["2"]},
    ]}},
    "uid_index": {"cu1": {"scene": "CY_X", "id": "1"}, "cu2": {"scene": "CY_X", "id": "2"},
                  "cu3": {"scene": "CY_X", "id": "3"}},
}
STORY_CYCLE = {"cu1": "가", "cu2": "나", "cu3": "다"}

def test_context_cycle_does_not_duplicate_target():
    ctx = sc.load_context("cu2", GRAPH_CYCLE, STORY_CYCLE, hops=6)
    after_uids = [n["uid"] for n in ctx["after"]]
    assert "cu2" not in after_uids
    assert after_uids == ["cu3"]


# Regression: walk must advance through non-StatementNodes (e.g. ActionNode)
# rather than stopping at them, only appending StatementNodes to the result.
GRAPH_NONSTATEMENT = {
    "scenes": {"NS_X": {"name": "NS_X", "source": "s.assets", "entry": "1", "nodes": [
        {"id": "1", "type": "StatementNode", "uid": "nu1", "actor": "Actor_Jun", "cht": "李莫", "text": "A", "out": ["2"]},
        {"id": "2", "type": "ActionNode", "uid": None, "actor": None, "cht": None, "text": "", "out": ["3"]},
        {"id": "3", "type": "StatementNode", "uid": "nu2", "actor": "Actor_Guard", "cht": "大魁", "text": "B", "out": ["4"]},
        {"id": "4", "type": "ActionNode", "uid": None, "actor": None, "cht": None, "text": "", "out": ["5"]},
        {"id": "5", "type": "StatementNode", "uid": "nu3", "actor": "Actor_Eda", "cht": "艾妲", "text": "C", "out": []},
    ]}},
    "uid_index": {"nu1": {"scene": "NS_X", "id": "1"}, "nu2": {"scene": "NS_X", "id": "3"},
                  "nu3": {"scene": "NS_X", "id": "5"}},
}
STORY_NONSTATEMENT = {"nu1": "하나", "nu2": "둘", "nu3": "셋"}

def test_context_walk_traverses_through_nonstatement_nodes():
    ctx = sc.load_context("nu2", GRAPH_NONSTATEMENT, STORY_NONSTATEMENT, hops=6)
    assert [n["uid"] for n in ctx["before"]] == ["nu1"]
    assert [n["uid"] for n in ctx["after"]] == ["nu3"]
