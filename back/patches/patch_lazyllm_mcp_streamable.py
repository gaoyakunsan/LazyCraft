#!/usr/bin/env python3
"""构建期补丁：让 lazyllm 0.7.1 的 MCPClient/make_mcp_tool 支持 Streamable HTTP 传输。

lazyllm 0.7.1 的 MCPClient._run_session 把 http/https URL 一律按 SSE 处理，
make_mcp_tool 也没有 transport 透传参数，导致 MCP 自定义服务的 Streamable_HTTP
类型在「工具测试」与「画布运行」两条链路上必然失败。

补丁内容（旧行为完全保留，向后兼容）：
  1. tools/mcp/client.py — MCPClient.__init__ 增加 transport=None 参数；
     _run_session 优先按 self._transport == 'Streamable_HTTP' 走
     mcp.client.streamable_http.streamablehttp_client 分支（注意其 yield 3 元组）。
  2. engine/engine.py    — make_mcp_tool 增加 transport=None 参数并透传给 MCPClient。

transport 缺省 None 时按 URL scheme 推断（原有行为），旧画布节点数据没有
transport 键，不受影响。长期方案：向上游 LazyLLM 提 PR 后删除本补丁。
"""
import sys

# 覆盖镜像内 lazyllm 的可能安装路径：
#   - back 镜像（python:3.10-slim, pip install .）
#   - cloud-service 系镜像（miniconda env）
ROOTS = [
    "/usr/local/lib/python3.10/site-packages/lazyllm",
    "/opt/miniconda3/envs/lazyllm/lib/python3.10/site-packages/lazyllm",
]

# ===== client.py: MCPClient.__init__ 增加 transport 参数 =====
CLIENT_INIT_OLD = """        headers: dict[str, Any] = None,
        timeout: float = 5,
    ):
        self._command_or_url = command_or_url
        self._args = args or []
        self._env = env
        self._headers = headers
        self._timeout = timeout
"""
CLIENT_INIT_NEW = """        headers: dict[str, Any] = None,
        timeout: float = 5,
        transport: str = None,
    ):
        self._command_or_url = command_or_url
        self._args = args or []
        self._env = env
        self._headers = headers
        self._timeout = timeout
        self._transport = transport
"""

# ===== client.py: _run_session 增加 Streamable HTTP 分支 =====
CLIENT_RUN_OLD = """    @asynccontextmanager
    async def _run_session(self):
        if urlparse(self._command_or_url).scheme in ('http', 'https'):
"""
CLIENT_RUN_NEW = """    @asynccontextmanager
    async def _run_session(self):
        if getattr(self, '_transport', None) == 'Streamable_HTTP':
            spec = importlib.util.find_spec('mcp.client.streamable_http')
            if spec is None:
                raise ImportError(
                    'Please install mcp to use mcp module. '
                    'You can install it with `pip install mcp`'
                )
            sh_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(sh_module)
            streamablehttp_client = sh_module.streamablehttp_client

            async with streamablehttp_client(
                url=self._command_or_url,
                headers=self._headers,
                timeout=self._timeout if self._timeout else 30,
                sse_read_timeout=max(self._timeout or 0, 300),
            ) as (read_stream, write_stream, _get_session_id):
                async with mcp.ClientSession(read_stream, write_stream) as session:
                    await session.initialize()
                    yield session
        elif urlparse(self._command_or_url).scheme in ('http', 'https'):
"""

# ===== engine.py: make_mcp_tool 透传 transport =====
ENGINE_OLD = """def make_mcp_tool(command_or_url: str, tool_name: str, args: Optional[List[str]] = None, env: Dict[str, str] = None,
                  headers: Dict[str, str] = None, timeout: float = 5):
    client = MCPClient(command_or_url, args or [], env, headers, timeout)
"""
ENGINE_NEW = """def make_mcp_tool(command_or_url: str, tool_name: str, args: Optional[List[str]] = None, env: Dict[str, str] = None,
                  headers: Dict[str, str] = None, timeout: float = 5, transport: str = None):
    client = MCPClient(command_or_url, args or [], env, headers, timeout, transport=transport)
"""

REPLACEMENTS = {
    "tools/mcp/client.py": [(CLIENT_INIT_OLD, CLIENT_INIT_NEW), (CLIENT_RUN_OLD, CLIENT_RUN_NEW)],
    "engine/engine.py": [(ENGINE_OLD, ENGINE_NEW)],
}


def patch_file(base_root, rel_path, pairs):
    path = f"{base_root}/{rel_path}"
    try:
        src = open(path).read()
    except OSError:
        return False
    if "Streamable_HTTP" in src:
        print(f"[patch-lazyllm-mcp-streamable] already patched: {path}")
        return True
    out = src
    for old, new in pairs:
        if old not in out:
            print(f"[patch-lazyllm-mcp-streamable] anchor not found in {path}, skip: {old.splitlines()[0][:60]}...")
            return False
        out = out.replace(old, new, 1)
    open(path, "w").write(out)
    print(f"[patch-lazyllm-mcp-streamable] patched: {path}")
    return True


patched_any = False
for root in ROOTS:
    if patch_file(root, "tools/mcp/client.py", REPLACEMENTS["tools/mcp/client.py"]):
        patched_any = True
    if patch_file(root, "engine/engine.py", REPLACEMENTS["engine/engine.py"]):
        patched_any = True

if not patched_any:
    sys.exit("[patch-lazyllm-mcp-streamable] no target file found")
