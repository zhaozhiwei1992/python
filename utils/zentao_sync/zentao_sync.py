#!/usr/bin/env python3
"""
禅道同步脚本 - 将禅道需求/任务/Bug 同步到 Emacs org-mode GTD
用法: python3 zentao_sync.py [--config config.json] [--offline test_data.json]
配置产品：在 config.json 的 product_ids 中添加更多产品 ID
"""

import json
import sys
import os
import urllib.request
import urllib.error
import ssl
from datetime import datetime
from pathlib import Path

# ─── 配置 ───────────────────────────────────────────────

DEFAULT_CONFIG = {
    "zentao_url": "https://10.10.101.28",
    "account_env": "ZENTAO_ACCOUNT",
    "password_env": "ZENTAO_PASSWORD",
    "output_path": os.path.expanduser("~/workspace/notes/org-notes/zentao.org"),
    "product_ids": [364],
    "execution_ids": [],
    "verify_ssl": False,
}

PRI_MAP = {1: "A", 2: "B", 3: "C", 4: "C"}

# 禅道 status/stage 中文映射
STORY_STATUS_MAP = {
    "draft": "草稿", "active": "激活", "closed": "已关闭", "changed": "已变更",
    "reviewing": "评审中",
}
STAGE_MAP = {
    "wait": "未开始", "planned": "已计划", "projected": "已立项",
    "developing": "研发中", "developed": "研发完毕", "testing": "测试中",
    "tested": "测试完毕", "verified": "已验收", "released": "已发布",
    "closed": "已关闭",
}
TASK_STATUS_MAP = {
    "wait": "未开始", "doing": "进行中", "done": "已完成",
    "closed": "已关闭", "cancel": "已取消",
}
BUG_STATUS_MAP = {
    "active": "激活", "closed": "已关闭", "resolved": "已解决",
}
BUG_SEVERITY_MAP = {
    1: "致命", 2: "严重", 3: "一般", 4: "轻微",
}

# ─── HTTP 请求 ──────────────────────────────────────────

def make_request(url, method="GET", data=None, token=None, verify_ssl=False):
    """发起 HTTP 请求"""
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Token"] = token

    body = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)

    ctx = ssl.create_default_context()
    if not verify_ssl:
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

    try:
        with urllib.request.urlopen(req, context=ctx) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.reason} - {url}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Request Error: {e} - {url}", file=sys.stderr)
        return None


def get_token(base_url, account, password, verify_ssl=False):
    """获取禅道 Token"""
    url = f"{base_url}/api.php/v1/tokens"
    resp = make_request(url, method="POST", data={"account": account, "password": password}, verify_ssl=verify_ssl)
    if resp and "token" in resp:
        return resp["token"]
    print("Failed to get token", file=sys.stderr)
    return None


# ─── 数据获取 ───────────────────────────────────────────

def get_stories(base_url, token, product_id, verify_ssl=False):
    """获取产品需求列表"""
    url = f"{base_url}/api.php/v1/products/{product_id}/stories?limit=500&status=assignedtome"
    resp = make_request(url, token=token, verify_ssl=verify_ssl)
    return resp.get("stories", []) if resp else []


def get_tasks(base_url, token, execution_id, verify_ssl=False):
    """获取执行下的任务列表"""
    url = f"{base_url}/api.php/v1/executions/{execution_id}/tasks?limit=500"
    resp = make_request(url, token=token, verify_ssl=verify_ssl)
    return resp.get("tasks", []) if resp else []


def get_bugs(base_url, token, product_id, verify_ssl=False):
    """获取产品 Bug 列表"""
    url = f"{base_url}/api.php/v1/products/{product_id}/bugs?limit=500"
    resp = make_request(url, token=token, verify_ssl=verify_ssl)
    return resp.get("bugs", []) if resp else []


def get_assigned_tasks(base_url, token, verify_ssl=False):
    """获取指派给我的任务（通过 /tasks 接口）"""
    url = f"{base_url}/api.php/v1/tasks?limit=500&type=assignedtome"
    resp = make_request(url, token=token, verify_ssl=verify_ssl)
    if resp and "tasks" in resp:
        return resp["tasks"]
    return []


# ─── 过滤逻辑 ──────────────────────────────────────────

def get_realname(person):
    """从人员对象中获取 realname"""
    if person is None:
        return ""
    if isinstance(person, dict):
        return person.get("realname", person.get("account", ""))
    return str(person)


def is_assigned_to_me(item, my_account):
    """判断是否指派给我"""
    assigned_to = item.get("assignedTo")
    if assigned_to is None:
        return False
    if isinstance(assigned_to, dict):
        return assigned_to.get("account") == my_account
    if isinstance(assigned_to, str):
        return assigned_to == my_account
    return False


def filter_stories(stories, my_account):
    """过滤需求：指派给我 且 未发布"""
    result = []
    for s in stories:
        if not is_assigned_to_me(s, my_account):
            continue
        stage = s.get("stage", "")
        status = s.get("status", "")
        # 只要未发布的
        if stage == "released" or status == "closed":
            continue
        result.append(s)
    return result


def filter_tasks(tasks, my_account):
    """过滤任务：指派给我 且 未完成"""
    result = []
    for t in tasks:
        if not is_assigned_to_me(t, my_account):
            continue
        status = t.get("status", "")
        if status in ("closed", "done", "cancel"):
            continue
        result.append(t)
    return result


def filter_bugs(bugs, my_account):
    """过滤 Bug：指派给我 且 未解决"""
    result = []
    for b in bugs:
        if not is_assigned_to_me(b, my_account):
            continue
        status = b.get("status", "")
        if status in ("closed", "resolved"):
            continue
        result.append(b)
    return result


# ─── org-mode 格式生成 ─────────────────────────────────

def format_pri(pri):
    """禅道优先级转 org 优先级"""
    return PRI_MAP.get(pri, "C")


def format_date(date_str):
    """日期格式转换: 2026-05-12T07:15:34Z -> 2026-05-12 Mon"""
    if not date_str:
        return datetime.now().strftime("%Y-%m-%d %a")
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %a")
    except Exception:
        return datetime.now().strftime("%Y-%m-%d %a")


def org_escape(text):
    """转义 org-mode 特殊字符"""
    if not text:
        return ""
    return text.replace("[", "\\[").replace("]", "\\]")


def gen_story_entry(story, base_url):
    """生成单条需求的 org 条目"""
    sid = story["id"]
    title = org_escape(story.get("title", ""))
    pri = format_pri(story.get("pri", 3))
    status = story.get("status", "")
    stage = story.get("stage", "")
    opened_by = get_realname(story.get("openedBy"))
    assigned_to = get_realname(story.get("assignedTo"))
    estimate = story.get("estimate", 0)
    opened_date = story.get("openedDate", "")

    # SCHEDULED 用 openedDate 或当天
    scheduled = format_date(opened_date) if opened_date else datetime.now().strftime("%Y-%m-%d %a")

    lines = [
        f"** TODO [#{pri}] {title}                                         :需求:禅道:",
        f"   SCHEDULED: <{scheduled}>",
        f"   :PROPERTIES:",
        f"   :ZENTAO_ID: {sid}",
        f"   :ZENTAO_TYPE: story",
        f"   :STATUS: {status}({STORY_STATUS_MAP.get(status, status)})",
        f"   :STAGE: {stage}({STAGE_MAP.get(stage, stage)})",
        f"   :ESTIMATE: {estimate}h",
        f"   :OPENED_BY: {opened_by}",
        f"   :ASSIGNED_TO: {assigned_to}",
        f"   :END:",
        f"   链接: [[{base_url}/story-view-{sid}.html][禅道#{sid}]]",
        "",
    ]
    return "\n".join(lines)


def gen_task_entry(task, base_url):
    """生成单条任务的 org 条目"""
    tid = task["id"]
    title = org_escape(task.get("name", task.get("title", "")))
    pri = format_pri(task.get("pri", 3))
    status = task.get("status", "")
    task_type = task.get("type", "")
    estimate = task.get("estimate", 0)
    consumed = task.get("consumed", 0)
    left = task.get("left", 0)
    assigned_to = get_realname(task.get("assignedTo"))
    opened_date = task.get("openedDate", "")

    scheduled = format_date(opened_date) if opened_date else datetime.now().strftime("%Y-%m-%d %a")

    lines = [
        f"** TODO [#{pri}] {title}                                         :任务:禅道:",
        f"   SCHEDULED: <{scheduled}>",
        f"   :PROPERTIES:",
        f"   :ZENTAO_ID: {tid}",
        f"   :ZENTAO_TYPE: task",
        f"   :STATUS: {status}({TASK_STATUS_MAP.get(status, status)})",
        f"   :TYPE: {task_type}",
        f"   :ESTIMATE: {estimate}h",
        f"   :CONSUMED: {consumed}h",
        f"   :LEFT: {left}h",
        f"   :ASSIGNED_TO: {assigned_to}",
        f"   :END:",
        f"   链接: [[{base_url}/task-view-{tid}.html][禅道#{tid}]]",
        "",
    ]
    return "\n".join(lines)


def gen_bug_entry(bug, base_url):
    """生成单条 Bug 的 org 条目"""
    bid = bug["id"]
    title = org_escape(bug.get("title", ""))
    pri = format_pri(bug.get("pri", 3))
    status = bug.get("status", "")
    severity = bug.get("severity", 3)
    assigned_to = get_realname(bug.get("assignedTo"))
    opened_by = get_realname(bug.get("openedBy"))
    opened_date = bug.get("openedDate", "")

    scheduled = format_date(opened_date) if opened_date else datetime.now().strftime("%Y-%m-%d %a")

    lines = [
        f"** TODO [#{pri}] {title}                                         :Bug:禅道:",
        f"   SCHEDULED: <{scheduled}>",
        f"   :PROPERTIES:",
        f"   :ZENTAO_ID: {bid}",
        f"   :ZENTAO_TYPE: bug",
        f"   :STATUS: {status}({BUG_STATUS_MAP.get(status, status)})",
        f"   :SEVERITY: {severity}({BUG_SEVERITY_MAP.get(severity, str(severity))})",
        f"   :OPENED_BY: {opened_by}",
        f"   :ASSIGNED_TO: {assigned_to}",
        f"   :END:",
        f"   链接: [[{base_url}/bug-view-{bid}.html][禅道#{bid}]]",
        "",
    ]
    return "\n".join(lines)


def generate_org(stories, tasks, bugs, base_url):
    """生成完整的 org 文件内容"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        "#+TITLE: 禅道同步待办",
        "#+OPTIONS: ^:nil toc:2",
        "#+LANGUAGE: zh-CN",
        "#+TAGS: 禅道",
        f"#+UPDATED: {now}",
        "",
    ]

    # 需求
    lines.append(f"* 需求 (共{len(stories)}条, 同步时间: [{now}])  :auto:")
    lines.append("")
    for s in sorted(stories, key=lambda x: x.get("pri", 3)):
        lines.append(gen_story_entry(s, base_url))

    # 任务
    lines.append(f"* 任务 (共{len(tasks)}条, 同步时间: [{now}])  :auto:")
    lines.append("")
    for t in sorted(tasks, key=lambda x: x.get("pri", 3)):
        lines.append(gen_task_entry(t, base_url))

    # Bug
    lines.append(f"* Bug (共{len(bugs)}条, 同步时间: [{now}])  :auto:")
    lines.append("")
    for b in sorted(bugs, key=lambda x: x.get("pri", 3)):
        lines.append(gen_bug_entry(b, base_url))

    return "\n".join(lines)


# ─── 主流程 ─────────────────────────────────────────────

def load_config(config_path):
    """加载配置文件"""
    config = DEFAULT_CONFIG.copy()
    if config_path and os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            user_config = json.load(f)
            config.update(user_config)
    return config


def sync(config):
    """执行同步"""
    base_url = config["zentao_url"].rstrip("/")
    account = os.environ.get("ZENTAO_ACCOUNT", config.get("account", ""))
    password = os.environ.get("ZENTAO_PASSWORD", config.get("password", ""))
    product_ids = config.get("product_ids", [])
    execution_ids = config.get("execution_ids", [])
    output_path = config["output_path"]
    verify_ssl = config.get("verify_ssl", False)

    # 1. 获取 Token
    print(f"[1/4] 登录禅道: {account}@{base_url}")
    token = get_token(base_url, account, password, verify_ssl)
    if not token:
        print("ERROR: 获取 Token 失败", file=sys.stderr)
        sys.exit(1)
    print(f"  Token: {token[:10]}...")

    # 2. 获取需求
    print(f"[2/4] 获取需求 (产品: {product_ids})")
    all_stories = []
    for pid in product_ids:
        stories = get_stories(base_url, token, pid, verify_ssl)
        print(f"  产品 {pid}: 获取 {len(stories)} 条需求")
        all_stories.extend(stories)

    # 3. 获取任务
    print(f"[3/4] 获取任务")
    all_tasks = []
    if execution_ids:
        for eid in execution_ids:
            tasks = get_tasks(base_url, token, eid, verify_ssl)
            print(f"  执行 {eid}: 获取 {len(tasks)} 条任务")
            all_tasks.extend(tasks)
    else:
        # 尝试通过指派给我的接口获取
        tasks = get_assigned_tasks(base_url, token, verify_ssl)
        if tasks:
            print(f"  指派给我的任务: {len(tasks)} 条")
            all_tasks.extend(tasks)

    # 4. 获取 Bug
    print(f"[4/4] 获取 Bug")
    all_bugs = []
    for pid in product_ids:
        bugs = get_bugs(base_url, token, pid, verify_ssl)
        print(f"  产品 {pid}: 获取 {len(bugs)} 条 Bug")
        all_bugs.extend(bugs)

    # 过滤
    my_stories = filter_stories(all_stories, account)
    my_tasks = filter_tasks(all_tasks, account)
    my_bugs = filter_bugs(all_bugs, account)
    print(f"\n过滤后: 需求 {len(my_stories)}, 任务 {len(my_tasks)}, Bug {len(my_bugs)}")

    # 生成 org
    org_content = generate_org(my_stories, my_tasks, my_bugs, base_url)

    # 写入文件
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(org_content)
    print(f"\n已写入: {output_path}")


def sync_offline(config, test_data_path):
    """离线模式：用测试数据生成 org 文件"""
    with open(test_data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    base_url = config["zentao_url"].rstrip("/")
    account = os.environ.get(config.get("account_env", "ZENTAO_ACCOUNT"), config.get("account", ""))
    output_path = config["output_path"]

    stories = data.get("stories", [])
    tasks = data.get("tasks", [])
    bugs = data.get("bugs", [])

    # 过滤
    my_stories = filter_stories(stories, account)
    my_tasks = filter_tasks(tasks, account)
    my_bugs = filter_bugs(bugs, account)
    print(f"过滤后: 需求 {len(my_stories)}, 任务 {len(my_tasks)}, Bug {len(my_bugs)}")

    # 生成
    org_content = generate_org(my_stories, my_tasks, my_bugs, base_url)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(org_content)
    print(f"已写入: {output_path}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="禅道同步到 Emacs GTD")
    parser.add_argument("--config", "-c", default="/home/zhaozhiwei/workspace/python/utils/zentao_sync/config.json",
                        help="配置文件路径")
    parser.add_argument("--offline", "-o", default=None,
                        help="离线模式，使用本地 JSON 测试数据")
    args = parser.parse_args()

    config = load_config(args.config)

    if args.offline:
        sync_offline(config, args.offline)
    else:
        account = os.environ.get("ZENTAO_ACCOUNT", config.get("account", ""))
        password = os.environ.get("ZENTAO_PASSWORD", config.get("password", ""))
        if not account or not password:
            print("ERROR: 请设置环境变量 ZENTAO_ACCOUNT 和 ZENTAO_PASSWORD", file=sys.stderr)
            print("  或在 config.json 中设置 account/password 字段", file=sys.stderr)
            sys.exit(1)
        sync(config)


if __name__ == "__main__":
    main()
