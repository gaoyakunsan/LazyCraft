# -*- coding: utf-8 -*-
"""阶段 6: 帮助文档图片全链路验证

打开 /console/api/doc/view docsify 页面, 断言 README 引用的全部图片
HTTP 200 且实际渲染(naturalWidth > 0)。用法:
    python s06_verify.py
"""
import re
import sys

import requests

sys.path.insert(0, "/root/LazyCraft/scripts/doc_images")
from doc_common import Shooter, api_token

BASE = "http://127.0.0.1:30382"


def image_urls_from_readme():
    r = requests.get(f"{BASE}/console/api/doc/view/README.md", timeout=30)
    r.raise_for_status()
    return re.findall(r"!\[[^\]]*\]\((/console/api/doc/image/[^)]+)\)", r.text)


def main():
    urls = image_urls_from_readme()
    print(f"README 引用图片 {len(urls)} 张")
    bad = []
    for u in urls:
        r = requests.get(BASE + u, timeout=30)
        ok = r.status_code == 200 and r.headers.get("Content-Type", "").startswith("image")
        if not ok:
            bad.append((u, r.status_code))
    print("HTTP 检查:", "全部 200" if not bad else bad)

    s = Shooter(viewport=(1440, 900))
    try:
        # 打开 docsify 页面并滚动到底, 触发所有图片加载
        s.page.goto(f"{BASE}/console/api/doc/view", wait_until="domcontentloaded")
        s.page.wait_for_timeout(5000)
        s.page.evaluate("""async () => {
            for (let i = 0; i < 40; i++) {
                window.scrollBy(0, 1200);
                await new Promise(r => setTimeout(r, 300));
            }
        }""")
        s.page.wait_for_timeout(3000)
        res = s.page.evaluate("""() => {
            const imgs = [...document.querySelectorAll('img')];
            return {total: imgs.length,
                    broken: imgs.filter(i => !i.complete || i.naturalWidth === 0)
                                 .map(i => i.getAttribute('src'))};
        }""")
        print("页面 img 总数:", res["total"])
        print("渲染失败:", res["broken"] or "无")
        assert not bad and not res["broken"], "存在缺失或未渲染图片"
        print("VERIFY-OK")
    finally:
        s.close()


if __name__ == "__main__":
    main()
