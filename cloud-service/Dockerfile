# cloud-service(AMS 推理 31340 / FT 微调 31341)服务镜像
#
# 环境层:本地固化的基础镜像(由原 registry.cn-hangzhou.aliyuncs.com/lazyllm/lazyllm:0b1a31c
#   docker tag 而来,conda 环境 torch/vllm 等依赖与其完全一致,不再依赖远端仓库拉取)
# 源码层:本仓库 cloud-service/lazyllm,即 LazyLLM 0b1a31c(v0.7.1)源码,
#   修改源码后执行: docker build -t lazycraft/cloud-service:0b1a31c-src ./
#   再 docker compose up -d cloud-service 生效
FROM lazycraft/cloud-service-base:0b1a31c

# 先清空再放入,保证与仓库源码严格一致(避免残留上游已删除的旧文件)
COPY lazyllm /tmp/lazyllm_src
RUN rm -rf /opt/miniconda3/envs/lazyllm/lib/python3.10/site-packages/lazyllm \
    && mv /tmp/lazyllm_src /opt/miniconda3/envs/lazyllm/lib/python3.10/site-packages/lazyllm \
    && find /opt/miniconda3/envs/lazyllm/lib/python3.10/site-packages/lazyllm -name '__pycache__' -type d -exec rm -rf {} +
