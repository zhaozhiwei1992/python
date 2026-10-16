#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_module_overview.py — 汇总功能模块目录，生成「AI 中台功能实现总览」汇报文档

职责：
  - 扫描 03_功能模块/<模块>/**/*.org
  - 提取 #+TITLE / #+SUMMARY / #+TAGS / #+DATE / #+UPDATED 与一级章节
  - 按「模块 → 功能」归并（需求规格说明书 / 技术方案 / API文档 等同一功能的文档并成一条）
  - 输出 org 汇报文档到 07_汇报材料/，附数据质量提示（SUMMARY 缺失/无信息）

用法：
  python3 gen_module_overview.py                      # 默认项目路径，写入 07_汇报材料/
  python3 gen_module_overview.py --stdout             # 只打印不写文件
  python3 gen_module_overview.py --no-outline         # 不列「关键章节」列
  python3 gen_module_overview.py -r <项目目录> -o <输出文件>
"""

import os
import re
import sys
import argparse
from collections import defaultdict
from datetime import date

# ========== 配置区 ==========
DEFAULT_ROOT = os.path.expanduser(
    "~/workspace/项目管理/开发文档/财政研发中心AI建设"
)
MODULE_DIR_NAME = "03_功能模块"
DEFAULT_OUT_NAME = "03_AI中台功能实现总览.org"   # 放在 <root>/07_汇报材料/
REPORT_DIR_NAME = "07_汇报材料"

# 文档类型后缀（长的在前，避免「技术方案」误吃「需求规格说明书」）
TYPE_SUFFIXES = [
    "需求规格说明书",
    "技术方案",
    "API文档",
    "前端设计",
    "数据维护",
    "导出导入实现",
    "模块总览",
    "总览",
]
# 索引类文件（不作为功能条目）
INDEX_FILES = {"README.org", "00_模块总览.org"}

# 章节黑名单（这些不是「功能点」，分析章节时不展示）
OUTLINE_SKIP = {
    "文档信息", "概述", "参考", "参考文献", "变更历史", "版本历史",
    "目录说明", "使用指南", "技术栈", "背景", "需求概述",
}
OUTLINE_MAX = 4          # 每个功能最多展示几个关键章节
SUMMARY_TRIM_PREFIX = re.compile(
    r"^(本文档|本文|本文件|该文档|文档|设计文档)?(主要)?"
    r"(描述|介绍|说明|概述|给出|列出|记录|阐述|总结|概括)(了|的是)?[：:，,]?\s*"
)
SUMMARY_MIN_LEN = 10     # 摘要短于此长度视为「无信息」
DESC_MAX = 120           # 「说明」列最大字符数（超出截断）
PREFIX_RE = re.compile(r"^\d+[_\-.\s]*")


def parse_args():
    p = argparse.ArgumentParser(
        description="汇总 03_功能模块，生成 AI 中台功能实现总览（汇报用）"
    )
    p.add_argument("-r", "--root", default=DEFAULT_ROOT, help="项目文档根目录")
    p.add_argument("-o", "--out", default=None, help="输出文件（默认 07_汇报材料/03_AI中台功能实现总览.org）")
    p.add_argument("--stdout", action="store_true", help="只打印，不写文件")
    p.add_argument("--no-outline", action="store_true", help="不输出「关键章节」列")
    p.add_argument("--no-clean", action="store_true", help="不清理摘要开头的“本文档描述了”等套话")
    p.add_argument("--only-plan", action="store_true",
                   help="只提取各功能的「技术方案」+ 其 SUMMARY，输出一张功能总表（汇报最简口径）")
    return p.parse_args()


def read_headings(path, limit=60):
    """提取一级章节标题（* xxx），用于「关键章节」列"""
    out = []
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for line in f:
                if line.startswith("* "):
                    h = re.sub(r"^\d+[.、)）]\s*", "", line[2:].strip())
                    if not h or h.startswith("["):
                        continue
                    if h not in OUTLINE_SKIP:
                        out.append(h)
                    if len(out) >= limit:
                        break
    except OSError:
        pass
    return out


def parse_header(path):
    """解析 #+KEY: value 头部（同 key 取首次出现）"""
    fields = {}
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for line in f:
                if not line.startswith("#+"):
                    continue
                m = re.match(r"^#\+([A-Za-z_]+):\s*(.*?)\s*$", line)
                if not m:
                    continue
                k, v = m.group(1).upper(), m.group(2)
                fields.setdefault(k, v)
    except OSError:
        pass
    return fields


def clean_summary(text):
    """去掉“本文档描述了……”“设计文档，……”这类套话，保留信息主体"""
    s = SUMMARY_TRIM_PREFIX.sub("", (text or "").strip())
    s = re.sub(r"^(本文档|本文|本文件)\s*设计\s*", "", s)
    s = re.sub(r"^\S{0,8}文档[，,：:]\s*", "", s)
    s = s.strip(" ：:，,。.；;")
    return s.rstrip("。.")


def split_name(filename):
    """文件名 → (功能名, 文档类型)"""
    base = re.sub(r"\.org$", "", os.path.basename(filename)).strip()
    while PREFIX_RE.match(base):          # 循环去 02_05_ / 002_ / 06 之类编号前缀
        base = PREFIX_RE.sub("", base, count=1).strip()
    for suf in TYPE_SUFFIXES:
        if base.endswith("-" + suf) or base.endswith(" " + suf):
            return base[: -(len(suf) + 1)].strip(), suf
    return base, "其他"


def clip(text, limit=DESC_MAX):
    t = (text or "").strip()
    return t if len(t) <= limit else t[:limit].rstrip(" ，,、") + "…"


def scan(root, with_outline=True):
    """返回 {模块: [文档记录]}"""
    mod_root = os.path.join(root, MODULE_DIR_NAME)
    if not os.path.isdir(mod_root):
        sys.exit(f"[错误] 模块目录不存在：{mod_root}")

    result = {}
    for mod in sorted(os.listdir(mod_root)):
        mod_path = os.path.join(mod_root, mod)
        if not os.path.isdir(mod_path):
            continue
        docs = []
        for dirpath, dirnames, filenames in os.walk(mod_path):
            dirnames[:] = [d for d in dirnames if not d.startswith(".")]
            for fn in sorted(filenames):
                if not fn.endswith(".org") or fn.startswith(".#"):
                    continue
                full = os.path.join(dirpath, fn)
                rel = os.path.relpath(full, root).replace(os.sep, "/")
                head = parse_header(full)
                title = head.get("TITLE") or re.sub(r"\.org$", "", fn)
                summary = head.get("SUMMARY", "")
                func, dtype = split_name(fn)
                docs.append({
                    "module": mod,
                    "path": full,
                    "rel": rel,
                    "file": fn,
                    "title": title,
                    "summary": summary,
                    "clean": clean_summary(summary),
                    "tags": head.get("TAGS", ""),
                    "updated": head.get("UPDATED") or head.get("DATE", ""),
                    "func": func,
                    "type": dtype,
                    "index": fn in INDEX_FILES or "总览" in dtype,
                    "headings": read_headings(full) if with_outline else [],
                })
        if docs:
            result[mod] = docs
    return result


def group_by_func(docs):
    """模块内文档 → 功能分组（同一功能的多份文档并成一条）"""
    groups = defaultdict(list)
    module_docs = []
    for d in docs:
        if d["index"]:
            module_docs.append(d)
        else:
            groups[d["func"]].append(d)

    TYPE_ORDER = {t: i for i, t in enumerate(TYPE_SUFFIXES + ["其他"])}
    out = []
    for func, items in groups.items():
        items.sort(key=lambda d: TYPE_ORDER.get(d["type"], 99))
        # 说明取最权威的一份：技术方案 > 需求规格说明书 > 其他
        desc, desc_from = "", ""
        for t in ("技术方案", "需求规格说明书", "API文档"):
            hit = next((d for d in items if d["type"] == t and d["clean"]), None)
            if hit:
                desc, desc_from = hit["clean"], hit["type"]
                break
        if not desc:
            for d in items:
                if d["clean"]:
                    desc, desc_from = d["clean"], d["type"]
                    break
        out.append({
            "func": func,
            "docs": items,
            "desc": desc,
            "desc_from": desc_from,
            "has_plan": any(d["type"] == "技术方案" for d in items),
        })
    out.sort(key=lambda g: (not g["has_plan"], g["func"]))
    return out, module_docs


def esc(text):
    """org 表格转义"""
    return (text or "").replace("|", "\\vert{}").replace("\n", " ").strip()


def rel_to(path, base):
    """把绝对路径转成相对 base 目录的链接（org file: 链接按文件所在目录解析）"""
    return os.path.relpath(path, base).replace(os.sep, "/")


def doc_link(d, base, text=None):
    return f"[[file:{rel_to(d['path'], base)}][{text or d['type']}]]"


def module_position(groups, module_docs):
    """模块定位：优先模块总览的摘要；若它是“文档索引”类描述，则退回首项功能的说明"""
    idx = next((d for d in module_docs if d["clean"]), None)
    if idx and not any(k in idx["clean"] for k in ("索引", "总览", "文档列表")):
        return clip(idx["clean"])
    for g in groups:
        if g["desc"]:
            return clip(g["desc"])
    return clip(idx["clean"]) if idx else ""


def build_plan_only(root, data, link_base):
    """只提取技术方案 + 其 SUMMARY：模块 | 功能 | 说明 | 文档"""
    today = date.today().isoformat()
    rows, n_mod, n_doc = [], 0, 0
    for mod, docs in data.items():
        groups, _ = group_by_func(docs)
        plans = [g for g in groups if g["has_plan"]]
        if not plans:
            continue
        n_mod += 1
        for g in plans:
            plan = next(d for d in g["docs"] if d["type"] == "技术方案")
            rows.append((mod, g["func"], plan["clean"], doc_link(plan, link_base)))
            n_doc += 1
    L = [f"#+TITLE: AI中台功能实现总览（技术方案口径）",
         "#+OPTIONS: ^:nil", "#+LANGUAGE: zh-CN", f"#+DATE: {today}", f"#+UPDATED: {today}",
         "#+TAGS: AI中台,功能清单,汇报,自动生成", "#+CATEGORIES: 汇报材料",
         f"#+SUMMARY: 直接提取 03_功能模块 下各功能的「技术方案」文档及其 #+SUMMARY，"
         f"共 {n_mod} 个模块 {n_doc} 项功能，用于汇报「AI 中台有哪些功能实现」。",
         "",
         f"本文件由 =gen_module_overview.py --only-plan= 自动生成（*勿手改*）。",
         "",
         "| # | 模块 | 功能 | 说明 | 文档 |",
         "|---+------+------+------+------|"]
    for i, (mod, func, desc, link) in enumerate(rows, 1):
        L.append(f"| {i} | {esc(mod)} | {esc(func)} | {esc(clip(desc)) or '—'} | {link} |")
    L += ["", f"*合计*：{n_mod} 个模块、{n_doc} 项功能（每项一条技术方案）。"]
    return "\n".join(L) + "\n"


def build_report(root, data, link_base, with_outline=True):
    today = date.today().isoformat()
    n_mod = len(data)
    n_doc = sum(len(v) for v in data.values())
    total_func = 0

    L = []
    A = L.append
    A(f"#+TITLE: AI中台功能实现总览（自动汇总）")
    A("#+OPTIONS: ^:nil")
    A("#+OPTIONS: toc:3")
    A("#+LANGUAGE: zh-CN")
    A(f"#+DATE: {today}")
    A(f"#+UPDATED: {today}")
    A("#+TAGS: AI中台,功能清单,汇报,自动生成")
    A("#+CATEGORIES: 汇报材料")
    A(f"#+SUMMARY: 自动汇总 03_功能模块 下 {n_mod} 个模块、{n_doc} 份文档的功能与摘要，"
      "用于汇报「AI 中台实现了哪些功能」；按模块→功能归并，同一功能的需求/方案/API 并成一条。")
    A("")
    A("* 0. 生成说明")
    A("")
    A("本文件由脚本自动生成，*请勿手工编辑*；改完 03_功能模块 下的文档后重跑：")
    A("")
    A("#+BEGIN_SRC bash")
    A("python3 ~/workspace/python/utils/orgmode格式处理/gen_module_overview.py")
    A("#+END_SRC")
    A("")
    A(f"- 数据源：={{root}}/{MODULE_DIR_NAME}/=")
    A("- 摘要取自各文档 =#+SUMMARY=；同一功能优先取「技术方案」的摘要")
    A(f"- 文档数不含 ={MODULE_DIR_NAME}/README.org=（模块清单），含各模块的 00_模块总览")
    A("")

    # ---- 模块总览表 ----
    A("* 1. 模块总览")
    A("")
    A("| # | 模块 | 功能项 | 文档数 | 模块定位 |")
    A("|---+------+--------+--------+----------|")
    mod_rows = []
    for i, (mod, docs) in enumerate(data.items(), 1):
        groups, module_docs = group_by_func(docs)
        total_func += len(groups)
        idx = next((d for d in module_docs if d["clean"]), None)
        pos = module_position(groups, module_docs)
        mod_path = os.path.join(root, MODULE_DIR_NAME, mod)
        A(f"| {i} | [[file:{rel_to(mod_path, link_base)}/][{mod}]] | {len(groups)} | {len(docs)} | {esc(pos)} |")
    A("")
    A(f"*合计*：{len(data)} 个模块，{total_func} 项功能，{n_doc} 份文档。")
    A("")

    # ---- 分模块功能清单 ----
    A("* 2. 分模块功能清单")
    A("")
    quality = []
    for mod, docs in data.items():
        groups, module_docs = group_by_func(docs)
        A(f"** {mod}（{len(groups)} 项功能 / {len(docs)} 份文档）")
        A("")
        cols = "| # | 功能 | 说明 | 配套文档 |"
        sep = "|---+------+------+----------|"
        if with_outline:
            cols = "| # | 功能 | 说明 | 关键章节 | 配套文档 |"
            sep = "|---+------+------+----------+----------|"
        A(cols)
        A(sep)
        for i, g in enumerate(groups, 1):
            links = " ".join(doc_link(d, link_base) for d in g["docs"])
            if with_outline:
                plan = next((d for d in g["docs"] if d["type"] == "技术方案"), None)
                hs = plan["headings"][:OUTLINE_MAX] if plan else []
                if plan and len(plan["headings"]) > OUTLINE_MAX:
                    hs.append("…")
                A(f"| {i} | {esc(g['func'])} | {esc(clip(g['desc'])) or '—'} "
                  f"| {esc('、'.join(hs))} | {links} |")
            else:
                A(f"| {i} | {esc(g['func'])} | {esc(clip(g['desc'])) or '—'} | {links} |")
            for d in g["docs"]:
                if not d["clean"] or len(d["clean"]) < SUMMARY_MIN_LEN:
                    quality.append((d, "SUMMARY 缺失或无信息"))
                elif d["clean"] == d["title"].strip():
                    quality.append((d, "SUMMARY 与标题相同"))
        if module_docs:
            A("")
            A("索引文档：" + " ".join(doc_link(d, link_base, d["file"]) for d in module_docs))
        A("")

    # ---- 质量提示 ----
    A("* 3. 文档质量提示（供补充 SUMMARY 用）")
    A("")
    if quality:
        A("| 文档 | 问题 | 当前 SUMMARY |")
        A("|------+------+--------------|")
        for d, why in quality:
            A(f"| [[file:{rel_to(d['path'], link_base)}][{d['file']}]] | {why} | "
              f"{esc(d['summary']) or '（空）'} |")
    else:
        A("无。")
    A("")

    # ---- 统计 ----
    A("* 4. 统计口径")
    A("")
    A("| 项 | 值 |")
    A("|----+----|")
    A(f"| 模块数 | {n_mod} |")
    A(f"| 功能项数 | {total_func} |")
    A(f"| 文档数 | {n_doc} |")
    A(f"| 生成日期 | {today} |")
    A("")
    A("统计口径：功能项 = 模块内去掉文档类型后缀后的功能名去重；"
      "同一功能的「需求规格说明书 / 技术方案 / API文档」计 1 项功能、3 份文档。")
    return "\n".join(L) + "\n"


def main():
    args = parse_args()
    root = os.path.abspath(os.path.expanduser(args.root))
    data = scan(root, with_outline=not args.no_outline)
    if not data:
        sys.exit("[错误] 未扫描到任何模块文档")
    # 关闭摘要清理时，用原始 SUMMARY 作为说明
    if args.no_clean:
        for docs in data.values():
            for d in docs:
                d["clean"] = d["summary"]
    out = args.out or os.path.join(root, REPORT_DIR_NAME, DEFAULT_OUT_NAME)
    link_base = os.path.dirname(os.path.abspath(out))
    if args.only_plan:
        report = build_plan_only(root, data, link_base)
    else:
        report = build_report(root, data, link_base, with_outline=not args.no_outline)

    if args.stdout:
        print(report)
        return
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(report)
    n_func = 0
    for docs in data.values():
        n_func += len(group_by_func(docs)[0])
    print(f"[完成] {len(data)} 个模块 / {n_func} 项功能 / "
          f"{sum(len(v) for v in data.values())} 份文档 → {out}")


if __name__ == "__main__":
    main()
