import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import node_graph_lib as lib

# 최소 DialogueTree JSON 블록(마커 포함) — 3노드 선형 체인 + 화자
BLOB = (
    '{"type":"NodeCanvas.DialogueTrees.DialogueTree","nodes":['
    '{"$type":"River.Incident.EventInfoNode","$id":"0"},'
    '{"statement":{"_text":"A"},"actorRef":{"uid":"guid-jun"},"_UID":"uid-a",'
    '"$type":"NodeCanvas.DialogueTrees.StatementNode","$id":"1"},'
    '{"statement":{"_text":"B"},"actorRef":{"uid":"guid-guard"},"_UID":"uid-b",'
    '"$type":"NodeCanvas.DialogueTrees.StatementNode","$id":"2"}],'
    '"connections":['
    '{"_sourceNode":{"$ref":"0"},"_targetNode":{"$ref":"1"},"$type":"x.DTConnection"},'
    '{"_sourceNode":{"$ref":"1"},"_targetNode":{"$ref":"2"},"$type":"x.DTConnection"}]}'
)
ACTOR_DEFS = {"guid-jun": {"locKey": "Actor_Jun", "cht": "李莫"},
              "guid-guard": {"locKey": "Actor_Guard", "cht": "大魁"}}

def test_extract_blob_with_name():
    raw = (b"\x00\x00DT_Test\x08\x00\x00\x00" + BLOB.encode("utf-8") + b"\x00\x00")
    blobs = lib.extract_tree_blobs(raw)
    assert len(blobs) == 1
    name, txt = blobs[0]
    assert name == "DT_Test"
    assert json.loads(txt)["type"] == "NodeCanvas.DialogueTrees.DialogueTree"

def test_parse_tree_chain_and_actors():
    tree = lib.parse_tree("DT_Test", BLOB, ACTOR_DEFS)
    nodes = {n["id"]: n for n in tree["nodes"]}
    assert nodes["1"]["uid"] == "uid-a" and nodes["1"]["actor"] == "Actor_Jun"
    assert nodes["2"]["uid"] == "uid-b" and nodes["2"]["actor"] == "Actor_Guard"
    assert nodes["0"]["out"] == ["1"]
    assert nodes["1"]["out"] == ["2"]
    assert tree["entry"] == "0"

def test_build_graph_uid_index():
    # BLOB을 임시 .assets로 저장 후 build_graph
    import tempfile
    d = tempfile.mkdtemp()
    with open(os.path.join(d, "sharedassets99.assets"), "wb") as f:
        f.write(b"\x00\x00DT_Test\x08\x00\x00\x00" + BLOB.encode("utf-8"))
    g = lib.build_graph(d, ACTOR_DEFS)
    assert "uid-a" in g["uid_index"]
    assert g["uid_index"]["uid-b"]["id"] == "2"
    assert g["uid_index"]["uid-b"]["scene"] in g["scenes"]
