#!/usr/bin/env python3
"""Nexus 组件漏洞扫描器（高危及以上）+ 报告生成

数据源：OSV.dev（npm / Maven，服务端精确版本匹配）
比对对象：Nexus 中所有 npm / maven2 格式的 proxy 仓库（git 缓存组件）

用法：
  python3 nexus_vuln_scan.py                                   # 扫全部 npm/maven proxy 仓库
  python3 nexus_vuln_scan.py --repos npm-proxy,maven-central   # 只扫指定仓库
  python3 nexus_vuln_scan.py --out-dir reports                 # 指定报告输出目录

凭据（优先级从高到低）：
  NEXUS_URL / NEXUS_USER / NEXUS_PASS 环境变量
  同目录已有脚本（npm恶意包扫描.py / maven恶意包扫描.py）中解析（兼容旧脚本）

产出：<out-dir>/nexus漏洞扫描报告-<时间戳>.md  + .csv（仅高危及以上命中）
"""

import argparse
import csv
import json
import os
import re
import sys
import time
import datetime as dt
import concurrent.futures
from pathlib import Path

import requests

OSV_BATCH_URL = "https://api.osv.dev/v1/querybatch"
OSV_VULN_URL = "https://api.osv.dev/v1/vulns/{}"
OSV_BATCH_SIZE = 1000  # OSV batch 单次上限
VULN_CACHE_DAYS = 7    # 漏洞详情缓存天数（OSV 数据会更新，别缓存太久）
HIGH_LEVELS = {"HIGH", "CRITICAL"}

ECOSYSTEM_BY_FORMAT = {"npm": "npm", "maven2": "Maven"}


def load_nexus_config():
    """读取 Nexus 连接配置：环境变量优先，其次从同目录旧脚本解析。"""
    url = os.getenv("NEXUS_URL")
    user = os.getenv("NEXUS_USER")
    pwd = os.getenv("NEXUS_PASS")
    if url and user and pwd:
        return url, user, pwd
    sys.exit("[!] 未找到 Nexus 凭据：请设置 NEXUS_URL/NEXUS_USER/NEXUS_PASS 环境变量")


def get_repositories(session, nexus_url):
    """列出所有仓库，返回 [(name, format, type)]"""
    resp = session.get(f"{nexus_url}/service/rest/v1/repositories", timeout=30)
    resp.raise_for_status()
    return [(r["name"], r["format"], r["type"]) for r in resp.json()]


def list_components(session, nexus_url, repo):
    """分页拉取指定仓库全部组件，返回 [{name, version, id, group}]"""
    comps = []
    token = None
    while True:
        params = {"repository": repo, "pageSize": 100}
        if token:
            params["continuationToken"] = token
        resp = session.get(f"{nexus_url}/service/rest/v1/search", params=params, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        comps.extend(data.get("items", []))
        token = data.get("continuationToken")
        if not token:
            break
    return comps


def osv_query_batch(session, queries):
    """OSV querybatch：{package:{ecosystem,name}, version} -> 命中漏洞 id 列表；失败自动重试"""
    for attempt in range(3):
        try:
            resp = session.post(OSV_BATCH_URL, json={"queries": queries}, timeout=60)
            if resp.status_code == 429:
                time.sleep(5 * (attempt + 1))
                continue
            resp.raise_for_status()
            hit_ids = []
            for r in resp.json()["results"]:
                hit_ids.append([v["id"] for v in r.get("vulns", [])])
            return hit_ids
        except requests.RequestException:
            if attempt == 2:
                raise
            time.sleep(2 * (attempt + 1))
    return [[] for _ in queries]


def load_vuln_cache(cache_file):
    if cache_file.exists():
        try:
            data = json.loads(cache_file.read_text(encoding="utf-8"))
            if time.time() - data.get("ts", 0) < VULN_CACHE_DAYS * 86400:
                return data.get("vulns", {})
        except (json.JSONDecodeError, KeyError):
            pass
    return {}


def save_vuln_cache(cache_file, vulns):
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(
        json.dumps({"ts": time.time(), "vulns": vulns}, ensure_ascii=False), encoding="utf-8"
    )


def fetch_vuln(session, vuln_id):
    resp = session.get(OSV_VULN_URL.format(vuln_id), timeout=30)
    if resp.status_code == 429:
        time.sleep(3)
        resp = session.get(OSV_VULN_URL.format(vuln_id), timeout=30)
    resp.raise_for_status()
    return resp.json()


def enrich_vulns(session, vuln_ids, cache_file):
    """并发补全漏洞详情（查缓存，缺的拉取），返回 {id: vuln}"""
    cache = load_vuln_cache(cache_file)
    missing = [v for v in vuln_ids if v not in cache]
    if missing:
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
            futures = {ex.submit(fetch_vuln, session, v): v for v in missing}
            for fut in concurrent.futures.as_completed(futures):
                try:
                    cache[futures[fut]] = fut.result()
                except requests.RequestException as e:
                    print(f"    [!] 拉取漏洞 {futures[fut]} 失败：{e}")
        save_vuln_cache(cache_file, cache)
    return cache


# ---------- CVSS v3.1 base score ----------
_M_AV = {"N": 0.85, "A": 0.62, "L": 0.55, "P": 0.2}
_M_AC = {"L": 0.77, "H": 0.44}
_M_PR = {"N": 0.85, "L0": 0.62, "L1": 0.68, "H0": 0.27, "H1": 0.5}
_M_UI = {"N": 0.85, "R": 0.62}
_M_CI = {"N": 0.0, "L": 0.22, "H": 0.56}


def cvss3_base(vector):
    """CVSS:3.x/AV:N/AC:L/... -> base score（0~10）；解析失败返回 None"""
    m = {}
    for part in vector.split("/"):
        if ":" in part:
            k, v = part.split(":", 1)
            m[k] = v
    if not {"AV", "AC", "PR", "UI", "S", "C", "I", "A"} <= set(m):
        return None
    scope_changed = m["S"] == "C"
    pr_key = m["PR"] if m["PR"] == "N" else m["PR"] + ("1" if scope_changed else "0")
    impact_scope = 1 - (1 - _M_CI[m["C"]]) * (1 - _M_CI[m["I"]]) * (1 - _M_CI[m["A"]])
    if scope_changed:
        impact = 7.52 * (impact_scope - 0.029) - 3.25 * (impact_scope - 0.02) ** 15
    else:
        impact = 6.42 * impact_scope
    if impact <= 0:
        return 0.0
    exploitability = 8.22 * _M_AV[m["AV"]] * _M_AC[m["AC"]] * _M_PR[pr_key] * _M_UI[m["UI"]]
    if scope_changed:
        score = min(1.08 * (impact + exploitability), 10.0)
    else:
        score = min(impact + exploitability, 10.0)
    return round(score * 10) / 10


def severity_and_score(vuln):
    """返回 (级别, cvss_base)。级别取 GitHub database_specific.severity，
    没有则按 CVSS v3 base 折算；base 尽量一并解析用于展示。"""
    base = None
    for s in vuln.get("severity", []):
        if s.get("type") == "CVSS_V3" and s.get("score"):
            b = cvss3_base(s["score"])
            if b is not None:
                base = b
                break
    db = (vuln.get("database_specific") or {}).get("severity")
    if db and str(db).upper() in {"CRITICAL", "HIGH", "MODERATE", "LOW"}:
        return str(db).upper(), base
    if base is not None:
        lvl = "CRITICAL" if base >= 9.0 else "HIGH" if base >= 7.0 else "MODERATE" if base >= 4.0 else "LOW"
        return lvl, base
    return None, None


def _ver_key(v):
    parts = re.findall(r"\d+", v)
    return [int(p) for p in parts] if parts else [0]


def fixed_versions(vuln, pkg_name):
    """从 affected ranges 提取修复版本集合（优先匹配当前包名的条目）"""
    vers = set()
    matched = False
    for aff in vuln.get("affected", []):
        aff_name = (aff.get("package") or {}).get("name", "")
        if aff_name and aff_name != pkg_name:
            continue
        matched = True
        for rng in aff.get("ranges", []):
            for ev in rng.get("events", []):
                f = ev.get("fixed")
                if f and f not in ("*", "0"):
                    vers.add(f)
    # affected 里没匹配到当前包名时，兜底取全部 fixed
    if not vers and not matched:
        for aff in vuln.get("affected", []):
            for rng in aff.get("ranges", []):
                for ev in rng.get("events", []):
                    f = ev.get("fixed")
                    if f and f not in ("*", "0"):
                        vers.add(f)
    return sorted(vers, key=_ver_key)


def comp_pkg_name(comp, fmt):
    if fmt == "maven2":
        return f"{comp.get('group')}:{comp.get('name')}"
    return comp.get("name")


def scan():
    parser = argparse.ArgumentParser(description="Nexus 组件漏洞扫描（高危及以上）")
    parser.add_argument("--repos", help="逗号分隔的仓库名，缺省扫全部 npm/maven2 proxy 仓库")
    parser.add_argument("--out-dir", default="reports", help="报告输出目录（默认 reports/）")
    args = parser.parse_args()

    nexus_url, nexus_user, nexus_pwd = load_nexus_config()
    session = requests.Session()
    session.auth = (nexus_user, nexus_pwd)
    session.headers.update({"Accept": "application/json"})

    print(f"[*] Nexus: {nexus_url}（用户: {nexus_user}）")
    repos = get_repositories(session, nexus_url)
    if args.repos:
        wanted = set(args.repos.split(","))
        targets = [r for r in repos if r[0] in wanted and r[1] in ECOSYSTEM_BY_FORMAT]
    else:
        targets = [
            r for r in repos
            if r[1] in ECOSYSTEM_BY_FORMAT and r[2] == "proxy"
        ]
    if not targets:
        sys.exit("[!] 没有可扫描的 npm/maven2 proxy 仓库")
    print(f"[*] 目标仓库: {', '.join(r[0] for r in targets)}")
    print("[!] 注：docker 格式不在范围（镜像漏洞请用 Trivy/Grype 扫）")

    cache_file = Path(__file__).parent / ".cache" / "osv-vulns.json"
    all_hits = []   # [{repo, pkg, version, comp_id, vuln_id, level, cvss, fixed, summary, ref}]
    checked = 0
    unseen = 0

    for repo, fmt, _ in targets:
        print(f"\n[*] 扫描 {repo}（{fmt}）...")
        comps = list_components(session, nexus_url, repo)
        print(f"    组件数: {len(comps)}")
        queries, meta = [], []
        for comp in comps:
            name = comp_pkg_name(comp, fmt)
            version = comp.get("version")
            if not name or not version:
                continue
            queries.append({"package": {"ecosystem": ECOSYSTEM_BY_FORMAT[fmt], "name": name},
                            "version": version})
            meta.append((repo, name, version, comp.get("id")))
        checked += len(queries)

        vuln_ids = set()
        id2comp = {}
        for i in range(0, len(queries), OSV_BATCH_SIZE):
            batch_q = queries[i:i + OSV_BATCH_SIZE]
            batch_m = meta[i:i + OSV_BATCH_SIZE]
            results = osv_query_batch(session, batch_q)
            for m, ids in zip(batch_m, results):
                for vid in ids:
                    vuln_ids.add(vid)
                    id2comp.setdefault(vid, []).append(m)
            print(f"    批次 {i // OSV_BATCH_SIZE + 1}/{(len(queries) - 1) // OSV_BATCH_SIZE + 1} 完成")

        if not vuln_ids:
            print("    无任何漏洞命中")
            continue

        vulns = enrich_vulns(session, list(vuln_ids), cache_file)
        new_count = 0
        for vid in vuln_ids:
            v = vulns.get(vid)
            if not v:
                continue
            level, base = severity_and_score(v)
            if level not in HIGH_LEVELS:
                continue
            new_count += 1
            for repo_i, pkg, version, comp_id in id2comp[vid]:
                fixes = fixed_versions(v, pkg)
                base_str = f"{base:.1f}" if base is not None else ""
                refs = [r.get("url") for r in (v.get("references") or []) if r.get("url")]
                all_hits.append({
                    "repo": repo_i, "pkg": pkg, "version": version, "comp_id": comp_id,
                    "vuln_id": vid, "level": level, "cvss": base_str,
                    "fixed": ", ".join(fixes) or "-", "summary": v.get("summary", ""),
                    "ref": refs[0] if refs else f"https://osv.dev/vulnerability/{vid}",
                })
        print(f"    高危及以上命中: {new_count} 个漏洞")

    # ---------- 报告 ----------
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    md_path = out_dir / f"nexus漏洞扫描报告-{stamp}.md"
    csv_path = out_dir / f"nexus漏洞扫描报告-{stamp}.csv"

    by_level = {l: 0 for l in ("CRITICAL", "HIGH")}
    by_repo = {}
    for h in all_hits:
        by_level[h["level"]] = by_level.get(h["level"], 0) + 1
        by_repo[h["repo"]] = by_repo.get(h["repo"], 0) + 1

    lines = []
    lines.append(f"# Nexus 组件漏洞扫描报告（高危及以上）")
    lines.append("")
    lines.append(f"- 扫描时间：{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"- 扫描仓库：{', '.join(r[0] for r in targets)}")
    lines.append(f"- 检查组件：{checked} 个（OSV 精确版本匹配）")
    lines.append(f"- 高危及以上漏洞命中：{len(all_hits)} 条")
    lines.append(f"- 级别分布：CRITICAL {by_level.get('CRITICAL', 0)} / HIGH {by_level.get('HIGH', 0)}")
    lines.append(f"- 仓库分布：{json.dumps(by_repo, ensure_ascii=False)}")
    lines.append("")
    lines.append("> 数据源 OSV.dev（覆盖 GitHub Advisory + NVD）。报告含命中 Java/npm 组件缓存版本，")
    lines.append("> 处理动作见下文「处理建议」。")
    lines.append("")

    lines.append("## 一、漏洞清单")
    lines.append("")
    lines.append("| 级别 | 组件 | 版本 | 仓库 | 漏洞 | CVSS | 升级到 | 摘要 |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- |")
    order = {"CRITICAL": 0, "HIGH": 1}
    for h in sorted(all_hits, key=lambda x: (order.get(x["level"], 9), x["pkg"], x["version"])):
        lines.append(
            f"| {h['level']} | `{h['pkg']}` | `{h['version']}` | {h['repo']} | "
            f"[{h['vuln_id']}]({h['ref']}) | {h['cvss']} | {h['fixed']} | {h['summary'][:70]} |"
        )
    lines.append("")

    lines.append("## 二、处理建议")
    lines.append("")
    lines.append("### 2.1 研发侧（治本：升级依赖）")
    lines.append("1. 每个命中组件升级到上表「升级到」列给出的修复版本；无修复版本的先评估影响面，无法升级则记录风险接受。")
    lines.append("2. npm 项目：改 `package.json` 并重新生成 `package-lock.json`（或在项目里跑 `npm audit` 交叉核对）；")
    lines.append("   Maven 项目：改 `pom.xml` 中 `<version>` / 依赖属性版本，然后重新构建。")
    lines.append("3. 只升级到修复版本即可；报告仅覆盖 Nexus 缓存中存在的版本，升级后新版本缓存由 proxy 自动拉取。")
    lines.append("")
    lines.append("### 2.2 仓库侧（治标：清理缓存中的漏洞版本）")
    lines.append("- 上表命中组件是 Nexus 已缓存的旧版本，旧 lockfile / 老项目仍可能拉取到。可删除缓存版本（下次下载时会重新从上游拉取，")
    lines.append("  所以必须配合 2.1 的升级才能根治）：")
    lines.append("")
    lines.append("```bash")
    lines.append(f"# 逐个删除命中组件（示例，user 换成低权限只读+删除账号）")
    for h in all_hits[:5]:
        lines.append(f"curl -u {nexus_user}:**** -X DELETE {nexus_url}/service/rest/v1/components/{h['comp_id']}")
    if len(all_hits) > 5:
        lines.append(f"# ... 其余 {len(all_hits) - 5} 条见 CSV 报告中的 comp_id")
    lines.append("```")
    lines.append("")
    lines.append("- 建议在 Nexus 管理后台为上述代理仓库配 Cleanup Policy：清理『90 天未使用 + 存在高危漏洞』的旧版本，避免再次积压。")
    lines.append("- hosted 仓库（如内部发布的二方库）：按 2.1 重新发布修复版本，并通知使用方升级。")
    lines.append("")
    lines.append("### 2.3 例行复查")
    lines.append("- 建议每周执行一次（脚本对漏洞详情有 7 天缓存）：")
    lines.append("")
    lines.append("```bash")
    lines.append("30 9 * * 1 cd /home/zhaozhiwei/workspace/python/utils/nexus漏洞检测 && python3 nexus_vuln_scan.py >> reports/scan.log 2>&1")
    lines.append("```")
    lines.append("")
    lines.append("### 2.4 范围说明")
    lines.append("- 仅覆盖 npm / maven2 格式的 proxy 仓库缓存；docker 镜像漏洞请用 Trivy / Grype 对镜像做扫描。")
    lines.append("- 判定标准：GitHub Advisory 级别为 HIGH/CRITICAL，或 CVSS v3 base >= 7.0。")
    lines.append("")

    md_path.write_text("\n".join(lines), encoding="utf-8")

    with csv_path.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["repo", "pkg", "version", "comp_id", "vuln_id", "level", "cvss", "fixed", "summary", "ref"])
        w.writeheader()
        w.writerows(all_hits)

    print(f"\n{'=' * 60}")
    print("扫描完成")
    print(f"  检查组件: {checked}")
    print(f"  高危及以上命中: {len(all_hits)} 条")
    print(f"  CRITICAL: {by_level.get('CRITICAL', 0)} / HIGH: {by_level.get('HIGH', 0)}")
    for r, n in by_repo.items():
        print(f"    - {r}: {n}")
    print(f"  报告: {md_path}")
    print(f"  CSV : {csv_path}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    scan()
