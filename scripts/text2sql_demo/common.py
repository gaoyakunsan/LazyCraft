# -*- coding: utf-8 -*-
"""Text2SQL 高校教学演示 —— 公共配置

平台: LazyCraft (http://127.0.0.1:30382)
租户: 00000000-0000-0000-0000-000000000000 (ui-verify-temp 为 owner)
"""
import json
import urllib.request

BASE = "http://127.0.0.1:30382/console/api"
TOKEN = open("/tmp/lc_token.txt").read().strip()

APP_NAME = "学生数据分析助手（Text2SQL）"
DB_NAME = "student_info"
DB_COMMENT = "高校教学演示数据库，存储学生基本信息与学业数据"
TABLE_NAME = "students"
TABLE_COMMENT = "学生信息表，存储在校学生的基本信息、院系、专业与学业成绩数据"

COLUMNS = [
    {"name": "id", "type": "INTEGER", "data_type": "INTEGER", "comment": "主键ID",
     "nullable": False, "default": None, "is_unique": True, "unique_group": "primary_pk",
     "is_primary_key": True, "is_foreign_key": False, "foreign_key_info": None},
    {"name": "student_no", "type": "VARCHAR", "data_type": "VARCHAR", "comment": "学号",
     "nullable": True, "default": None, "is_unique": False, "unique_group": None,
     "is_primary_key": False, "is_foreign_key": False, "foreign_key_info": None},
    {"name": "name", "type": "VARCHAR", "data_type": "VARCHAR", "comment": "学生姓名",
     "nullable": True, "default": None, "is_unique": False, "unique_group": None,
     "is_primary_key": False, "is_foreign_key": False, "foreign_key_info": None},
    {"name": "gender", "type": "VARCHAR", "data_type": "VARCHAR", "comment": "性别（男/女）",
     "nullable": True, "default": None, "is_unique": False, "unique_group": None,
     "is_primary_key": False, "is_foreign_key": False, "foreign_key_info": None},
    {"name": "age", "type": "INTEGER", "data_type": "INTEGER", "comment": "年龄",
     "nullable": True, "default": None, "is_unique": False, "unique_group": None,
     "is_primary_key": False, "is_foreign_key": False, "foreign_key_info": None},
    {"name": "department", "type": "VARCHAR", "data_type": "VARCHAR",
     "comment": "所属院系（计算机学院/数学学院/外国语学院/物理学院/经济管理学院）",
     "nullable": True, "default": None, "is_unique": False, "unique_group": None,
     "is_primary_key": False, "is_foreign_key": False, "foreign_key_info": None},
    {"name": "major", "type": "VARCHAR", "data_type": "VARCHAR", "comment": "专业",
     "nullable": True, "default": None, "is_unique": False, "unique_group": None,
     "is_primary_key": False, "is_foreign_key": False, "foreign_key_info": None},
    {"name": "grade", "type": "INTEGER", "data_type": "INTEGER", "comment": "年级（入学年份）",
     "nullable": True, "default": None, "is_unique": False, "unique_group": None,
     "is_primary_key": False, "is_foreign_key": False, "foreign_key_info": None},
    {"name": "gpa", "type": "NUMERIC", "data_type": "NUMERIC",
     "comment": "学分绩点GPA（满分4.0）",
     "nullable": True, "default": None, "is_unique": False, "unique_group": None,
     "is_primary_key": False, "is_foreign_key": False, "foreign_key_info": None},
    {"name": "scholarship", "type": "NUMERIC", "data_type": "NUMERIC",
     "comment": "奖学金金额（元，0表示未获得奖学金）",
     "nullable": True, "default": None, "is_unique": False, "unique_group": None,
     "is_primary_key": False, "is_foreign_key": False, "foreign_key_info": None},
]

# 40 名学生的演示数据
def build_rows():
    data = [
        # (学号, 姓名, 性别, 年龄, 院系, 专业, 年级, GPA, 奖学金)
        ("2022010001", "张伟", "男", 22, "计算机学院", "计算机科学与技术", 2022, 3.8, 8000),
        ("2022010002", "王芳", "女", 21, "计算机学院", "软件工程", 2022, 3.6, 3000),
        ("2022010003", "李娜", "女", 22, "计算机学院", "人工智能", 2022, 3.9, 8000),
        ("2022010004", "刘强", "男", 23, "计算机学院", "计算机科学与技术", 2022, 3.2, 1000),
        ("2022010005", "陈静", "女", 22, "计算机学院", "数据科学与大数据技术", 2022, 3.5, 2000),
        ("2022010006", "杨洋", "男", 22, "计算机学院", "软件工程", 2022, 2.8, 0),
        ("2023010007", "赵敏", "女", 20, "计算机学院", "人工智能", 2023, 3.7, 3000),
        ("2023010008", "孙磊", "男", 21, "计算机学院", "计算机科学与技术", 2023, 3.1, 1000),
        ("2023010009", "周涛", "男", 20, "计算机学院", "网络工程", 2023, 2.5, 0),
        ("2023010010", "吴雪", "女", 20, "计算机学院", "数据科学与大数据技术", 2023, 3.4, 2000),
        ("2022020001", "郑爽", "女", 21, "数学学院", "数学与应用数学", 2022, 3.6, 3000),
        ("2022020002", "冯军", "男", 22, "数学学院", "信息与计算科学", 2022, 2.9, 0),
        ("2022020003", "褚燕", "女", 21, "数学学院", "统计学", 2022, 3.85, 8000),
        ("2023020004", "卫平", "男", 20, "数学学院", "数学与应用数学", 2023, 3.3, 2000),
        ("2023020005", "蒋华", "男", 20, "数学学院", "统计学", 2023, 2.4, 0),
        ("2023020006", "沈玉", "女", 20, "数学学院", "信息与计算科学", 2023, 3.55, 3000),
        ("2023020007", "韩梅", "女", 19, "数学学院", "统计学", 2023, 3.0, 1000),
        ("2022030001", "朱强", "男", 22, "外国语学院", "英语", 2022, 3.1, 1000),
        ("2022030002", "胡丽", "女", 21, "外国语学院", "翻译", 2022, 3.65, 3000),
        ("2022030003", "林芳", "女", 22, "外国语学院", "日语", 2022, 3.2, 2000),
        ("2023030004", "何军", "男", 20, "外国语学院", "英语", 2023, 2.6, 0),
        ("2023030005", "高燕", "女", 20, "外国语学院", "翻译", 2023, 3.75, 8000),
        ("2023030006", "马超", "男", 21, "外国语学院", "英语", 2023, 2.95, 0),
        ("2022040001", "罗成", "男", 22, "物理学院", "物理学", 2022, 3.4, 2000),
        ("2022040002", "梁红", "女", 21, "物理学院", "应用物理学", 2022, 3.55, 3000),
        ("2022040003", "宋伟", "男", 22, "物理学院", "物理学", 2022, 2.7, 0),
        ("2023040004", "唐月", "女", 20, "物理学院", "应用物理学", 2023, 3.9, 8000),
        ("2023040005", "许亮", "男", 20, "物理学院", "光电信息科学与工程", 2023, 3.15, 1000),
        ("2023040006", "邓飞", "男", 21, "物理学院", "物理学", 2023, 2.3, 0),
        ("2023040007", "曹颖", "女", 20, "物理学院", "光电信息科学与工程", 2023, 3.45, 2000),
        ("2022050001", "彭勇", "男", 22, "经济管理学院", "工商管理", 2022, 3.25, 1000),
        ("2022050002", "潘悦", "女", 21, "经济管理学院", "会计学", 2022, 3.7, 3000),
        ("2022050003", "袁媛", "女", 22, "经济管理学院", "金融学", 2022, 3.95, 8000),
        ("2023050004", "蔡明", "男", 20, "经济管理学院", "金融学", 2023, 2.85, 0),
        ("2023050005", "田甜", "女", 20, "经济管理学院", "会计学", 2023, 3.35, 2000),
        ("2023050006", "董浩", "男", 21, "经济管理学院", "工商管理", 2023, 3.05, 1000),
        ("2023050007", "苏晴", "女", 20, "经济管理学院", "经济学", 2023, 3.5, 2000),
        ("2023050008", "吕帅", "男", 20, "经济管理学院", "经济学", 2023, 2.55, 0),
        ("2022050009", "萧然", "男", 22, "经济管理学院", "金融学", 2022, 3.45, 2000),
        ("2023030007", "卢雪", "女", 20, "外国语学院", "日语", 2023, 3.4, 2000),
    ]
    rows = []
    for i, r in enumerate(data, start=1):
        rows.append({
            "id": i, "student_no": r[0], "name": r[1], "gender": r[2], "age": r[3],
            "department": r[4], "major": r[5], "grade": r[6],
            "gpa": r[7], "scholarship": r[8],
        })
    return rows


def api(method, path, body=None, files=None):
    url = BASE + path
    data = None
    headers = {"Authorization": f"Bearer {TOKEN}"}
    if body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())
