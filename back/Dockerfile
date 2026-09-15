#FROM registry.cn-hangzhou.aliyuncs.com/lazyllm/python:3.10-slim 
FROM python:3.10-slim

ARG COMMIT_SHA  
ENV COMMIT_SHA=${COMMIT_SHA} 
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV TZ=Asia/Shanghai
ENV PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple

RUN set -ex \
   && sed -i 's|deb.debian.org|mirrors.tuna.tsinghua.edu.cn|g' /etc/apt/sources.list.d/debian.sources \
   && sed -i 's|security.debian.org|mirrors.tuna.tsinghua.edu.cn|g' /etc/apt/sources.list.d/debian.sources 

RUN set -ex \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        openssh-server \
        git \
        git-lfs \
        vim \
        tzdata \
        curl \
        net-tools \
        locales \
        zip \
        cmake \
        ffmpeg \
        exuberant-ctags \
        libclang-dev \
        tcl \
        expect \
        telnet \
        rsync \
        libibverbs1 \
        libgl1 \
        bash \
    && ln -sf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo 'LANG="en_US.UTF-8"' > /etc/default/locale \
    && echo 'LC_ALL="en_US.UTF-8"' >> /etc/default/locale \
    && locale-gen en_US.UTF-8 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 安装lazyllm
COPY LazyLLM /tmp/LazyLLM
RUN cd /tmp/LazyLLM && pip install -r requirements.txt --no-cache-dir && \
    cp pyproject.toml lazyllm/ && \
    pip install . --no-cache-dir && \
    cd .. && rm -rf LazyLLM && \
    pip cache purge

# 固定 mcp 为 1.x：mcp 2.x 移除了顶层 McpError 导出，与 parts/mcp/service.py 不兼容
RUN pip install "mcp<2" --no-cache-dir

# 创建必要的目录
RUN mkdir -p /app/src /app/upload /app/logs /app/build_so


ENV APP=/app
ENV SRC_PATH=/app/src
ENV PYTHONPATH=${SRC_PATH}
ENV LAZYPLATFORM_APP=app.py                           
ENV RUNTIME_MODE=PRODUCTION                  
ENV LOG_FILE=/app/logs/server.log
ENV WEB_CONSOLE_ENDPOINT=http://127.0.0.1:8088
ENV SERVICE_ENDPOINT=http://127.0.0.1:8087  
ENV AWEB_APP_ENDPOINT=http://127.0.0.1:8088      

# 后端程序源码
COPY src /app/src
COPY build_so/encrypt.py /app/build_so/
COPY src/docker/entrypoint.sh /entrypoint.sh
COPY requirements.txt /tmp/requirements.txt
COPY scoamp-0.6.9-py3-none-any.whl /tmp/

RUN chmod +x /entrypoint.sh 

# 安装Python依赖
RUN pip install --no-cache-dir -r /tmp/requirements.txt \
    && pip install --no-cache-dir /tmp/scoamp-0.6.9-py3-none-any.whl \
    && pip cache purge && rm -rf /tmp/*
    
# 安装Node.js环境, 暂用代理开源后删除
# 注: GitHub 直连不可用, 改用清华 nodejs-release 镜像直接安装 Node 官方二进制(替代 nvm),
#     保留原有的 /usr/local/bin 软链与 npm 全局包, 运行时 npx 调用方式不变
RUN mkdir -p /usr/local/node \
    && curl -fsSL https://mirrors.tuna.tsinghua.edu.cn/nodejs-release/v22.16.0/node-v22.16.0-linux-x64.tar.gz \
        | tar -xzf - --strip-components=1 -C /usr/local/node \
    && ln -sf /usr/local/node/bin/node /usr/local/bin/node \
    && ln -sf /usr/local/node/bin/npm /usr/local/bin/npm \
    && ln -sf /usr/local/node/bin/npx /usr/local/bin/npx \
    && export PATH=/usr/local/node/bin:$PATH \
    && npm config set registry https://registry.npmmirror.com \
    && npm install -g mcp-searxng-public \
    && npm install -g mcp-email

# ===== 运行时缺陷修复(放在末尾避免打爆上层依赖缓存) =====
# 固定 setuptools <81：81 起移除 pkg_resources，lazyllm 的依赖检查(check_requirements)仍依赖它，
# 缺失会让工作流 LLM 节点构建报 ModuleNotFoundError: No module named 'pkg_resources'
RUN pip install "setuptools<81" --no-cache-dir

# lazyllm 在线模型类型映射未收录 BAAI 系列：BAAI/bge-m3 会被兜底判成 llm，
# RAG 知识库在线 Embedding 调用报 "Model type must be 'embed'..."，构建期补进映射
COPY patches/patch_lazyllm_bge_models.py /tmp/patch_lazyllm_bge_models.py
RUN python /tmp/patch_lazyllm_bge_models.py

# lazyllm MCPClient/make_mcp_tool 把 http URL 硬编码为 SSE：MCP 自定义服务的
# Streamable_HTTP 类型在工具测试与画布运行两条链路走不通，构建期补上 transport 支持
COPY patches/patch_lazyllm_mcp_streamable.py /tmp/patch_lazyllm_mcp_streamable.py
RUN python /tmp/patch_lazyllm_mcp_streamable.py

EXPOSE 8087

WORKDIR /app/src

ENTRYPOINT ["/entrypoint.sh"]
