#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
org_fix_header.py — 统一 .org 文件头部格式

职责：
  - 保留 #+TITLE:
  - 删除其他所有 #+ 属性行
  - 写入标准头部：TITLE → OPTIONS → LANGUAGE → DATE → UPDATED
  - DATE 优先级：文件已有 > git 首次提交日期 > 文件修改时间
  - UPDATED 用当前日期
  - 保留正文不变
  - 跳过空文件

用法：
  python3 org_fix_header.py              # 默认处理 ~/workspace/项目管理
  python3 org_fix_header.py --dry-run    # 只预览不修改
"""

import os
import re
import logging
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# ========== 配置区 ==========
NOTES_DIR = os.path.expanduser("~/workspace/项目管理")
MAX_WORKERS = 8

# 日志
LOG_FILE = "org_fix_header.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 属性行正则
RE_TITLE = re.compile(r'^#\+TITLE:\s*(.+)$', re.IGNORECASE)
RE_DATE = re.compile(r'^#\+DATE:\s*(.+)$', re.IGNORECASE)
RE_KEYWORD = re.compile(r'^#\+[A-Z_]+:', re.IGNORECASE)
DATE_LINE_RE = re.compile(r'^\d{4}-\d{2}-\d{2}')


def build_git_date_map(notes_dir: Path) -> dict:
    """从 git 历史批量获取每个 .org 文件的首次提交日期"""
    date_map = {}
    try:
        result = subprocess.run(
            ["git", "log", "--reverse", "--format=%ai", "--name-only",
             "--diff-filter=A", "--", "*.org"],
            capture_output=True, text=True, cwd=notes_dir, timeout=60
        )
        current_date = None
        for line in result.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            if DATE_LINE_RE.match(line):
                current_date = line[:10]
            elif current_date and line not in date_map:
                date_map[line] = current_date
        logger.info(f"从 git 历史获取了 {len(date_map)} 个文件的创建日期")
    except Exception as e:
        logger.warning(f"获取 git 日期失败: {e}")
    return date_map


def fix_header(file_path: Path, git_dates: dict, dry_run: bool = False) -> str:
    """处理单个文件，返回结果描述"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if not content.strip():
        return f"skip: {file_path.name} 空文件"

    lines = content.splitlines()

    # 提取 TITLE
    title = None
    for line in lines:
        m = RE_TITLE.match(line.strip())
        if m:
            title = m.group(1).strip()
            break

    if not title:
        return f"skip: {file_path.name} 无TITLE"

    # 提取已有 DATE（保留）
    existing_date = None
    for line in lines:
        m = RE_DATE.match(line.strip())
        if m:
            existing_date = m.group(1).strip()[:10]  # 只取日期部分
            break

    # 确定 DATE：已有 > git > mtime
    if existing_date:
        date_str = existing_date
    else:
        rel_path = file_path.relative_to(file_path.parents[2])  # 相对于工作空间根
        # 尝试多种相对路径匹配
        date_str = None
        for parent in [file_path.parent]:
            for try_path in [
                str(file_path.relative_to(Path(NOTES_DIR))),
                file_path.name,
            ]:
                if try_path in git_dates:
                    date_str = git_dates[try_path]
                    break
            if date_str:
                break

        if not date_str:
            # 最后 fallback：用 mtime
            date_str = datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%Y-%m-%d")

    updated_str = datetime.now().strftime("%Y-%m-%d")

    # 分离：删除所有 #+ 属性行，保留正文
    body_lines = []
    for line in lines:
        if RE_KEYWORD.match(line.strip()):
            continue
        body_lines.append(line)

    # 去掉正文开头的空行
    while body_lines and not body_lines[0].strip():
        body_lines.pop(0)

    # 生成新头部
    new_header = [
        f"#+TITLE: {title}",
        "#+OPTIONS: ^:nil",
        "#+OPTIONS: toc:2",
        "#+LANGUAGE: zh-CN",
        f"#+DATE: {date_str}",
        f"#+UPDATED: {updated_str}",
    ]

    new_content = "\n".join(new_header) + "\n\n" + ("\n".join(body_lines) if body_lines else "")
    if not new_content.endswith("\n"):
        new_content += "\n"

    if dry_run:
        return f"dry: {file_path.name} TITLE={title} DATE={date_str}"

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    return f"ok: {file_path.name} TITLE={title} DATE={date_str}"


def main():
    parser = argparse.ArgumentParser(description="统一 .org 文件头部格式")
    parser.add_argument("--dry-run", action="store_true", help="只预览不修改")
    args = parser.parse_args()

    notes_dir = Path(NOTES_DIR)
    org_files = list(notes_dir.rglob("*.org"))

    # 先批量获取 git 日期
    logger.info("正在从 git 历史获取文件创建日期...")
    git_dates = build_git_date_map(notes_dir)

    logger.info(f"找到 {len(org_files)} 个 .org 文件，使用 {MAX_WORKERS} 线程并行处理"
                + (" (DRY RUN)" if args.dry_run else ""))

    ok_count = 0
    skip_count = 0
    dry_count = 0
    error_count = 0
    done_count = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(fix_header, f, git_dates, args.dry_run): f for f in org_files}
        for future in as_completed(futures):
            done_count += 1
            file_path = futures[future]
            try:
                result = future.result()
            except Exception as e:
                error_count += 1
                logger.error(f"[{done_count}/{len(org_files)}] {file_path.name} 异常: {e}")
                continue

            if result.startswith("ok:"):
                ok_count += 1
                logger.info(f"[{done_count}/{len(org_files)}] ✅ {result[4:]}")
            elif result.startswith("dry:"):
                dry_count += 1
                logger.info(f"[{done_count}/{len(org_files)}] 👁️  {result[5:]}")
            elif result.startswith("skip:"):
                skip_count += 1
            else:
                error_count += 1
                logger.error(f"[{done_count}/{len(org_files)}] ❌ {result[7:]}")

    logger.info(f"处理完成: 成功 {ok_count}, 预览 {dry_count}, "
                f"跳过 {skip_count}, 失败 {error_count}, 总计 {len(org_files)}")


if __name__ == "__main__":
    main()
