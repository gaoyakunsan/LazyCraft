# -*- coding: utf-8 -*-
"""阶段 1: 登录并截取 01-登录页 / 02-应用商店列表"""
import sys

sys.path.insert(0, "/root/LazyCraft/scripts/doc_images")
import doc_common
from doc_common import Shooter


def main():
    s = Shooter(login=False)
    try:
        # 01-登录页: 协议弹窗打开状态最有代表性, 但兜底截表单本身
        s.page.goto("http://127.0.0.1:30382/signin", wait_until="domcontentloaded")
        s.page.wait_for_timeout(2500)
        s.shot("01-登录页")
        # 登录(处理可能的用户协议弹窗)
        s.login()
        # 02-应用商店列表
        s.page.goto("http://127.0.0.1:30382/apps", wait_until="domcontentloaded")
        s.page.wait_for_timeout(4000)
        s.shot("02-应用商店列表")
    finally:
        s.close()


if __name__ == "__main__":
    main()
