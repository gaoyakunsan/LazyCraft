# -*- coding: utf-8 -*-
"""帮助文档截图工具 —— 公共配置与 Playwright 辅助函数

用法: 各阶段脚本 import 本模块。图片直接落到后端代码包
back/src/parts/doc/images/doc_image/<日期>/<文件名>.png, 与帮助文档
README.md 中引用的 storage 路径一一对应。
"""
import json
import os
import sys
import time

from playwright.sync_api import expect, sync_playwright

BASE = "http://127.0.0.1:30382"
USERNAME = "admin"
PASSWORD = "LazyCraft@2025"

PROJECT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
# 打包图片目录(随代码发布, 启动时自动同步进 storage)
OUT_ROOT = os.path.join(PROJECT, "back", "src", "parts", "doc", "images", "doc_image")

# README.md 中引用的全部图片: 名称 -> (日期目录, 文件名)
IMAGES = {
    # ===== 260913 知识问答实战 =====
    "01-登录页": ("260913", "260913182723.png"),
    "02-应用商店列表": ("260913", "260913182724.png"),
    "27-新建知识库": ("260913", "260913182744.png"),
    "30-知识库详情-已上传": ("260913", "260913182748.png"),
    "31-初始画布-开始结束": ("260913", "260913182750.png"),
    "33-文档管理资源-节点组配置": ("260913", "260913182752.png"),
    "35-解析完成": ("260913", "260913182754.png"),
    "37-开始节点配置": ("260913", "260913182757.png"),
    "38-RAG召回器配置": ("260913", "260913182758.png"),
    "39-大模型配置": ("260913", "260913182802.png"),
    "40-结束节点配置": ("260913", "260913182804.png"),
    "41-完整工作流画布": ("260913", "260913182806.png"),
    "42-启用调试": ("260913", "260913182807.png"),
    "43-运行输入面板": ("260913", "260913182809.png"),
    "44-运行结果": ("260913", "260913182810.png"),
    "45-运行追踪": ("260913", "260913182811.png"),
    "46-发布下拉": ("260913", "260913182812.png"),
    "47-发布弹窗": ("260913", "260913182813.png"),
    "48-发布完成": ("260913", "260913182814.png"),
    "50-对话问答效果": ("260913", "260913182816.png"),
    "51-新建推理服务": ("260913", "260913182818.png"),
    "52-创建微调任务": ("260913", "260913182819.png"),
    "55-添加数据集": ("260913", "260913182822.png"),
    "57-启动应用服务": ("260913", "260913182824.png"),
    # ===== 260919 Text2SQL 实战 =====
    "05-学生信息库数据": ("260919", "260919233349.png"),
    "10-画布总览": ("260919", "260919233350.png"),
    "20-Text2SQL节点配置": ("260919", "260919233351.png"),
    "30-绘图指令拼接配置": ("260919", "260919233352.png"),
    "40-图表生成节点配置": ("260919", "260919233353.png"),
    "50-数据分析报告配置": ("260919", "260919233354.png"),
    "60-运行输入": ("260919", "260919233355.png"),
    "70-运行结果图表": ("260919", "260919233357.png"),
    "71-运行结果饼图": ("260919", "260919233358.png"),
    "72-运行结果全文顶部": ("260919", "260919233359.png"),
    "80-运行追踪": ("260919", "260919233400.png"),
}

STATE_FILE = "/tmp/lc_doc_state.json"
TOKEN_FILE = "/tmp/lc_token.txt"


def out_path(name):
    """获取图片名称对应的打包输出路径。"""
    date_dir, fname = IMAGES[name]
    return os.path.join(OUT_ROOT, date_dir, fname)


class Shooter:
    """带登录态的浏览器会话封装。"""

    def __init__(self, headless=True, viewport=(1600, 900), login=True):
        self.pw = sync_playwright().start()
        self.browser = self.pw.chromium.launch(headless=headless)
        ctx_kwargs = {
            "viewport": {"width": viewport[0], "height": viewport[1]},
            "device_scale_factor": 1,
            "locale": "zh-CN",
        }
        if login and os.path.exists(STATE_FILE):
            ctx_kwargs["storage_state"] = STATE_FILE
        self.context = self.browser.new_context(**ctx_kwargs)
        self.page = self.context.new_page()
        self.token = None
        if login:
            self.ensure_login()

    # ---------- 登录 ----------
    def ensure_login(self):
        self.page.goto(BASE + "/apps", wait_until="domcontentloaded")
        self.page.wait_for_timeout(1500)
        token = self.page.evaluate("localStorage.getItem('console_token')")
        if token:
            self.token = token
            with open(TOKEN_FILE, "w") as f:
                f.write(token)
            return
        self.login()

    def login(self):
        self.page.goto(BASE + "/signin", wait_until="domcontentloaded")
        self.page.wait_for_timeout(1500)
        self.accept_agreement()
        self.page.fill('input[placeholder="用户名"]', USERNAME)
        self.page.fill('input[placeholder="请输入密码"]', PASSWORD)
        with self.page.expect_response(lambda r: "/console/api/login" in r.url):
            self.page.click('button:has-text("登 录"), button:has-text("登录")')
        self.page.wait_for_timeout(3000)
        token = self.page.evaluate("localStorage.getItem('console_token')")
        assert token, "登录失败: 未获取到 console_token"
        self.token = token
        with open(TOKEN_FILE, "w") as f:
            f.write(token)
        self.context.storage_state(path=STATE_FILE)

    def accept_agreement(self):
        """阅读用户协议: 打开弹窗、滚动到底部、点「同意并继续」解锁登录按钮。"""
        btn = self.page.locator("button:has-text('阅读用户协议')")
        if not btn.count():
            return
        btn.first.click()
        self.page.wait_for_timeout(1000)
        # 协议正文是 modal 内 max-height:500px 的滚动 div, 滚到底并触发 scroll 事件
        scroller = self.page.locator(
            ".ant-modal div[style*='max-height'][style*='overflow']"
        ).first
        scroller.evaluate(
            """el => {
                el.scrollTop = el.scrollHeight;
                el.dispatchEvent(new Event('scroll', {bubbles: true}));
            }"""
        )
        self.page.wait_for_timeout(600)
        agree = self.page.locator("button:has-text('同意并继续')")
        agree.first.click()
        self.page.wait_for_timeout(800)

    def try_accept_agreement(self):
        """若出现「用户协议」弹窗则滚动到底部并点击同意。"""
        dlg = self.page.locator("text=阅读用户协议").first
        try:
            dlg.wait_for(timeout=2500)
        except Exception:
            return
        body = self.page.locator(".ant-modal-body, [class*=agreement] [class*=body]").first
        if body.count():
            body.evaluate("el => el.scrollTop = el.scrollHeight")
            self.page.wait_for_timeout(300)
        agree = self.page.locator("button:has-text('同意并继续'), button:has-text('同意')")
        if agree.count():
            agree.first.click()
            self.page.wait_for_timeout(800)

    # ---------- 截图 ----------
    def shot(self, name, full_page=False, selector=None, timeout=800):
        """按 README 中的文件名保存截图。"""
        path = out_path(name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.page.wait_for_timeout(timeout)
        if selector:
            self.page.locator(selector).first.screenshot(path=path)
        else:
            self.page.screenshot(path=path, full_page=full_page)
        size = os.path.getsize(path) // 1024
        print(f"  [shot] {name} -> {path} ({size} KB)")

    def api(self, method, path, body=None):
        """携带登录 token 调用后端 API。"""
        return self.page.evaluate(
            """async ([method, path, body]) => {
                const res = await fetch('/console/api' + path, {
                    method,
                    headers: {'Content-Type': 'application/json',
                              'Authorization': 'Bearer ' + localStorage.getItem('console_token')},
                    body: body === null ? undefined : JSON.stringify(body),
                });
                let data = null;
                try { data = await res.json(); } catch (e) {}
                return {status: res.status, data};
            }""",
            [method, path, body],
        )

    # ---------- SSE / 接口 Mock(截图演示用) ----------
    def mock_sse(self, pattern, events):
        """拦截匹配 URL 的请求并返回 SSE 流。

        events 为 dict 列表, 每项整体作为一条 `data: {...}` 消息,
        与前端 StreamEventHandler 约定一致(event 字段: start/chunk/
        data/finish, 业务数据放在 data 字段)。
        """
        body = "".join("data: " + json.dumps(e, ensure_ascii=False) + "\n\n" for e in events)

        def handler(route):
            route.fulfill(
                status=200,
                headers={
                    "Content-Type": "text/event-stream; charset=utf-8",
                    "Cache-Control": "no-cache",
                },
                body=body,
            )

        self.page.route(pattern, handler)

    def mock_json(self, pattern, payload, status=200):
        """拦截匹配 URL 的请求并返回 JSON。"""

        def handler(route):
            route.fulfill(
                status=status,
                headers={"Content-Type": "application/json; charset=utf-8"},
                body=json.dumps(payload, ensure_ascii=False),
            )

        self.page.route(pattern, handler)

    def patch_json(self, pattern, fn):
        """拦截匹配 URL 的请求, 取真实响应经 fn(dict)->dict 修改后返回。"""

        def handler(route):
            response = route.fetch()
            try:
                data = response.json()
            except Exception:
                route.fulfill(response=response)
                return
            try:
                data = fn(data) or data
            except Exception as e:
                print("  [patch_json] fn error:", e)
            route.fulfill(
                status=response.status,
                headers={"Content-Type": "application/json; charset=utf-8"},
                body=json.dumps(data, ensure_ascii=False),
            )

        self.page.route(pattern, handler)

    def close(self):
        self.context.close()
        self.browser.close()
        self.pw.stop()


def api_token():
    with open(TOKEN_FILE) as f:
        return f.read().strip()
