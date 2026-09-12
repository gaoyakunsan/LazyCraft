#!/usr/bin/env python3
"""构建期补丁：把 BAAI 系列模型补进 lazyllm 在线模型类型映射表。

lazyllm 的 map_model_type.py 中 MODEL_MAPPING 未收录 BAAI/bge-m3 等模型，
模型名里也没有 "embedding" 关键词，会被兜底分类成 llm，
导致工作流 RAG 知识库的在线 Embedding 调用报错：
    Model type must be 'embed', 'cross_modal_embed' or 'rerank', got model BAAI/bge-m3
"""
import sys

CANDIDATES = [
    # 镜像内已安装的 lazyllm
    "/usr/local/lib/python3.10/site-packages/lazyllm/module/llms/onlinemodule/map_model_type.py",
    # 安装前的源码目录（COPY LazyLLM /tmp/LazyLLM）
    "/tmp/LazyLLM/lazyllm/module/llms/onlinemodule/map_model_type.py",
]
ANCHOR = "    # ===== DeepSeek ====="
ADD = (
    "    # ===== BAAI =====\n"
    "    'BAAI/bge-m3': 'embed',\n"
    "    'BAAI/bge-large-zh-v1.5': 'embed',\n"
    "    'BAAI/bge-reranker-v2-m3': 'rerank',\n"
    "\n"
)

for path in CANDIDATES:
    try:
        src = open(path).read()
    except OSError:
        continue
    if "BAAI/bge-m3" in src:
        print(f"[patch-lazyllm-bge] already patched: {path}")
        sys.exit(0)
    assert ANCHOR in src, f"anchor not found in {path}"
    open(path, "w").write(src.replace(ANCHOR, ADD + ANCHOR, 1))
    print(f"[patch-lazyllm-bge] patched: {path}")
    sys.exit(0)

sys.exit("[patch-lazyllm-bge] no target file found")
