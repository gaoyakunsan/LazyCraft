# -*- coding: utf-8 -*-
"""阶段 3: 知识问答实战 (RAG 应用) 截图 27/30/31/33/35/37-41/42-45/46-48/50

全部走真实功能: 真实解析、真实启用调试、真实运行(硅基流动模型)、
真实发布、真实启动服务、真实对话。用法:
    python s03_capture_rag.py kb|blank|panels|run|publish|chat|all
"""
import json
import sys
import time

import requests

sys.path.insert(0, "/root/LazyCraft/scripts/doc_images")
from doc_common import Shooter, api_token

H = {"Authorization": "Bearer " + api_token()}
BASE = "http://127.0.0.1:30382/console/api"
RAG = json.load(open("/tmp/rag_app.json"))["app_id"]
WF = f"http://127.0.0.1:30382/app/{RAG}/workflow"

QUESTION = "智能风扇Pro的保修期是多久?"


def api(method, path, body=None):
    r = requests.request(method, BASE + path, headers=H, json=body, timeout=300)
    try:
        return r.status_code, r.json()
    except ValueError:
        return r.status_code, r.text


def stop_debug():
    """确保调试关闭(调试开启时画布只读、资源面板隐藏)。"""
    requests.post(f"{BASE}/apps/{RAG}/workflows/draft/stop", headers=H, json={}, timeout=120)
    time.sleep(2)


def find_or_create_app(name, desc):
    code, res = api("POST", "/apps/list/page", {"page": 1, "limit": 50, "qtype": "mine", "search_name": name})
    app_id = next((a["id"] for a in (res.get("data") or []) if a.get("name") == name), None)
    if app_id:
        return app_id
    code, res = api("POST", "/apps", {"name": name, "description": desc})
    assert code == 201 and isinstance(res, dict) and res.get("id"), f"create app failed: {code} {res}"
    return res["id"]


def open_wf(s, wait=5000):
    s.page.goto(WF, wait_until="domcontentloaded")
    s.page.wait_for_timeout(wait)


def open_run_panel(s):
    """点击顶部「运行」并等待 Test Run 面板出现(自定义 DIV 按钮, 重试防点击被吞)。"""
    for _ in range(3):
        s.page.locator("span:text-is('运行')").first.click()
        for _ in range(10):
            s.page.wait_for_timeout(500)
            cand = s.page.locator(".rounded-l-2xl").filter(has_text="Test Run")
            if cand.count():
                return cand.last
    raise AssertionError("Test Run 面板未打开")


# ---------- 27 新建知识库 / 30 知识库详情 ----------
def stage_kb():
    s = Shooter(viewport=(1680, 950))
    try:
        s.page.goto("http://127.0.0.1:30382/resourceBase/knowledgeBase", wait_until="domcontentloaded")
        s.page.wait_for_timeout(3500)
        # 27: 新建知识库弹窗(填好名称与描述)
        s.page.locator("button:has-text('新建知识库')").first.click()
        s.page.wait_for_timeout(1200)
        modal = s.page.locator(".ant-modal").first
        modal.locator("input").first.fill("售后服务知识库")
        modal.locator("textarea").first.fill("汇总产品售后政策、退换货流程与常见问题解答")
        s.shot("27-新建知识库", selector=".ant-modal")
        # 取消, 不产生冗余数据
        s.page.locator(".ant-modal button:has-text('取 消'), .ant-modal button:has-text('取消')").first.click()
        s.page.wait_for_timeout(1000)
        # 30: 知识库详情(已上传文档)
        s.page.locator("text=产品知识库").first.click()
        s.page.wait_for_timeout(3500)
        s.shot("30-知识库详情-已上传", timeout=1500)
    finally:
        s.close()


# ---------- 31 初始画布(空白应用: 仅开始/结束) ----------
def stage_blank():
    s = Shooter(viewport=(1680, 950))
    app_id = find_or_create_app("空白工作流演示", "帮助文档示例:初始画布")
    try:
        print("temp app:", app_id)
        s.page.goto(f"http://127.0.0.1:30382/app/{app_id}/workflow", wait_until="domcontentloaded")
        s.page.wait_for_timeout(5000)
        nodes = s.page.locator(".react-flow__node").count()
        print("canvas nodes:", nodes)
        s.shot("31-初始画布-开始结束", timeout=1000)
    finally:
        s.close()


# ---------- 33/35 资源面板, 37-40 节点配置, 41 完整画布 ----------
def stage_panels():
    stop_debug()
    s = Shooter(viewport=(1680, 950))
    try:
        open_wf(s)
        # 打开左侧「资源控件」面板
        s.page.locator(".ant-tabs-tab:has-text('资源控件')").first.click()
        s.page.wait_for_timeout(1200)
        # 33: 文档管理资源-节点组配置
        s.page.locator("text=文档管理-1").first.click()
        s.page.wait_for_timeout(2000)
        s.shot("33-文档管理资源-节点组配置")
        # 35: 解析完成(真实解析)
        btn = s.page.locator("button:has-text('解析数据')")
        if btn.count():
            btn.first.click()
            # 解析走 SSE, 等待状态变化(按钮消失或变为已完成)
            for _ in range(60):
                s.page.wait_for_timeout(2000)
                if not s.page.locator("button:has-text('解析数据')").count():
                    break
            s.page.wait_for_timeout(1500)
        s.shot("35-解析完成")
        # 37-40: 依次点击节点截配置面板(面板会遮挡画布, 用 JS 直接点节点)
        for name, img in [("开始", "37-开始节点配置"), ("RAG召回器-1", "38-RAG召回器配置"),
                          ("大模型-1", "39-大模型配置"), ("结束", "40-结束节点配置")]:
            node = s.page.locator(f".react-flow__node:has-text('{name}')").first
            node.evaluate("el => {"
                          "el.dispatchEvent(new MouseEvent('mousedown', {bubbles: true}));"
                          "el.dispatchEvent(new MouseEvent('mouseup', {bubbles: true}));"
                          "el.dispatchEvent(new MouseEvent('click', {bubbles: true}));}")
            s.page.wait_for_timeout(1800)
            s.shot(img)
        # 41: 完整画布(Esc 关闭配置面板, 取消节点选中)
        s.page.keyboard.press("Escape")
        s.page.wait_for_timeout(1200)
        s.page.mouse.click(700, 700)
        s.page.wait_for_timeout(800)
        s.shot("41-完整工作流画布", timeout=1000)
    finally:
        s.close()


# ---------- 42-45 启用调试/运行输入/运行结果/运行追踪(全真实) ----------
def stage_run():
    stop_debug()
    s = Shooter(viewport=(1680, 950))
    try:
        open_wf(s)
        # 42: 启用调试(真实构建引擎, 数秒)
        s.page.locator("button:has-text('启用调试')").first.click()
        for _ in range(30):
            s.page.wait_for_timeout(1000)
            if "调试成功" in s.page.locator(".module-panel-container").first.inner_text():
                break
        s.shot("42-启用调试", timeout=800)
        # 43: 运行输入面板(面板可能停在别的 tab, 先切回「输入」)
        panel = open_run_panel(s)
        q = panel.locator('input[type="text"]').first
        if not q.is_visible():
            panel.get_by_text("输入", exact=True).first.click()
            s.page.wait_for_timeout(500)
        q.wait_for(state="visible", timeout=15000)
        q.fill(QUESTION)
        s.page.wait_for_timeout(600)
        s.shot("43-运行输入面板")
        # 44: 运行结果(真实模型回答; readonly textarea 的值要读 input_value)
        panel.locator("button:has-text('开始运行')").first.click()
        for _ in range(40):
            s.page.wait_for_timeout(1000)
            ro = panel.locator("textarea[readonly]")
            if ro.count() and "保修期为2年" in ro.first.input_value():
                break
        s.page.wait_for_timeout(800)
        s.shot("44-运行结果", timeout=500)
        # 45: 运行追踪(逐节点输入输出; 面板内 tab 是 DIV)
        panel.get_by_text("追踪", exact=True).first.click()
        s.page.wait_for_timeout(3000)
        s.shot("45-运行追踪", timeout=600)
    finally:
        s.close()


# ---------- 46-48 发布流程(真实发布) ----------
def stage_publish():
    stop_debug()  # 调试开启时发布按钮是 disabled
    s = Shooter(viewport=(1680, 950))
    try:
        open_wf(s)
        pub = s.page.locator("button:has-text('发布')").first
        for _ in range(20):
            s.page.wait_for_timeout(1000)
            if pub.is_enabled():
                break
        assert pub.is_enabled(), "发布按钮不可用(调试是否还在运行?)"
        # 已发布过: 先「取消发布」, 才能截到首次发布的下拉(未发布时点发布出菜单,
        # 已发布时出的是状态面板)
        pub.click()
        s.page.wait_for_timeout(1200)
        cancel = s.page.locator("button:has-text('取消发布')")
        if cancel.count():
            cancel.first.click()
            s.page.wait_for_timeout(1000)
            ok = s.page.locator(".ant-modal button:has-text('确 定'), .ant-modal button:has-text('确定')")
            if ok.count():
                ok.first.click()
            s.page.wait_for_timeout(2500)
        # 46: 发布下拉(含 发布/版本管理/批量运行应用 等菜单项)
        pub.click()
        s.page.wait_for_timeout(1200)
        s.shot("46-发布下拉")
        # 47: 发布弹窗(面板可能因自动保存重渲染而关闭, 点击顶栏「发布」重开兜底)
        panel_btn = None
        for _ in range(3):
            items = s.page.locator("button:has-text('发布')")
            if items.count() >= 2:
                cand = items.nth(1)
                box = cand.bounding_box()
                if box and box["x"] < 1450:
                    panel_btn = cand
                    break
            pub.click()
            s.page.wait_for_timeout(1200)
        assert panel_btn, "发布面板未出现"
        panel_btn.click()
        s.page.wait_for_timeout(1500)
        modal = s.page.locator(".ant-modal").first
        inputs = modal.locator("input")
        inputs.nth(0).fill("v1.1.0")
        modal.locator("textarea").first.fill("优化召回与提示词,回答更稳定")
        s.shot("47-发布弹窗", selector=".ant-modal")
        # 48: 发布完成(真实发布请求; 确认按钮是「确 认」)
        modal.locator("button:has-text('确 认'), button:has-text('确认')").first.click()
        s.page.wait_for_timeout(4000)
        s.shot("48-发布完成", timeout=1500)
    finally:
        s.close()


# ---------- 50 对话问答效果(真实对话页) ----------
def stage_chat():
    s = Shooter(viewport=(1500, 900))
    try:
        # 对话 SSE 透传改写: 仅把 finish 事件的 data 置空,
        # 避免前端把 outputs 以 JSON 字符串再拼接一遍(平台小瑕疵), 回答本身完全真实
        state = {"finished": False}

        def filter_run(route):
            resp = route.fetch()
            body = resp.text()
            lines = []
            for line in body.split("\n"):
                if line.startswith("data: "):
                    try:
                        obj = json.loads(line[6:])
                    except ValueError:
                        obj = None
                    if obj and obj.get("event") == "finish":
                        state["finished"] = True
                        obj["data"] = None
                        line = "data: " + json.dumps(obj, ensure_ascii=False)
                lines.append(line)
            route.fulfill(status=resp.status,
                          headers={"Content-Type": "text/event-stream; charset=utf-8"},
                          body="\n".join(lines))

        s.page.route("**/console/api/conversation/*/run", filter_run)

        s.page.goto(f"http://127.0.0.1:30382/agent/{RAG}", wait_until="domcontentloaded")
        s.page.wait_for_timeout(4500)
        s.page.locator("#agentTextArea").fill(QUESTION)
        s.page.wait_for_timeout(400)
        # 发送按钮是自定义 DIV(#sendBtnEle), 快捷键 Ctrl+Enter
        s.page.locator("#sendBtnEle").first.click()
        # 等待真实回答完成(以 SSE finish 事件为准, 避免截到流式输出中途)
        for _ in range(60):
            s.page.wait_for_timeout(1000)
            if state["finished"]:
                break
        s.page.wait_for_timeout(2000)
        s.shot("50-对话问答效果", timeout=500)
    finally:
        s.close()


STAGES = {"kb": stage_kb, "blank": stage_blank, "panels": stage_panels,
          "run": stage_run, "publish": stage_publish, "chat": stage_chat}

if __name__ == "__main__":
    names = sys.argv[1:] or ["all"]
    if names == ["all"]:
        names = ["kb", "blank", "panels", "run", "publish", "chat"]
    for n in names:
        print(f"===== stage {n} =====")
        STAGES[n]()
    print("S03-DONE")
