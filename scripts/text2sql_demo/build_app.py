# -*- coding: utf-8 -*-
"""步骤 2: 创建 Text2SQL 应用 + 组装工作流(开始→Text2SQL→图表生成→分析报告→结束) + 保存草稿"""
import copy
import json
import uuid

from common import api, APP_NAME, DB_NAME, DB_COMMENT, TABLE_NAME, TABLE_COMMENT, COLUMNS

BRAND_ID = 20                      # SiliconFlow 大模型品牌行(lazymodel_online_models.id=20, 挂 api_key)
MODEL_NAME = "Qwen/Qwen2.5-72B-Instruct"
SQL_RESOURCE_ID = "resource_" + uuid.uuid4().hex.replace("-", "_")[:32]
PIE_RES_ID = "resource_f24d5b0e_d1ed_404a_8d54_27adf9792333"   # 与范本一致
BAR_RES_ID = "resource_4a66a23e_f8fd_4e20_add2_e6380bc28ec7"

T = lambda p: json.load(open(f"templates/templates_{p}"))

insight = T("insight_graph.json")
sqlcall_t = T("sqlcall.json")["data"]
funcall_t = T("funcall.json")["data"]
llm_t = T("llm.json")["data"]

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


def node_data(base, kind, title, desc, extra=None):
    d = copy.deepcopy(base)
    d["title"] = title
    d["desc"] = desc
    d.pop("selected", None)
    if extra:
        d.update(extra)
    return d


def make_node(nid, data, x, y):
    return {
        "id": nid, "type": "custom", "data": data,
        "position": {"x": x, "y": y}, "positionAbsolute": {"x": x, "y": y},
        "targetPosition": "left", "sourcePosition": "right",
        "width": 195, "height": 92, "selected": False,
        "dragging": False,
    }


def edge(src, dst, s_type, t_type):
    return {
        "id": uuid.uuid4().hex, "source": src, "target": dst,
        "sourceHandle": "source", "targetHandle": "target", "type": "custom",
        "data": {"sourceType": s_type, "targetType": t_type}, "selected": False,
        "sourceHandleId": None, "targetHandleId": None,
    }


# ---------- 1. 应用 ----------
APP_DESC = ("高校教学演示:输入自然语言问题,自动生成 SQL 查询学生表,调用 ECharts 工具绘制图表,并生成数据分析报告。"
            "完整展示 Text2SQL → 数据可视化 → 智能报告 的 Agent 工作流。")
code, res = api("POST", "/apps/list/page", {"page": 1, "limit": 50, "qtype": "mine", "search_name": APP_NAME})
app_id = next((a["id"] for a in res.get("data", []) if a.get("name") == APP_NAME), None)
if app_id:
    print("app exists:", app_id)
else:
    code, res = api("POST", "/apps", {"name": APP_NAME, "description": APP_DESC})
    print("create app:", code, json.dumps(res, ensure_ascii=False)[:200])
    assert code == 201, res
    app_id = res["id"]
print("app_id =", app_id)

# ---------- 2. 资源: sql-manager(平台数据库) ----------
tables_array = [{
    "name": TABLE_NAME, "comment": TABLE_COMMENT,
    "columns": copy.deepcopy(COLUMNS),
    "key": uuid.uuid4().hex,
}]
tables_dict = {"tables": [{
    "name": TABLE_NAME, "comment": TABLE_COMMENT,
    "columns": [{"name": c["name"], "data_type": c["data_type"], "nullable": c["nullable"],
                 "comment": c["comment"], "is_primary_key": c["is_primary_key"]}
                for c in COLUMNS],
}]}

sql_manager_res = {
    "id": SQL_RESOURCE_ID, "type": "sql-manager", "title": "学生信息库",
    "desc": "数据库管理器", "payload__kind": "SqlManager", "title_en": "数据库管理",
    "status": True,
    "config__parameters": copy.deepcopy(
        [r for r in insight["resources"][2]["config__parameters"]]),
    "classification": "built-in", "name": "sql-manager", "description": "数据库管理器",
    "payload__source": "platform", "payload__db_type": "MySQL",
    "payload__database_id": 30001, "payload__database_name": DB_NAME,
    "payload__tables_info_dict_array": tables_array,
    "payload__tables_info_dict": tables_dict,
    "ref_id": 30001,
}
# 引擎从 data 子对象取 payload(sql_manager 伪节点)
sql_manager_res["data"] = copy.deepcopy(sql_manager_res)
sql_manager_res["data"]["id"] = SQL_RESOURCE_ID

pie_res = next(r for r in insight["resources"] if r.get("name", "").endswith("generate_pie_chart"))
bar_res = next(r for r in insight["resources"] if r.get("name", "").endswith("generate_bar_chart"))
resources = [sql_manager_res, pie_res, bar_res]

# ---------- 3. 节点 ----------
START_ID, END_ID = "__start__", "__end__"
import random
SQL_ID, FC_ID, LLM_ID = (str(random.randint(10**12, 10**13 - 1)) for _ in range(3))

start_data = copy.deepcopy(next(n for n in insight["nodes"] if n["id"] == "__start__")["data"])

end_data = copy.deepcopy(next(n for n in insight["nodes"] if n["id"] == "__end__")["data"])
end_data["config__input_ports"][0]["param_source_shape"] = [{
    "id": uuid.uuid4().hex, "variable_name": "output", "variable_type": "any",
    "variable_mode": "mode-line", "variable_name_readonly": True,
    "variable_mode_readonly": False, "variable_type_readonly": False,
    "sourceNodeTitle": "数据分析报告",
}]

sql_in_port = {
    "id": "target",
    "param_source_shape": [{
        "id": "input_1", "variable_mode": "mode-line", "variable_name": "query",
        "variable_type": "str", "payload__batch_flag": False, "sourceNodeTitle": "开始",
    }],
    "param_check_success": True, "param_input_error": [],
    "param_input_success": [{
        "id": "query", "variable_name": "query", "variable_type": "str",
        "variable_mode": "mode-line", "variable_name_readonly": True,
        "variable_type_readonly": True, "variable_mode_readonly": False,
        "variable_type_options": ["str"], "variable_file_type": "default",
    }],
}
sqlcall_data = node_data(sqlcall_t, "SqlCall", "Text2SQL 数据查询",
                         "将自然语言转换为 SQL 并查询学生表",
                         extra={
                             **MODEL_PAYLOAD,
                             "payload__sql_manager": SQL_RESOURCE_ID,
                             "payload__sql_manager_name": "sql-manager",
                             "payload__sql_examples": "查询各个院系的学生人数: SELECT department, COUNT(*) AS cnt FROM students GROUP BY department",
                             "payload__use_llm_for_sql_result": True,
                         })
sqlcall_data["config__input_ports"] = [sql_in_port]

fc_in_port = copy.deepcopy(sql_in_port)
fc_in_port["param_source_shape"][0]["sourceNodeTitle"] = "Text2SQL 数据查询"
funcall_data = node_data(funcall_t, "FunctionCall", "图表生成",
                         "调用 ECharts MCP 工具绘制柱状图/饼图",
                         extra={**MODEL_PAYLOAD, "payload__algorithm": "React"})
funcall_data["config__input_ports"] = [fc_in_port]

REPORT_PROMPT = {
    "system": "你是一名资深数据分析专家，擅长撰写结构化的数据分析报告。请根据提供的数据查询结果和图表分析信息，用中文撰写一份专业的数据分析报告。",
    "user": "请根据以下数据查询与图表分析结果，撰写一份数据分析报告。\n\n【数据查询与图表分析结果】\n{query}\n\n报告要求：\n一、数据概览：概述查询结果中的关键数据；\n二、图表解读：结合图表说明数据的分布与对比情况；\n三、结论与建议：给出2-3条数据驱动的结论或建议。\n\n请直接输出报告正文，使用 Markdown 格式。",
}
llm_in_port = {
    "id": "target",
    "param_source_shape": [
        {"id": uuid.uuid4().hex, "variable_name": "output", "variable_type": "any",
         "variable_mode": "mode-line", "variable_name_readonly": True,
         "variable_mode_readonly": False, "variable_type_readonly": False,
         "sourceNodeTitle": "图表生成", "payload__batch_flag": False},
    ],
    "param_check_success": True, "param_input_error": [],
    "param_input_success": [
        {"id": "query", "variable_name": "query", "variable_type": "str",
         "variable_mode": "mode-line", "payload__batch_flag": False},
    ],
}
llm_data = node_data(llm_t, "OnlineLLM", "数据分析报告",
                     "根据查询与图表结果生成分析报告",
                     extra={
                         **MODEL_PAYLOAD,
                         "payload__prompt": REPORT_PROMPT,
                         "payload__stream": True,
                         "payload__use_history": False,
                     })
llm_data["config__input_shape"] = llm_in_port["param_input_success"]
llm_data["config__input_ports"] = [llm_in_port]

nodes = [
    make_node(START_ID, start_data, -760, 300),
    make_node(SQL_ID, sqlcall_data, -400, 285),
    make_node(FC_ID, funcall_data, -40, 285),
    make_node(LLM_ID, llm_data, 330, 285),
    make_node(END_ID, end_data, 700, 300),
]
edges = [
    edge(START_ID, SQL_ID, "start", "sqlcall"),
    edge(SQL_ID, FC_ID, "sqlcall", "functioncall"),
    edge(FC_ID, LLM_ID, "functioncall", "onlinellm"),
    edge(LLM_ID, END_ID, "onlinellm", "end"),
]
graph = {
    "nodes": nodes, "edges": edges, "resources": resources,
    "edgeMode": "bezier",
    "viewport": {"x": 250.0, "y": 160.0, "zoom": 0.75},
}

json.dump(graph, open("/tmp/t2s_graph.json", "w"), ensure_ascii=False, indent=1)

# ---------- 4. 保存草稿 ----------
code, draft = api("GET", f"/apps/{app_id}/workflows/draft")
cur_hash = draft.get("hash") if code == 200 else None
body = {"graph": graph}
if cur_hash:
    body["hash"] = cur_hash
code, res = api("POST", f"/apps/{app_id}/workflows/draft", body)
print("save draft:", code, json.dumps(res, ensure_ascii=False)[:300])
assert code == 200, res

json.dump({"app_id": app_id}, open("/tmp/t2s_app.json", "w"))
print("saved /tmp/t2s_app.json ->", {"app_id": app_id})
