# -*- coding: utf-8 -*-
"""步骤 1: 通过 db_manage API 创建 学生信息库 + 学生表(students) + 演示数据"""
import json
from common import (api, DB_NAME, DB_COMMENT, TABLE_NAME, TABLE_COMMENT,
                    COLUMNS, build_rows)

out = {}

# 0. 幂等: 已存在同名库则直接复用
code, res = api("POST", "/database/list/page", {"page": 1, "page_size": 100, "qtype": "already"})
dbs = res.get("data", {}).get("items", []) if isinstance(res.get("data"), dict) else res.get("data", [])
if isinstance(dbs, dict):
    dbs = dbs.get("items", [])
db_id = None
for d in dbs:
    if not isinstance(d, dict):
        continue
    if d.get("name") == DB_NAME or DB_NAME in str(d.get("database_name", "")):
        db_id = d.get("id")
if db_id is None:
    code, res = api("POST", "/database", {"db_name": DB_NAME, "comment": DB_COMMENT})
    print("create db:", code, json.dumps(res, ensure_ascii=False)[:400])
    assert code == 200 and res.get("code") == 200, res
    db_id = res["data"]["id"]
out["database_id"] = db_id
print("database_id =", db_id)

# 1. 创建学生表
code, res = api("POST", f"/database/{db_id}/table",
                {"table_name": TABLE_NAME, "comment": TABLE_COMMENT, "columns": COLUMNS})
print("create table:", code, json.dumps(res, ensure_ascii=False)[:400])

# 2. 找到表 id
code, res = api("GET", f"/database/{db_id}/table/list?page=1&limit=100")
tables = res.get("data", [])
if isinstance(tables, dict):
    tables = tables.get("items", tables.get("list", []))
table_id = None
for t in tables:
    if t.get("name") == TABLE_NAME:
        table_id = t.get("id")
assert table_id, f"table list: {json.dumps(res, ensure_ascii=False)[:500]}"
out["table_id"] = table_id
print("table_id =", table_id)

# 3. 插入演示数据
code, res = api("PUT", f"/database/{db_id}/table_data/{table_id}",
                {"add_items": build_rows(), "update_items": [], "delete_items": []})
print("insert data:", code, json.dumps(res, ensure_ascii=False)[:300])
assert code == 200, res

# 4. 校验: 查询行数
code, res = api("GET", f"/database/{db_id}/table_data/{table_id}?page=1&limit=3")
print("select preview:", code, json.dumps(res, ensure_ascii=False)[:400])

with open("/tmp/t2s_db.json", "w") as f:
    json.dump(out, f)
print("saved /tmp/t2s_db.json ->", out)
