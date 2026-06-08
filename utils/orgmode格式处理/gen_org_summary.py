#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import time
import logging
from pathlib import Path
from openai import OpenAI
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

# ========== 配置区 ==========
NOTES_DIR = "/home/zhaozhiwei/workspace/notes"          # 你的 .org 笔记根目录
OPENAI_MODEL = "deepseek-v3"
OPENAI_API_KEY = "sk-12345678"
OPENAI_BASE_URL = "http://10.11.12.164:4000/v1"

# API 调用设置
MAX_CONTENT_CHARS = 2000     # 传递给 AI 的文本长度（控制 token）
SUMMARY_MAX_LEN = 80         # 摘要最大字符数（避免意外长文）
REQUEST_TIMEOUT = 30         # 单次请求超时（秒）
RETRY_TIMES = 2              # 失败重试次数
SLEEP_BETWEEN_FILES = 0.5    # 两个文件之间的延迟（秒），避免限流
MAX_WORKERS = 8              # 并行线程数

# 日志
LOG_FILE = "summary_generation.log"
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

# ========== 辅助函数 ==========
def extract_text_for_summary(content: str) -> str:
    """提取 .org 文件正文（去掉属性行、空行）的前 MAX_CONTENT_CHARS 个字符"""
    lines = content.splitlines()
    body_lines = []
    # 跳过开头的属性行（如 #TITLE:、#OPTIONS: 等）
    in_property_section = True
    for line in lines:
        stripped = line.strip()
        # 仍然以 #+ 开头且冒号，视为属性行
        if re.match(r'^#\+[A-Z_]+:', stripped):
            continue
        # 遇到非属性行后，开始收集正文
        if stripped and not stripped.startswith('#'):
            body_lines.append(line)
        # 如果空行，也保留（但为了节省 token，连续空行只留一个）
    # 合并并截断
    text = "\n".join(body_lines).strip()
    return text[:MAX_CONTENT_CHARS]

def call_ai_summary(text: str) -> Optional[str]:
    """调用 OpenAI 兼容 API 生成一句话摘要，失败返回 None"""
    prompt = (
        "请用一句中文概括以下技术笔记的核心内容，要求简洁明了，不超过50字。"
        "只输出摘要本身，不要有任何额外解释或前缀。\n\n"
        f"笔记内容：\n---\n{text}\n---\n\n摘要："
    )
    for attempt in range(RETRY_TIMES):
        try:
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "你是一个专业的技术文档摘要助手，输出精炼准确。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=100,
            )
            # 调试：打印原始响应
            msg = response.choices[0].message
            logger.debug(
                "API raw response: content=%r, reasoning_content=%r",
                msg.content,
                getattr(msg, 'reasoning_content', 'N/A'),
            )

            # content 可能为 None（某些模型/代理会这样返回）
            raw = msg.content
            if raw is None:
                # 某些代理返回空 content 时，response 里可能有其他字段
                logger.warning("API returned None content, full message: %r", msg)
                raise ValueError("API returned None content")

            summary = raw.strip()
            # 去除可能自带的"摘要："前缀
            summary = re.sub(r'^摘要：?', '', summary)
            if len(summary) > SUMMARY_MAX_LEN:
                summary = summary[:SUMMARY_MAX_LEN]
            if not summary:
                raise ValueError("Empty summary after processing")
            return summary
        except Exception as e:
            logger.warning("API call failed (attempt %d): %s", attempt + 1, e)
            time.sleep(2 ** attempt)  # 指数退避
    return None

def update_summary_in_file(file_path: Path, new_summary: str) -> bool:
    """更新或插入 #+SUMMARY: 行到 .org 文件中，返回是否成功

    同时清理之前错误生成的 #SUMMARY: 行。
    插入位置：所有 #+KEYWORD: 属性行的最后。
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        logger.error(f"读取文件失败 {file_path}: {e}")
        return False

    summary_pattern = re.compile(r'^#\+SUMMARY:\s*.*$', re.IGNORECASE)
    old_wrong_pattern = re.compile(r'^#SUMMARY:\s*.*$', re.IGNORECASE)

    # 清理：删除所有 #SUMMARY: 和 #+SUMMARY: 行
    cleaned = [l for l in lines
               if not summary_pattern.match(l) and not old_wrong_pattern.match(l)]

    # 找所有 #+KEYWORD: 属性行的最后位置，插入到其后
    insert_idx = 0
    for idx, line in enumerate(cleaned):
        if re.match(r'^#\+[A-Z_]+:', line):
            insert_idx = idx + 1

    cleaned.insert(insert_idx, f"#+SUMMARY: {new_summary}\n")

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(cleaned)
        return True
    except Exception as e:
        logger.error(f"写入文件失败 {file_path}: {e}")
        return False

def process_file(file_path: Path) -> str:
    """处理单个文件，返回结果描述"""
    # 检查是否已有摘要
    with open(file_path, 'r', encoding='utf-8') as f:
        first_kb = f.read(1024)
    existing = re.search(r'^#\+SUMMARY:\s*(.+)$', first_kb, re.MULTILINE)
    if existing and existing.group(1).strip():
        return f"skip: {file_path.name} 已有摘要"

    # 读取完整内容并提取正文
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            full_content = f.read()
    except Exception as e:
        return f"error: 读取 {file_path.name} 失败: {e}"

    text_for_ai = extract_text_for_summary(full_content)
    if not text_for_ai:
        return f"skip: {file_path.name} 无正文"

    summary = call_ai_summary(text_for_ai)
    if summary is None:
        return f"error: {file_path.name} 摘要生成失败"

    if update_summary_in_file(file_path, summary):
        return f"ok: {file_path.name} -> {summary}"
    else:
        return f"error: {file_path.name} 写入失败"


def main():
    org_files = list(Path(NOTES_DIR).rglob("*.org"))
    logger.info(f"找到 {len(org_files)} 个 .org 文件，使用 {MAX_WORKERS} 线程并行处理")

    success_count = 0
    skip_count = 0
    error_count = 0
    done_count = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(process_file, f): f for f in org_files}
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
                success_count += 1
                logger.info(f"[{done_count}/{len(org_files)}] ✅ {result[4:]}")
            elif result.startswith("skip:"):
                skip_count += 1
                logger.info(f"[{done_count}/{len(org_files)}] ⏭️  {result[6:]}")
            else:
                error_count += 1
                logger.error(f"[{done_count}/{len(org_files)}] ❌ {result[7:]}")

    logger.info(f"处理完成: 成功 {success_count}, 跳过 {skip_count}, 失败 {error_count}, 总计 {len(org_files)}")

if __name__ == "__main__":
    main()
