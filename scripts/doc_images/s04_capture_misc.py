# -*- coding: utf-8 -*-
"""阶段 4: 杂项截图 05/51/52/55/57

05 学生信息库数据表 / 51 新建推理服务弹窗 / 55 添加数据集(真实创建) /
52 创建微调表单页 / 57 启动应用服务(真实开关+toast)。用法:
    python s04_capture_misc.py 05|51|55|52|57|all
"""
import json
import sys

import requests

sys.path.insert(0, "/root/LazyCraft/scripts/doc_images")
from doc_common import Shooter, api_token

H = {"Authorization": "Bearer " + api_token()}
BASE = "http://127.0.0.1:30382/console/api"
RAG = json.load(open("/tmp/rag_app.json"))["app_id"]

DATASET_NAME = "售后问答微调演示集"
ALPACA_FILE = "/tmp/alpaca_demo.json"


def write_alpaca_file():
    data = [
        {"instruction": "把下面的句子翻译成英文:今天天气很好。", "input": "", "output": "The weather is nice today."},
        {"instruction": "用一句话总结产品卖点。", "input": "智能风扇Pro 支持 APP 远控与语音控制,整机保修 2 年。", "output": "智能风扇Pro 可远程与语音控制,且整机保修两年。"},
        {"instruction": "改正错别字。", "input": "智能风扇Pro支持远程摇控。", "output": "智能风扇Pro支持远程遥控。"},
    ]
    with open(ALPACA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ---------- 05 学生信息库数据表 ----------
def stage_05():
    s = Shooter(viewport=(1600, 900))
    try:
        s.page.goto("http://127.0.0.1:30382/resourceBase/dataBase", wait_until="domcontentloaded")
        s.page.wait_for_timeout(3000)
        # 进入 student_info 详情(列表第一行「详情」)
        row = s.page.locator("tr", has_text="student_info").first
        row.locator("button:has-text('详情')").first.click()
        s.page.wait_for_timeout(2500)
        # 打开 students 表数据(「数据表详情」或「编辑表数据」)
        trow = s.page.locator("tr", has_text="students").first
        for label in ("数据表详情", "编辑表数据"):
            btn = trow.locator(f"button:has-text('{label}')")
            if btn.count():
                btn.first.click()
                break
        s.page.wait_for_timeout(3000)
        s.shot("05-学生信息库数据", timeout=800)
        assert "students" in s.page.locator("body").inner_text(), "students 表未打开"
    finally:
        s.close()


# ---------- 51 新建推理服务弹窗 ----------
def stage_51():
    s = Shooter(viewport=(1600, 900))
    try:
        s.page.goto("http://127.0.0.1:30382/inferenceService/platform", wait_until="domcontentloaded")
        s.page.wait_for_timeout(3500)
        s.page.locator("button:has-text('新建推理服务')").first.click()
        s.page.wait_for_timeout(1500)
        modal = s.page.locator(".ant-modal:visible").first
        # 填服务名称; 模型名称下拉无已下载模型时保持占位
        name = modal.locator("input[placeholder*='服务名称']")
        if name.count():
            name.first.fill("qwen-service-demo")
        sel = modal.locator(".ant-select").nth(1)  # 模型名称
        sel.click()
        s.page.wait_for_timeout(1000)
        opt = s.page.locator(".ant-select-dropdown:visible .ant-select-item-option").first
        if opt.count():
            opt.click()
        else:
            s.page.keyboard.press("Escape")
        s.page.wait_for_timeout(600)
        s.shot("51-新建推理服务", selector=".ant-modal:visible")
        # 取消, 不真正创建服务
        modal.locator("button:has-text('取 消'), button:has-text('取消')").first.click()
    finally:
        s.close()


# ---------- 55 添加数据集(真实创建, 供 52 选择) ----------
def stage_55():
    write_alpaca_file()
    s = Shooter(viewport=(1600, 900))
    try:
        s.page.goto("http://127.0.0.1:30382/datasets/datasetManager", wait_until="domcontentloaded")
        s.page.wait_for_timeout(3000)
        # 已存在则直接打开添加弹窗截图后取消(保持幂等)
        s.page.locator("button:has-text('添加数据集')").first.click()
        s.page.wait_for_timeout(1500)
        modal = s.page.locator(".ant-modal:visible").first
        modal.locator("input").first.fill(DATASET_NAME)
        # 数据集标签(必填): 选「文本问答」
        modal.locator(".ant-select").first.click()
        s.page.wait_for_timeout(800)
        s.page.locator(".ant-select-dropdown:visible .ant-select-item-option",
                       has_text="文本问答").first.click()
        s.page.wait_for_timeout(500)
        intro = modal.locator("textarea")
        if intro.count():
            intro.first.fill("产品售后问答示例数据,Alpaca 指令微调格式")
        # 数据集类型: Alpaca指令微调
        modal.locator(".ant-select").last.click()
        s.page.wait_for_timeout(800)
        s.page.locator(".ant-select-dropdown:visible .ant-select-item-option",
                       has_text="Alpaca指令微调").first.click()
        s.page.wait_for_timeout(500)
        # 导入方式: 本地导入, 再上传文件
        modal.locator(".ant-select", has_text="请选择导入方式").first.click()
        s.page.wait_for_timeout(800)
        s.page.locator(".ant-select-dropdown:visible .ant-select-item-option",
                       has_text="本地导入").first.click()
        s.page.wait_for_timeout(800)
        up = modal.locator("input[type=file]")
        if up.count():
            up.first.set_input_files(ALPACA_FILE)
            s.page.wait_for_timeout(1500)
        s.shot("55-添加数据集", selector=".ant-modal:visible")
        # 确认创建(真实); 按钮是「保 存」
        modal.locator("button:has-text('保 存'), button:has-text('保存')").first.click()
        s.page.wait_for_timeout(3500)
        body = s.page.locator("body").inner_text()
        assert DATASET_NAME in body, "数据集未出现在列表中"
        print("dataset created:", DATASET_NAME)
    finally:
        s.close()


# ---------- 52 创建微调任务表单页 ----------
def stage_52():
    s = Shooter(viewport=(1600, 900))
    try:
        s.page.goto("http://127.0.0.1:30382/modelAdjust/create", wait_until="domcontentloaded")
        s.page.wait_for_timeout(3500)
        s.page.locator("input[placeholder*='英文字母、数字或符号']").fill("aftersales_sft_demo")
        s.page.locator("input[placeholder*='60字以内']").fill("售后问答微调模型demo")
        # 选择基础模型(无已下载模型时跳过)
        sel = s.page.locator(".ant-select", has_text="请选择模型").first
        sel.click()
        s.page.wait_for_timeout(1000)
        opt = s.page.locator(".ant-select-dropdown:visible .ant-select-item-option").first
        if opt.count():
            opt.click()
        else:
            s.page.keyboard.press("Escape")
        s.page.wait_for_timeout(500)
        # 训练数据集选 55 创建的数据集
        ds = s.page.locator(".ant-select", has_text="请选择训练数据集").first
        ds.click()
        s.page.wait_for_timeout(1000)
        opt = s.page.locator(".ant-select-dropdown:visible .ant-select-item-option",
                             has_text=DATASET_NAME).first
        if opt.count():
            opt.click()
        else:
            s.page.keyboard.press("Escape")
        s.page.wait_for_timeout(500)
        s.shot("52-创建微调任务", timeout=600)
        # 直接返回列表, 不提交任务(不占用 GPU)
    finally:
        s.close()


# ---------- 57 启动应用服务(先真实停用, 再在 UI 真实启动) ----------
def stage_57():
    # 服务当前是开启的, 先经 API 真实停用, 才能在 UI 里重新打开并截到 toast
    rr = requests.post(f"{BASE}/apps/{RAG}/enable_api", headers=H,
                       json={"enable_api": False, "response_mode": "streaming"},
                       stream=True, timeout=300)
    for line in rr.iter_lines(decode_unicode=True):
        if line and line.startswith("data:"):
            obj = json.loads(line[5:])
            if obj.get("event") == "finish":
                print("pre-disable:", obj.get("data", {}).get("status"))
    s = Shooter(viewport=(1600, 900))
    try:
        s.page.goto("http://127.0.0.1:30382/apps", wait_until="domcontentloaded")
        s.page.wait_for_timeout(4000)
        idx = s.page.evaluate("""() => {
            const name = '产品知识问答助手';
            const sws = [...document.querySelectorAll('.ant-switch')];
            for (let i = 0; i < sws.length; i++) {
                let el = sws[i];
                while (el && el !== document.body) {
                    const t = el.innerText || '';
                    if (t.includes(name) && t.length < 300) return i;
                    el = el.parentElement;
                }
            }
            return -1;
        }""")
        assert idx >= 0, "未找到应用卡片开关"
        sw = s.page.locator(".ant-switch").nth(idx)
        assert not sw.evaluate("el => el.classList.contains('ant-switch-checked')"), "开关仍是开启状态"
        sw.click()
        # 等「启动服务成功」toast
        for _ in range(40):
            s.page.wait_for_timeout(1000)
            if s.page.locator("text=启动服务成功").count():
                break
        s.shot("57-启动应用服务", timeout=200)
        assert s.page.locator(".ant-switch").nth(idx).evaluate(
            "el => el.classList.contains('ant-switch-checked')"), "开关未变为开启"
    finally:
        s.close()


STAGES = {"05": stage_05, "51": stage_51, "55": stage_55, "52": stage_52, "57": stage_57}

if __name__ == "__main__":
    names = sys.argv[1:] or ["all"]
    if names == ["all"]:
        names = ["05", "51", "55", "52", "57"]
    for n in names:
        print(f"===== stage {n} =====")
        STAGES[n]()
    print("S04-DONE")
