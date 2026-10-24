# Copyright (c) 2025 SenseTime. All Rights Reserved.
# Author: LazyLLM Team,  https://github.com/LazyAGI/LazyLLM
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import os

logger = logging.getLogger(__name__)

# 帮助文档图片随代码打包发布: images/doc_image/<日期>/<文件名>.png
# 与 storage 中的 doc_image 相对路径保持一致, 便于互相回填
BUNDLED_IMAGES_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "images"
)


def _bundled_filepath(rel_path: str) -> str:
    """获取打包图片的本地绝对路径。

    Args:
        rel_path (str): 相对 doc_image 的存储路径, 如 doc_image/260913/260913182723.png

    Returns:
        str: 打包目录下的绝对路径(可能不存在)
    """
    return os.path.join(BUNDLED_IMAGES_DIR, rel_path)


def sync_bundled_images() -> int:
    """启动时将打包图片同步进 storage, 自动补齐缺失的文档图片。

    storage 属于运行时数据, 可能被清理或迁移; 打包图片只读不写,
    每次启动仅回填 storage 中不存在的文件, 不覆盖用户后上传的同名图片。

    Returns:
        int: 本次回填的图片数量
    """
    from utils.util_storage import storage

    restored = 0
    root = os.path.join(BUNDLED_IMAGES_DIR, "doc_image")
    if not os.path.isdir(root):
        return 0

    for dirpath, _, filenames in os.walk(root):
        for filename in filenames:
            abs_path = os.path.join(dirpath, filename)
            rel_path = os.path.relpath(abs_path, BUNDLED_IMAGES_DIR)
            try:
                if storage.exists(rel_path):
                    continue
                with open(abs_path, "rb") as f:
                    storage.save(rel_path, f.read())
                restored += 1
            except Exception as e:  # 单个文件失败不影响整体启动
                logger.warning(f"同步文档图片失败 {rel_path}: {e}")

    if restored:
        logger.info(f"已从代码包回填 {restored} 张帮助文档图片到 storage")
    return restored


def load_bundled_image(rel_path: str):
    """读取打包图片, 用于 storage 缺失时的请求级兜底。

    Args:
        rel_path (str): 相对存储路径, 如 doc_image/260913/260913182723.png

    Returns:
        bytes: 图片内容; 文件不存在时返回 None
    """
    abs_path = _bundled_filepath(rel_path)
    if os.path.isfile(abs_path):
        try:
            with open(abs_path, "rb") as f:
                return f.read()
        except OSError as e:
            logger.warning(f"读取打包文档图片失败 {rel_path}: {e}")
    return None


def load_image(rel_path: str):
    """优先从 storage 读取文档图片, 缺失时回退到代码包并回填 storage。

    Args:
        rel_path (str): 相对存储路径, 如 doc_image/260913/260913182723.png

    Returns:
        bytes: 图片内容; 两处均不存在时返回 None
    """
    from utils.util_storage import storage

    try:
        if storage.exists(rel_path):
            return storage.load(rel_path, stream=False)
    except Exception as e:
        logger.warning(f"从 storage 读取文档图片失败 {rel_path}: {e}")

    data = load_bundled_image(rel_path)
    if data is not None:
        try:  # 回填 storage, 避免后续请求再次回退
            storage.save(rel_path, data)
        except Exception as e:
            logger.warning(f"回填文档图片到 storage 失败 {rel_path}: {e}")
    return data
