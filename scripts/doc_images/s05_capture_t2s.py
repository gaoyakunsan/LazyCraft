# -*- coding: utf-8 -*-
"""阶段 5: Text2SQL 实战截图 10/20/30/40/50/60/70/71/72/80

全部真实: 真实启用调试、真实运行(Text2SQL→MCP 画图→分析报告,
硅基流动在线模型推理, 图表由 MCP 服务真实生成)。用法:
    python s05_capture_t2s.py canvas|panels|run|all
"""
import json
import sys
import time

import requests

sys.path.insert(0, "/root/LazyCraft/scripts/doc_images")
from doc_common import Shooter, api_token

H = {"Authorization": "Bearer " + api_token()}
BASE = "http://127.0.0.1:30382/console/api"
T2S = json.load(open("/tmp/t2s_app.json"))["app_id"]
WF = f"http://127.0.0.1:30382/app/{T2S}/workflow"

QUESTION = "统计各个学院的学生人数,并用柱状图和饼图展示"

NODES = [
    ("Text2SQL 数据查询", "20-Text2SQL节点配置"),
    ("绘图指令拼接", "30-绘图指令拼接配置"),
    ("图表生成", "40-图表生成节点配置"),
    ("数据分析报告", "50-数据分析报告配置"),
]


def stop_debug():
    requests.post(f"{BASE}/apps/{T2S}/workflows/draft/stop", headers=H, json={}, timeout=120)
    time.sleep(2)


def open_wf(s, wait=6000):
    s.page.goto(WF, wait_until="domcontentloaded")
    s.page.wait_for_timeout(wait)


def click_node(s, name):
    node = s.page.locator(f".react-flow__node:has-text('{name}')").first
    node.evaluate("el => {"
                  "el.dispatchEvent(new MouseEvent('mousedown', {bubbles: true}));"
                  "el.dispatchEvent(new MouseEvent('mouseup', {bubbles: true}));"
                  "el.dispatchEvent(new MouseEvent('click', {bubbles: true}));}")


# ---------- 10 画布总览 ----------
def stage_canvas():
    stop_debug()
    s = Shooter(viewport=(1680, 950))
    try:
        open_wf(s)
        s.page.keyboard.press("Escape")
        s.page.mouse.click(700, 700)
        s.page.wait_for_timeout(800)
        s.shot("10-画布总览", timeout=800)
    finally:
        s.close()


# ---------- 20-50 各节点配置面板 ----------
def stage_panels():
    stop_debug()
    s = Shooter(viewport=(1680, 950))
    try:
        open_wf(s)
        for name, img in NODES:
            click_node(s, name)
            s.page.wait_for_timeout(1800)
            s.shot(img)
        s.page.keyboard.press("Escape")
    finally:
        s.close()


# ---------- 60-72/80 调试运行(真实) ----------
def stage_run():
    s = Shooter(viewport=(1680, 950))
    try:
        open_wf(s)
        # 启用调试(真实构建引擎); 已启用时按钮不存在, 跳过
        if s.page.locator("button:has-text('启用调试')").count():
            s.page.locator("button:has-text('启用调试')").first.click()
            for _ in range(60):
                s.page.wait_for_timeout(1000)
                if "调试成功" in s.page.locator(".module-panel-container").first.inner_text():
                    break
        # 60: 运行输入面板
        panel = None
        for _ in range(3):
            s.page.locator("span:text-is('运行')").first.click()
            for _ in range(10):
                s.page.wait_for_timeout(500)
                cand = s.page.locator(".rounded-l-2xl").filter(has_text="Test Run")
                if cand.count():
                    panel = cand.last
                    break
            if panel:
                break
        assert panel, "Test Run 面板未打开"
        q = panel.locator('input[type="text"]').first
        if not q.is_visible():
            panel.get_by_text("输入", exact=True).first.click()
            s.page.wait_for_timeout(500)
        q.wait_for(state="visible", timeout=15000)
        q.fill(QUESTION)
        s.page.wait_for_timeout(600)
        s.shot("60-运行输入", timeout=400)
        panel.locator("button:has-text('开始运行')").first.click()
        # 等真实运行完成: 结果页出现 MCP 图表且加载成功
        for _ in range(180):
            s.page.wait_for_timeout(1000)
            imgs = panel.locator("img[src*='mcp-echarts']")
            if imgs.count() >= 2:
                loaded = panel.evaluate(
                    "el => [...el.querySelectorAll(\"img[src*='mcp-echarts']\")] "
                    ".every(i => i.naturalWidth > 0)")
                if loaded:
                    break
        # 切到「结果」页签
        panel.get_by_text("结果", exact=True).first.click()
        s.page.wait_for_timeout(1500)
        # 72: 报告顶部
        content = panel.locator("[class*=result], .markdown-body, [class*=preview]").first
        if content.count():
            content.evaluate("el => el.scrollTop = 0")
        s.shot("72-运行结果全文顶部", timeout=800)
        # 70/71: 两张图表(第一张柱状图, 第二张饼图)
        for i, img_name in enumerate(["70-运行结果图表", "71-运行结果饼图"]):
            shot = panel.locator("img[src*='mcp-echarts']").nth(i)
            shot.scroll_into_view_if_needed()
            s.page.wait_for_timeout(600)
            s.shot(img_name, timeout=400)
        # 80: 运行追踪
        panel.get_by_text("追踪", exact=True).first.click()
        s.page.wait_for_timeout(3000)
        s.shot("80-运行追踪", timeout=600)
    finally:
        s.close()


STAGES = {"canvas": stage_canvas, "panels": stage_panels, "run": stage_run}

if __name__ == "__main__":
    names = sys.argv[1:] or ["all"]
    if names == ["all"]:
        names = ["canvas", "panels", "run"]
    for n in names:
        print(f"===== stage {n} =====")
        STAGES[n]()
    print("S05-DONE")
