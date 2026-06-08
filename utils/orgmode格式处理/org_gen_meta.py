#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
org_gen_meta.py — AI 生成 .org 文件的 TAGS/CATEGORIES/SUMMARY

职责：
  - 读取文件正文
  - 通过 AI 一次性生成 tags、categories、summary
  - 插入头部 #+UPDATED: 之后

用法：
  python3 org_gen_meta.py              # 默认处理 ~/workspace/项目管理
  python3 org_gen_meta.py --force      # 强制重新生成（覆盖已有的）
"""

import os
import re
import json
import time
import logging
import argparse
from pathlib import Path
from openai import OpenAI
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

# ========== 配置区 ==========
NOTES_DIR = os.path.expanduser("~/workspace/项目管理")
OPENAI_MODEL = "deepseek-v3"
OPENAI_API_KEY = "sk-12345678"
OPENAI_BASE_URL = "http://10.11.12.164:4000/v1"

MAX_CONTENT_CHARS = 2000     # 传递给 AI 的文本长度
REQUEST_TIMEOUT = 30         # 单次请求超时（秒）
RETRY_TIMES = 2              # 失败重试次数
MAX_WORKERS = 8              # 并行线程数

# 日志
LOG_FILE = "org_gen_meta.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 初始化 OpenAI 客户端
client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_BASE_URL,
    timeout=REQUEST_TIMEOUT,
)

# 属性行正则
RE_KEYWORD = re.compile(r'^#\+[A-Z_]+:', re.IGNORECASE)
RE_UPDATED = re.compile(r'^#\+UPDATED:\s*(.+)$', re.IGNORECASE)
RE_TAGS = re.compile(r'^#\+TAGS:\s*(.+)$', re.IGNORECASE)
RE_CATEGORIES = re.compile(r'^#\+CATEGORIES:\s*(.+)$', re.IGNORECASE)
RE_SUMMARY = re.compile(r'^#\+SUMMARY:\s*(.+)$', re.IGNORECASE)


def extract_body(content: str) -> str:
    """提取正文（去掉所有 #+ 属性行）"""
    lines = content.splitlines()
    body_lines = []
    for line in lines:
        if RE_KEYWORD.match(line.strip()):
            continue
        body_lines.append(line)
    text = "\n".join(body_lines).strip()
    return text[:MAX_CONTENT_CHARS]


def call_ai_meta(title: str, text: str) -> Optional[dict]:
    """调用 AI 一次性生成 tags、categories、summary，返回 dict 或 None"""
    prompt = f"""请为以下技术文档生成元信息。文档标题：{title}

文档内容：
---
{text}
---

请严格按照以下 JSON 格式输出，不要有任何其他内容：
{{"tags": "标签1,标签2,标签3", "categories": "分类名", "summary": "一句话摘要，不超过50字"}}

要求：
- tags：3-5个关键词，用英文逗号分隔，反映文档的技术主题
- categories：一个简短的分类名，如"项目管理"、"支付系统"、"工作计划"等
- summary：一句精炼的中文摘要，概括文档核心内容"""

    for attempt in range(RETRY_TIMES):
        try:
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "你是一个技术文档分类专家，输出严格遵循 JSON 格式。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=200,
            )
            raw = response.choices[0].message.content
            if raw is None:
                raise ValueError("API returned None content")

            # 提取 JSON（模型可能包裹在 ```json ... ``` 中）
            raw = raw.strip()
            json_match = re.search(r'\{[^}]+\}', raw, re.DOTALL)
            if not json_match:
                raise ValueError(f"No JSON found in response: {raw[:100]}")

            data = json.loads(json_match.group())

            # 校验字段
            if not all(k in data for k in ('tags', 'categories', 'summary')):
                raise ValueError(f"Missing fields in JSON: {data}")

            # summary 清理
            summary = data['summary'].strip()
            summary = re.sub(r'^摘要：?', '', summary)
            if len(summary) > 80:
                summary = summary[:80]

            return {
                'tags': data['tags'].strip(),
                'categories': data['categories'].strip(),
                'summary': summary,
            }
        except Exception as e:
            logger.warning("AI meta call failed (attempt %d): %s", attempt + 1, e)
            time.sleep(2 ** attempt)
    return None


def extract_title(content: str) -> Optional[str]:
    """从头部提取 TITLE"""
    for line in content.splitlines():
        m = re.match(r'^#\+TITLE:\s*(.+)$', line.strip(), re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return None


def update_meta_in_file(file_path: Path, meta: dict) -> bool:
    """在 #+UPDATED: 后插入 TAGS/CATEGORIES/SUMMARY，删除旧的"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        logger.error(f"读取文件失败 {file_path}: {e}")
        return False

    # 删除旧的 TAGS/CATEGORIES/SUMMARY 行
    cleaned = [l for l in lines
               if not RE_TAGS.match(l)
               and not RE_CATEGORIES.match(l)
               and not RE_SUMMARY.match(l)]

    # 找 #+UPDATED: 行的位置，在其后插入
    insert_idx = -1
    for idx, line in enumerate(cleaned):
        if RE_UPDATED.match(line):
            insert_idx = idx + 1
            break

    # 如果没有 UPDATED，找最后一个 #+ 属性行之后
    if insert_idx == -1:
        insert_idx = 0
        for idx, line in enumerate(cleaned):
            if RE_KEYWORD.match(line):
                insert_idx = idx + 1

    new_meta_lines = [
        f"#+TAGS: {meta['tags']}\n",
        f"#+CATEGORIES: {meta['categories']}\n",
        f"#+SUMMARY: {meta['summary']}\n",
    ]

    for i, meta_line in enumerate(new_meta_lines):
        cleaned.insert(insert_idx + i, meta_line)

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(cleaned)
        return True
    except Exception as e:
        logger.error(f"写入文件失败 {file_path}: {e}")
        return False


def process_file(file_path: Path, force: bool = False) -> str:
    """处理单个文件，返回结果描述"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if not content.strip():
        return f"skip: {file_path.name} 空文件"

    # 检查是否已有完整元信息
    has_tags = bool(RE_TAGS.search(content))
    has_categories = bool(RE_CATEGORIES.search(content))
    has_summary = bool(RE_SUMMARY.search(content))

    if has_tags and has_categories and has_summary and not force:
        return f"skip: {file_path.name} 已有完整元信息"

    title = extract_title(content)
    if not title:
        return f"skip: {file_path.name} 无TITLE"

    body = extract_body(content)
    if not body:
        return f"skip: {file_path.name} 无正文"

    meta = call_ai_meta(title, body)
    if meta is None:
        return f"error: {file_path.name} AI生成失败"

    if update_meta_in_file(file_path, meta):
        return f"ok: {file_path.name} -> tags={meta['tags']} cat={meta['categories']} summary={meta['summary']}"
    else:
        return f"error: {file_path.name} 写入失败"


def main():
    parser = argparse.ArgumentParser(description="AI 生成 .org 文件元信息")
    parser.add_argument("--force", action="store_true", help="强制重新生成（覆盖已有的）")
    args = parser.parse_args()

    org_files = list(Path(NOTES_DIR).rglob("*.org"))
    logger.info(f"找到 {len(org_files)} 个 .org 文件，使用 {MAX_WORKERS} 线程并行处理"
                + (" (FORCE)" if args.force else ""))

    ok_count = 0
    skip_count = 0
    error_count = 0
    done_count = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(process_file, f, args.force): f for f in org_files}
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
            elif result.startswith("skip:"):
                skip_count += 1
                logger.debug(f"[{done_count}/{len(org_files)}] ⏭️  {result[6:]}")
            else:
                error_count += 1
                logger.error(f"[{done_count}/{len(org_files)}] ❌ {result[7:]}")

    logger.info(f"处理完成: 成功 {ok_count}, 跳过 {skip_count}, "
                f"失败 {error_count}, 总计 {len(org_files)}")


if __name__ == "__main__":
    main()
