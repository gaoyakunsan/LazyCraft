# -*- coding: utf-8 -*-
"""阶段 2: 准备演示数据
1. 知识库「产品知识库」+ 上传产品文档
2. 应用「产品知识问答助手」+ RAG 工作流草稿(开始→RAG召回器→大模型→结束)
3. Text2SQL 应用工作流中插入「绘图指令拼接」代码块节点(与手册第 5 步一致)
"""
import copy
import json
import random
import sys
import uuid

import requests

sys.path.insert(0, "/root/LazyCraft/scripts/doc_images")
from doc_common import api_token

BASE = "http://127.0.0.1:30382/console/api"
H = {"Authorization": "Bearer " + api_token()}
TPL = "/root/LazyCraft/scripts/doc_images"

KB_NAME = "产品知识库"
RAG_APP_NAME = "产品知识问答助手"

# 在线模型展示配置(与手册第 7 步一致: SiliconFlow / Qwen2.5-72B-Instruct)
BRAND_ID = 20
MODEL_NAME = "Qwen/Qwen2.5-72B-Instruct"
MODEL_PAYLOAD = {
    "payload__model_source": "online_model",
    "payload__source": "SiliconFlow",
    "payload__base_url": "",
    "payload__source_id": BRAND_ID,
    "payload__base_model_selected_keys": [MODEL_NAME],
    "payload__base_model": MODEL_NAME,
    "payload__can_finetune": False,
    "payload__model_id": BRAND_ID,
    "payload__model_generate_control": {
        "payload__temperature": 0.6, "payload__top_p": 0.7, "payload__max_tokens": 4096,
    },
    "payload__base_model_id": BRAND_ID,
}

PRODUCT_DOC = """# 智能风扇Pro 产品手册

## 产品概述
智能风扇Pro是本公司 2025 年推出的旗舰智能风扇,支持 APP 远程控制、语音控制、自然风模拟与睡眠模式。

## 售后服务与保修政策
- 智能风扇Pro 整机保修期为 **2 年**,自购买之日起计算。
- 电机核心部件保修期为 **5 年**。
- 保修期内非人为损坏免费维修;人为损坏收取配件成本费。
- 全国联保,支持 400-800-1234 客服热线报修。

## 产品参数
| 型号 | 风量(CFM) | 噪音(dB) | 额定功率 | 上市价格 |
| --- | --- | --- | --- | --- |
| 智能风扇Pro | 3200 | 28 | 45W | 599 元 |
| 智能风扇Lite | 2100 | 32 | 30W | 299 元 |

## 常见问题
1. 问:智能风扇Pro的保修期是多久? 答:整机保修 2 年,电机保修 5 年。
2. 问:支持哪些语音助手? 答:支持小爱同学、天猫精灵与自定义 API 接入。
3. 问:滤网多久更换一次? 答:建议 6 个月更换一次,配件价格 39 元。
"""


def api(method, path, body=None):
    r = requests.request(method, BASE + path, headers=H, json=body, timeout=120)
    try:
        return r.status_code, r.json()
    except ValueError:
        return r.status_code, r.text


def make_node(nid, data, x, y, w=195, h=92):
    return {
        "id": nid, "type": "custom", "data": data,
        "position": {"x": x, "y": y}, "positionAbsolute": {"x": x, "y": y},
        "targetPosition": "left", "sourcePosition": "right",
        "width": w, "height": h, "selected": False, "dragging": False,
    }


def edge(src, dst, s_type, t_type):
    return {
        "id": uuid.uuid4().hex, "source": src, "target": dst,
        "sourceHandle": "source", "targetHandle": "target", "type": "custom",
        "data": {"sourceType": s_type, "targetType": t_type}, "selected": False,
        "sourceHandleId": None, "targetHandleId": None,
    }


def in_port(var, source_title, src_type="str", readonly=True):
    return {
        "id": "target",
        "param_source_shape": [{
            "id": uuid.uuid4().hex, "variable_mode": "mode-line", "variable_name": var,
            "variable_type": src_type, "payload__batch_flag": False,
            "sourceNodeTitle": source_title,
        }],
        "param_check_success": True, "param_input_error": [],
        "param_input_success": [{
            "id": var, "variable_name": var, "variable_type": src_type,
            "variable_mode": "mode-line", "variable_name_readonly": readonly,
            "variable_type_readonly": True, "variable_mode_readonly": False,
            "variable_type_options": [src_type], "variable_file_type": "default",
        }],
    }


# ---------- 1. 知识库 ----------
def seed_kb():
    code, res = api("POST", "/kb/list", {"page": 1, "limit": 100, "qtype": ""})
    items = res.get("data") or []
    if isinstance(items, dict):
        items = items.get("items", [])
    kb = next((k for k in items if k.get("name") == KB_NAME), None)
    if kb:
        print("kb exists:", kb["id"])
    else:
        code, kb = api("POST", "/kb/create", {
            "name": KB_NAME,
            "description": "智能风扇等产品的说明文档与售后政策知识库",
        })
        assert code == 200, kb
        print("kb created:", kb["id"])
    kb_id = kb["id"]

    code, res = api("POST", f"/kb/file/list?knowledge_base_id={kb_id}", {"page": 1, "limit": 20})
    files = res.get("data") or []
    if isinstance(files, dict):
        files = files.get("items", [])
    if files:
        print("kb files exist:", [f.get("name") for f in files])
        return kb_id
    # 上传产品文档
    r = requests.post(
        BASE + "/kb/upload",
        headers=H,
        files={"file": ("智能风扇Pro产品手册.md", PRODUCT_DOC.encode(), "text/markdown")},
        timeout=120,
    )
    assert r.status_code == 200, r.text
    file_info = r.json()["files"][0]
    code, res = api("POST", "/kb/file/add", {
        "knowledge_base_id": kb_id, "file_ids": [file_info["id"]],
    })
    print("upload+add:", code, res)
    return kb_id


# ---------- 2. RAG 应用 ----------
def seed_rag_app(kb_id):
    code, res = api("POST", "/apps/list/page", {"page": 1, "limit": 50, "qtype": "mine", "search_name": RAG_APP_NAME})
    app_id = next((a["id"] for a in res.get("data", []) if a.get("name") == RAG_APP_NAME), None)
    if app_id:
        print("rag app exists:", app_id)
    else:
        code, res = api("POST", "/apps", {
            "name": RAG_APP_NAME,
            "description": "基于产品知识库的智能问答助手:先从知识库召回相关片段,再由大模型生成准确回答。",
        })
        assert code == 201, res
        app_id = res["id"]
        print("rag app created:", app_id)

    # --- 文档管理资源 ---
    tpl_res = json.load(open(f"{TPL}/tpl_document_res.json"))
    res_id = "resource_" + uuid.uuid4().hex.replace("-", "_")[:32]
    medium_key = uuid.uuid4().hex
    doc_res = copy.deepcopy(tpl_res)
    for target in (doc_res, doc_res["data"]):
        target["id"] = res_id
        target["title"] = "文档管理-1"
        target["payload__dataset_path"] = ["/app/upload/knowledge/00000000-0000-0000-0000-000000000001/" + KB_NAME]
        target["payload__knowledge_id"] = [kb_id]
        target["payload__activated_groups"] = [{
            "key": medium_key, "name": "MediumChunk",
            "embed": {"payload__model_source": "none"},
        }]
        target["selected"] = False

    # --- 节点 ---
    start = json.load(open(f"{TPL}/tpl_start.json"))
    start["data"]["config__output_shape"] = [{
        "id": uuid.uuid4().hex, "variable_mode": "mode-line", "variable_name": "query",
        "payload__batch_flag": False, "variable_type": "str",
    }]

    end = json.load(open(f"{TPL}/tpl_end.json"))
    end["data"]["config__input_ports"] = [{
        "id": "target",
        "param_source_shape": [{
            "id": uuid.uuid4().hex, "variable_name": "output", "variable_type": "str",
            "variable_mode": "mode-line", "variable_name_readonly": True,
            "variable_mode_readonly": False, "variable_type_readonly": False,
            "sourceNodeTitle": "大模型-1",
        }],
        "param_check_success": True, "param_input_error": [],
        "param_input_success": [{
            "id": "answer", "variable_name": "answer", "variable_type": "str",
            "variable_mode": "mode-line", "payload__batch_flag": False,
        }],
    }]
    end["data"]["config__input_shape"] = [{
        "id": "answer", "variable_mode": "mode-line", "variable_name": "answer",
        "variable_type": "str", "payload__batch_flag": False,
    }]

    ret = json.load(open(f"{TPL}/tpl_retriever.json"))
    ret_d = ret["data"]
    ret_d["title"] = "RAG召回器-1"
    ret_d.pop("selected", None)
    ret_d["payload__topk"] = 3
    ret_d["payload__output_format"] = "content"
    ret_d["payload__join"] = True
    ret_d["payload__group_name"] = "MediumChunk"
    ret_d["payload__doc"] = res_id
    ret_d["config__input_ports"] = [in_port("query", "开始")]

    llm = json.load(open(f"{TPL}/tpl_llm.json"))
    llm_d = llm["data"]
    llm_d["title"] = "大模型-1"
    llm_d.pop("selected", None)
    llm_d.update(MODEL_PAYLOAD)
    llm_d["payload__prompt"] = {
        "system": "你是一名严谨的产品客服助手,必须仅依据参考资料回答用户问题,不得编造。",
        "user": "参考资料:\n{query}\n\n用户问题:{question}\n\n请仅依据参考资料用中文简洁回答;若资料未涉及,请如实说明。",
    }
    llm_d["payload__stream"] = True
    llm_d["payload__use_history"] = True
    llm_d["config__input_shape"] = [
        {"id": "query", "variable_name": "query", "variable_type": "str",
         "variable_mode": "mode-line", "variable_name_readonly": True,
         "variable_type_readonly": False, "variable_mode_readonly": False,
         "variable_type_options": ["str", "dict"], "configurable": True},
        {"id": uuid.uuid4().hex, "variable_name": "question", "variable_type": "str",
         "variable_mode": "mode-line", "variable_name_readonly": False,
         "variable_type_readonly": False, "variable_mode_readonly": False,
         "variable_type_options": ["str", "dict"], "configurable": True},
    ]
    llm_d["config__input_ports"] = [
        {**in_port("query", "RAG召回器-1")},
        {**in_port("question", "开始", readonly=False)},
    ]

    RET_ID, LLM_ID = str(random.randint(10**12, 10**13 - 1)), str(random.randint(10**12, 10**13 - 1))
    nodes = [
        make_node("__start__", start["data"], -620, 260, 195, 56),
        make_node(RET_ID, ret_d, -240, 150),
        make_node(LLM_ID, llm_d, 140, 150, 195, 120),
        make_node("__end__", end["data"], 560, 260, 195, 56),
    ]
    edges = [
        edge("__start__", RET_ID, "start", "retriever"),
        edge(RET_ID, LLM_ID, "retriever", "onlinellm"),
        edge("__start__", LLM_ID, "start", "onlinellm"),
        edge(LLM_ID, "__end__", "onlinellm", "end"),
    ]
    graph = {
        "nodes": nodes, "edges": edges, "resources": [doc_res],
        "edgeMode": "bezier", "viewport": {"x": 150, "y": 120, "zoom": 0.85},
    }
    code, draft = api("GET", f"/apps/{app_id}/workflows/draft")
    body = {"graph": graph}
    if code == 200 and draft.get("hash"):
        body["hash"] = draft["hash"]
    code, res = api("POST", f"/apps/{app_id}/workflows/draft", body)
    print("save rag draft:", code, json.dumps(res, ensure_ascii=False)[:200])
    json.dump({"app_id": app_id, "ret_id": RET_ID, "llm_id": LLM_ID,
               "res_id": res_id}, open("/tmp/rag_app.json", "w"))
    return app_id


# ---------- 3. Text2SQL 应用补「绘图指令拼接」代码块 ----------
CHART_PROMPT_CODE = '''def build_chart_prompt(query: str):
    """把SQL查询结果包装成明确的画图指令,驱动React智能体调用画图工具"""
    return (
        "请根据下面的数据查询结果立即调用绘图工具生成图表:"
        "分类对比类数据(如各院系/各部门人数)调用 generate_bar_chart 绘制柱状图;"
        "占比构成类数据调用 generate_pie_chart 绘制饼图;"
        "若两类都适用则各绘制一张。"
        "禁止向用户提问或请求澄清,必须直接调用工具完成绘图。"
        "绘图完成后,在 Answer 中必须包含两部分内容,缺一不可:\\n"
        "1.「数据明细」:原样复述下方【数据查询结果】中的全部数据,一字不改;\\n"
        "2.「图表链接」:每张图表的 Markdown 图片链接,格式为 ![](图片链接),并用一句话说明图表内容。\\n\\n"
        "【数据查询结果】\\n" + str(query)
    )
'''


def extend_t2s():
    t2s = json.load(open("/tmp/t2s_app.json"))
    app_id = t2s["app_id"]
    code, draft = api("GET", f"/apps/{app_id}/workflows/draft")
    assert code == 200 and draft.get("graph"), draft
    graph = draft["graph"] if isinstance(draft.get("graph"), dict) else json.loads(draft["graph"])
    if any(n["data"].get("title") == "绘图指令拼接" for n in graph["nodes"]):
        print("t2s code node exists")
        return
    tpl = json.load(open("/tmp/code_node.json"))
    code_d = copy.deepcopy(tpl["data"])
    code_d["title"] = "绘图指令拼接"
    code_d["desc"] = "把 SQL 查询结果包装成明确的画图指令"
    code_d["payload__code"] = CHART_PROMPT_CODE
    code_d["payload__code_language"] = "python3"
    code_d.pop("selected", None)
    code_d["config__input_shape"] = [{
        "id": uuid.uuid4().hex, "variable_mode": "mode-line", "variable_name": "query",
        "variable_type": "str", "payload__batch_flag": False,
    }]
    code_d["config__output_shape"] = [{
        "id": "x", "variable_name": "x", "variable_type": "str",
        "variable_mode": "mode-line", "payload__batch_flag": False,
    }]
    sql_node = next(n for n in graph["nodes"] if n["data"].get("title") == "Text2SQL 数据查询")
    fc_node = next(n for n in graph["nodes"] if n["data"].get("title") == "图表生成")
    code_d["config__input_ports"] = [in_port("query", "Text2SQL 数据查询")]

    CODE_ID = str(random.randint(10**12, 10**13 - 1))
    x = (sql_node["position"]["x"] + fc_node["position"]["x"]) / 2
    y = fc_node["position"]["y"] + 260
    graph["nodes"].append(make_node(CODE_ID, code_d, x, y, 195, 104))
    # SQL -> CODE -> FC, 删除 SQL->FC 直连
    graph["edges"] = [
        e for e in graph["edges"]
        if not (e["source"] == sql_node["id"] and e["target"] == fc_node["id"])
    ]
    graph["edges"] += [
        edge(sql_node["id"], CODE_ID, "sqlcall", "code"),
        edge(CODE_ID, fc_node["id"], "code", "functioncall"),
    ]
    body = {"graph": graph}
    if draft.get("hash"):
        body["hash"] = draft["hash"]
    code, res = api("POST", f"/apps/{app_id}/workflows/draft", body)
    print("save t2s draft:", code, json.dumps(res, ensure_ascii=False)[:200])


if __name__ == "__main__":
    kb_id = seed_kb()
    seed_rag_app(kb_id)
    extend_t2s()
    print("SEED-DONE")
