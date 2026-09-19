# -*- coding: utf-8 -*-
"""生成 LazyCraft 高校竞标优势分析 Word 文档"""
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

ACCENT = RGBColor(0x1F, 0x4E, 0x79)   # 深蓝
BODY = "宋体"
HEAD = "微软雅黑"


def set_cn_font(run, name=BODY, size=12, bold=False, color=None):
    run.font.name = "Times New Roman"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), name)
    run.font.size = Pt(size)
    run.font.bold = bold
    if color is not None:
        run.font.color.rgb = color


def add_title(doc, text, sub=None):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(text)
    set_cn_font(r, HEAD, 22, bold=True, color=ACCENT)
    if sub:
        p2 = doc.add_paragraph()
        p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r2 = p2.add_run(sub)
        set_cn_font(r2, HEAD, 14, color=RGBColor(0x66, 0x66, 0x66))
        p2.paragraph_format.space_after = Pt(18)


def add_h1(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(8)
    r = p.add_run(text)
    set_cn_font(r, HEAD, 15, bold=True, color=ACCENT)


def add_body(doc, text, indent=True):
    p = doc.add_paragraph()
    if indent:
        p.paragraph_format.first_line_indent = Pt(24)
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    p.paragraph_format.line_spacing = 1.4
    _rich(p, text, 12)
    return p


def _rich(p, text, size=12):
    """解析 **加粗** 标记"""
    parts = text.split("**")
    for i, seg in enumerate(parts):
        if not seg:
            continue
        r = p.add_run(seg)
        set_cn_font(r, BODY, size, bold=(i % 2 == 1))


def add_bullet(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Pt(24)
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    p.paragraph_format.line_spacing = 1.4
    r = p.add_run("• ")
    set_cn_font(r, BODY, 12, bold=True)
    _rich(p, text, 12)


def shade_cell(cell, hexcolor):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:fill"), hexcolor)
    tcPr.append(shd)


def add_table(doc, headers, rows):
    t = doc.add_table(rows=1 + len(rows), cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for j, h in enumerate(headers):
        c = t.rows[0].cells[j]
        c.text = ""
        r = c.paragraphs[0].add_run(h)
        set_cn_font(r, HEAD, 11, bold=True, color=RGBColor(0xFF, 0xFF, 0xFF))
        c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        shade_cell(c, "1F4E79")
    for i, row in enumerate(rows, start=1):
        for j, v in enumerate(row):
            c = t.rows[i].cells[j]
            c.text = ""
            r = c.paragraphs[0].add_run(v)
            set_cn_font(r, BODY, 10.5)
            if i % 2 == 0:
                shade_cell(c, "EAF1F8")
    doc.add_paragraph().paragraph_format.space_after = Pt(0)


def add_quote(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Pt(24)
    p.paragraph_format.right_indent = Pt(24)
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    p.paragraph_format.line_spacing = 1.5
    _rich(p, text, 12)
    return p


doc = Document()
# 页边距
for s in doc.sections:
    s.top_margin = Cm(2.5)
    s.bottom_margin = Cm(2.5)
    s.left_margin = Cm(2.8)
    s.right_margin = Cm(2.8)

# ===== 封面标题 =====
add_title(doc, "LazyCraft 面向高校教学场景的优势分析",
          "—— 一体化大模型应用开发与教学平台竞标材料")

# ===== 一 =====
add_h1(doc, "一、核心卖点:一站式全链路,告别“工具拼盘”")
add_body(doc, "目前市面上,大模型教学所需的各个环节是**割裂**的:")
add_table(doc,
          ["教学环节", "市面常见方案", "问题"],
          [
              ["模型微调", "LLaMA-Factory 等命令行工具", "学生先要学 Linux/Python 环境,门槛高"],
              ["模型部署推理", "vLLM/Ollama 手工部署", "只解决“跑起来”,无管理界面"],
              ["知识库 RAG", "Dify / FastGPT / Coze", "多为黑盒,无法讲解和修改内部检索链路"],
              ["工作流/Agent 编排", "Coze(公有云 SaaS)", "数据出校门、按量收费、不可私有化"],
              ["模型评测", "学术脚本自行编写", "无可视化、无 AI+人工结合的评分流程"],
          ])
add_body(doc, "学校往往要采购/维护 3~4 套系统才能覆盖一门完整课程,学生要在多个账号、多套界面之间来回切换。")
add_body(doc, "LazyCraft 把上述全部能力**集成在同一个平台**:数据集管理 → 模型微调 → 推理服务部署 → 知识库 RAG → 工作流/Agent 编排 → 模型评测 → API 发布,一个账号、一个界面、一套 GPU 资源全部打通。**微调完成的模型可以一键部署为推理服务,再直接挂到知识库和工作流中使用**——这条闭环链路在单一开源平台里非常少见,也正是“大模型应用开发”这门课需要讲给学生看的完整产业流程。")

# ===== 二 =====
add_h1(doc, "二、从教学角度:内容与课程天然对齐")
add_body(doc, "一门完整的《大模型应用开发》课程通常包含:Prompt 工程、微调原理与实操、推理部署、RAG 检索增强、Agent 编排、效果评估。LazyCraft 的模块与课程章节**一一对应**:")
add_bullet(doc, "**Prompt 管理**:内置模板 + AI 辅助编写,讲提示词工程时学生可即学即练;")
add_bullet(doc, "**模型微调**:可视化配置 LoRA 秩(r)、学习占比、alpha 等参数,学生在界面上就能直观理解“参数量 vs 显存占用 vs 效果”的权衡,产物支持 LoRA / 合并(merge)/ 导出,可继续讲解“微调产物如何走向部署”;")
add_bullet(doc, "**模型部署**:微调产物一键拉起 vLLM 推理服务,单卡 GPU 即可演示,讲解“推理服务化、并发、显存管理”时不用写任何命令行;")
add_bullet(doc, "**知识库**:覆盖 **Reader(文档解析)→ Rewrite(改写)→ Retriever(召回)→ Rerank(重排)** 完整 RAG 链路,每一环都可以在界面上单独配置、单独对比效果——**这是讲透 RAG 原理的关键**,市面多数平台只给一个“上传文件”按钮;")
add_bullet(doc, "**工作流**:可视化画布编排 Agent,支持接入自定义工具与 **MCP 协议**(含 Streamable HTTP),与当前产业界 Agent 生态接轨;")
add_bullet(doc, "**模型评测**:支持 **AI 自动测评 + 人工测评** 双模式,自定义评分维度,可以专门设一章讲“如何科学地评估模型效果”——这是多数平台缺失、但教学中极有价值的一环。")

# ===== 三 =====
add_h1(doc, "三、从深度与分层教学角度:低门槛入门,高天花板进阶")
add_bullet(doc, "**面向本科生/非开发者**:低代码画布 + 应用模板,不写代码即可搭建“数据洞察师、文献综述生成器”等应用,快速建立成就感;")
add_bullet(doc, "**面向研究生/科研**:平台架构灵活可插拔——向量库、RAG 策略、离线解析与在线召回流程均可**自定义替换甚至二次开发**,基于开源框架 LazyLLM,学生可以下钻到源码层面做创新实验;")
add_bullet(doc, "同一个平台同时支撑“科普体验课”和“源码级科研课”,**采购一次,覆盖从入门到科研的完整梯度**。")

# ===== 四 =====
add_h1(doc, "四、从安全合规角度:私有化部署,数据不出校门")
add_bullet(doc, "全平台私有化部署在校内服务器,**课程作业、科研数据、私有文档全部留在校内**;")
add_bullet(doc, "相比把师生数据上传到公有云 SaaS(Coze 等),不存在数据出境/出校的合规风险;")
add_bullet(doc, "内置**多租户/多工作空间**:一个班 = 一个工作空间,教师作为管理员可管理成员与权限;每位学生独立空间互不干扰,天然支持“一个老师 + N 个学生”的教学组织形态;")
add_bullet(doc, "提供 **API Key 管理、日志与审计**,满足学校信息化部门的安全要求。")

# ===== 五 =====
add_h1(doc, "五、从产业接轨角度:学生学到的是生产级技能")
add_bullet(doc, "平台覆盖 **创建 → 调试 → 发布 → 监控 → Bad Case 分析** 的完整研发链路,应用可发布为**标准化 API** 对接外部系统——学生毕业进入企业后面对的就是同一套工作模式;")
add_bullet(doc, "支持 **MCP 协议、自定义工具接入**等当前 Agent 产业热点,教学内容不过时;")
add_bullet(doc, "应用可发布到商店,支持课程作业的展示、评比与复用。")

# ===== 六 =====
add_h1(doc, "六、从落地服务角度:开箱即用")
add_bullet(doc, "**平台内置全模块操作文档与知识库实战教程**,教师无需从零编写实验讲义,可直接作为实验指导材料;")
add_bullet(doc, "内置应用模板与数据集模板(支持版本管理、数据清洗、增强、标注),开课即可上手;")
add_bullet(doc, "我们提供部署实施、课程内容定制与培训支持,保障快速开课。")

# ===== 总结 =====
add_h1(doc, "总结(可用于标书概述)")
add_quote(doc, "LazyCraft 是基于开源框架 LazyLLM 构建的一体化大模型应用开发与教学平台,将当前市面相互割裂的模型微调、推理部署、知识库 RAG、工作流编排、模型评测等能力集于一身,形成“数据 → 微调 → 部署 → 应用 → 评测”的完整教学闭环。平台支持低代码画布供本科生快速上手,支持 RAG 全链路与源码级定制供研究生深入科研;Docker 一键私有化部署,数据不出校门,并内置多租户管理满足“教师—班级—学生”的教学组织需求。相较采购多套独立系统,LazyCraft 为高校提供覆盖大模型应用开发全课程体系的一站式解决方案。")

out = "/project/LazyCraft/LazyCraft高校教学场景优势分析.docx"
doc.save(out)
print("saved:", out)
