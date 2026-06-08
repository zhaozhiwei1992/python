#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
org_validate.py — 校验 .org 文件头部完整性

职责：
  - 检查所有文件是否具备完整的头部字段
  - 输出缺失字段报告

用法：
  python3 org_validate.py              # 默认检查 ~/workspace/项目管理
"""

import os
import re
import logging
from pathlib import Path
from collections import defaultdict

# ========== 配置区 ==========
NOTES_DIR = os.path.expanduser("~/workspace/项目管理")

# 日志
LOG_FILE = "org_validate.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 必需字段
REQUIRED_FIELDS = [
    ("TITLE",     re.compile(r'^#\+TITLE:', re.IGNORECASE | re.MULTILINE)),
    ("OPTIONS",   re.compile(r'^#\+OPTIONS:', re.IGNORECASE | re.MULTILINE)),
    ("LANGUAGE",  re.compile(r'^#\+LANGUAGE:', re.IGNORECASE | re.MULTILINE)),
    ("DATE",      re.compile(r'^#\+DATE:', re.IGNORECASE | re.MULTILINE)),
    ("UPDATED",   re.compile(r'^#\+UPDATED:', re.IGNORECASE | re.MULTILINE)),
    ("TAGS",      re.compile(r'^#\+TAGS:', re.IGNORECASE | re.MULTILINE)),
    ("CATEGORIES", re.compile(r'^#\+CATEGORIES:', re.IGNORECASE | re.MULTILINE)),
    ("SUMMARY",   re.compile(r'^#\+SUMMARY:', re.IGNORECASE | re.MULTILINE)),
]


def validate_file(file_path: Path) -> list:
    """校验单个文件，返回缺失字段列表"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read(4096)  # 只读头部就够了

    if not content.strip():
        return ["空文件"]

    missing = []
    for name, pattern in REQUIRED_FIELDS:
        if not pattern.search(content):
            missing.append(name)
    return missing


def main():
    org_files = list(Path(NOTES_DIR).rglob("*.org"))
    logger.info(f"检查 {len(org_files)} 个 .org 文件")

    total = len(org_files)
    complete = 0
    empty = 0
    missing_stats = defaultdict(int)
    problems = []

    for fp in org_files:
        missing = validate_file(fp)
        if not missing:
            complete += 1
        elif missing == ["空文件"]:
            empty += 1
        else:
            for field in missing:
                missing_stats[field] += 1
            problems.append((str(fp.relative_to(NOTES_DIR)), missing))

    # 输出报告
    print("\n" + "=" * 60)
    print(f"校验报告：{NOTES_DIR}")
    print("=" * 60)
    print(f"总计: {total} 个文件")
    print(f"✅ 完整: {complete} 个")
    print(f"⚠️  空文件: {empty} 个")
    print(f"❌ 缺失字段: {total - complete - empty} 个")
    print()

    if missing_stats:
        print("缺失字段统计:")
        for field, count in sorted(missing_stats.items(), key=lambda x: -x[1]):
            print(f"  {field}: {count} 个文件缺失")
        print()

    if problems:
        print("问题文件列表:")
        for rel_path, missing in sorted(problems):
            print(f"  {rel_path}: 缺 {', '.join(missing)}")
    else:
        print("🎉 所有文件头部完整！")

    logger.info(f"校验完成: 完整 {complete}, 空文件 {empty}, 缺失 {total - complete - empty}")


if __name__ == "__main__":
    main()
