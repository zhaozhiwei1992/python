#!/usr/bin/env python3
"""
将 Markdown 格式的 .org 文件转换为 Org Mode 格式
"""
import re
import sys
from pathlib import Path
from datetime import datetime


def parse_frontmatter(content):
    """解析 Markdown 的 frontmatter"""
    lines = content.split('\n')
    if lines[0] != '---':
        return None, content

    # 找到结束的 ---
    end_idx = None
    for i in range(1, len(lines)):
        if lines[i] == '---':
            end_idx = i
            break

    if end_idx is None:
        return None, content

    # 解析 frontmatter
    frontmatter_lines = lines[1:end_idx]
    content_lines = lines[end_idx+1:]

    frontmatter = {}
    for line in frontmatter_lines:
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            # 处理列表值
            if key in ['tag', 'tags']:
                if value.startswith('[') and value.endswith(']'):
                    # YAML 数组格式
                    value = value[1:-1].split(',')
                elif value.startswith('- '):
                    # YAML 列表格式（多行）
                    value = [v.strip() for v in frontmatter_lines if v.strip().startswith('- ')]
                else:
                    value = [v.strip() for v in value.split(',')]
                frontmatter['tags'] = value
            else:
                frontmatter[key] = value

    # 剩余内容
    remaining_content = '\n'.join(content_lines)

    return frontmatter, remaining_content


def convert_frontmatter_to_org(frontmatter):
    """将 frontmatter 转换为 Org Mode 格式"""
    org_lines = []

    if 'title' in frontmatter:
        org_lines.append(f"#+TITLE: {frontmatter['title']}")

    if 'category' in frontmatter:
        org_lines.append(f"#+CATEGORY: {frontmatter['category']}")

    if 'tags' in frontmatter:
        tags = frontmatter['tags']
        if isinstance(tags, list):
            org_lines.append(f"#+TAGS: {','.join(tags)}")
        else:
            org_lines.append(f"#+TAGS: {tags}")

    if 'date' in frontmatter:
        org_lines.append(f"#+DATE: {frontmatter['date']}")

    return org_lines


def convert_headings(content):
    """转换 Markdown 标题为 Org Mode 标题"""
    lines = content.split('\n')
    converted_lines = []

    for line in lines:
        # 匹配 Markdown 标题：## 或 ### 等
        match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if match:
            level = len(match.group(1))
            text = match.group(2)
            # 转换为 Org 标题：* 级别
            org_heading = '*' * (level) + ' ' + text
            converted_lines.append(org_heading)
        else:
            converted_lines.append(line)

    return '\n'.join(converted_lines)


def convert_code_blocks(content):
    """转换 Markdown 代码块为 Org Mode 代码块"""
    # 匹配 ```language 或 ````language
    pattern = r'```(\w+)?\n(.*?)\n```'
    matches = list(re.finditer(pattern, content, re.DOTALL))

    if not matches:
        return content

    result = []
    last_pos = 0

    for match in matches:
        # 添加代码块之前的内容
        result.append(content[last_pos:match.start()])

        lang = match.group(1) if match.group(1) else ''
        code = match.group(2)

        # 转换为 Org 代码块
        if lang:
            result.append(f'#+BEGIN_SRC {lang}\n{code}\n#+END_SRC')
        else:
            result.append(f'#+BEGIN_EXAMPLE\n{code}\n#+END_EXAMPLE')

        last_pos = match.end()

    # 添加最后的内容
    result.append(content[last_pos:])

    return ''.join(result)


def convert_inline_code(content):
    """转换行内代码 `code` 为 =code="""
    content = re.sub(r'`([^`]+)`', r'=\1=', content)
    return content


def convert_images(content):
    """转换 Markdown 图片为 Org 模式"""
    # ![alt text](url)
    pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
    result = re.sub(pattern, r'[[\2][\1]]', content)
    return result


def convert_links(content):
    """转换 Markdown 链接为 Org 模式"""
    # [text](url)
    pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    result = re.sub(pattern, r'[[\2][\1]]', content)
    return result


def convert_bold(content):
    """转换粗体 **text** 为 *text*"""
    # 逐行处理，跳过 Org 标题行（以 * 开头）
    lines = content.split('\n')
    converted_lines = []

    for line in lines:
        stripped = line.lstrip()
        # 跳过 Org 标题（行首有连续的 *）
        if stripped.startswith('*') and len(stripped) > 0 and stripped[0] == '*':
            converted_lines.append(line)
        else:
            # 替换行内的粗体
            converted = re.sub(r'\*\*([^*]+)\*\*', r'*\1*', line)
            converted_lines.append(converted)

    return '\n'.join(converted_lines)


def convert_italic(content):
    """转换斜体 *text* 为 /text/"""
    # 注意：要避免转换 Org 标题中的 *
    # 方法：在行首的 * 不处理（已经是 Org 标题）
    lines = content.split('\n')
    converted_lines = []

    for line in lines:
        # 如果是 Org 标题（行首是 *），跳过
        if line.lstrip().startswith('*'):
            converted_lines.append(line)
        else:
            # 替换行内的斜体
            converted = re.sub(r'\*([^*]+)\*', r'/\1/', line)
            converted_lines.append(converted)

    return '\n'.join(converted_lines)


def convert_lists(content):
    """转换列表为 Org 模式（可选，Org 模式也支持 - 和 1.）"""
    # Markdown 和 Org 模式列表格式基本兼容
    # 可以不做转换
    return content


def convert_blockquotes(content):
    """转换引用块 > 为 Org 模式"""
    lines = content.split('\n')
    converted_lines = []

    for line in lines:
        # 匹配以 > 开头的引用
        if line.startswith('>'):
            # 转换为 Org 模式：#+BEGIN_QUOTE
            converted_lines.append(f'#+BEGIN_QUOTE')
            # 去掉 > 前缀，并去掉多余空格
            quoted_text = line[1:].strip()
            converted_lines.append(quoted_text)
        else:
            converted_lines.append(line)

    return '\n'.join(converted_lines)


def remove_html_comments(content):
    """移除 HTML 注释"""
    content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
    return content


def clean_html_tags(content):
    """清理简单的 HTML 标签"""
    # 移除 <p> 标签但保留内容
    content = re.sub(r'<p[^>]*>(.*?)</p>', r'\1\n', content, flags=re.DOTALL)
    # 移除其他自闭合标签（<br/> 等）
    content = re.sub(r'<br\s*/?>', '\n', content)
    # 移除其他简单的 HTML 标签
    content = re.sub(r'<(/?\w+)[^>]*>', '', content)
    return content


def convert_markdown_to_org(content):
    """完整的 Markdown 到 Org Mode 转换"""
    # 1. 解析 frontmatter
    frontmatter, content = parse_frontmatter(content)

    # 2. 转换 content
    content = remove_html_comments(content)
    content = convert_code_blocks(content)
    content = convert_headings(content)
    content = convert_images(content)
    content = convert_links(content)
    content = convert_bold(content)
    content = convert_italic(content)
    content = convert_inline_code(content)
    content = convert_blockquotes(content)
    content = clean_html_tags(content)

    # 3. 添加 Org frontmatter
    if frontmatter:
        org_frontmatter = convert_frontmatter_to_org(frontmatter)
        org_frontmatter.extend(['', ''])  # 添加空行
        content = '\n'.join(org_frontmatter) + content

    return content


def convert_file(filepath):
    """转换单个文件"""
    print(f"处理文件: {filepath}")

    try:
        # 读取原始内容
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查是否是 Markdown 格式
        if not content.startswith('---'):
            print(f"  → 跳过：不是 Markdown 格式")
            return False

        # 转换
        org_content = convert_markdown_to_org(content)

        # 写入
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(org_content)

        print(f"  ✅ 转换完成")
        return True

    except Exception as e:
        print(f"  ❌ 转换失败: {e}")
        return False


def find_markdown_files(notes_dir):
    """查找所有 Markdown 格式的 .org 文件"""
    markdown_files = []

    # 查找以 --- 开头的 .org 文件
    for filepath in Path(notes_dir).rglob('*.org'):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                if first_line == '---':
                    # 排除专门的 Markdown 教程文件
                    if 'markdown' not in filepath.name.lower():
                        markdown_files.append(filepath)
        except:
            continue

    return sorted(markdown_files)


def main():
    notes_dir = "/home/zhaozhiwei/Documents/notes"

    print("=== Markdown 到 Org Mode 转换工具 ===\n")

    # 查找所有 Markdown 格式的文件
    print("正在查找 Markdown 格式的 .org 文件...")
    markdown_files = find_markdown_files(notes_dir)

    if not markdown_files:
        print("未找到需要转换的文件")
        return

    print(f"找到 {len(markdown_files)} 个 Markdown 格式的 .org 文件\n")

    # 显示将要转换的文件列表
    print("文件列表：")
    for i, filepath in enumerate(markdown_files, 1):
        rel_path = filepath.relative_to(notes_dir)
        print(f"  {i}. {rel_path}")

    print(f"\n即将转换 {len(markdown_files)} 个文件...")
    print("-" * 50)

    # 统计
    success_count = 0
    fail_count = 0

    # 逐个转换
    for filepath in markdown_files:
        if convert_file(filepath):
            success_count += 1
        else:
            fail_count += 1
        print()

    # 汇总
    print("=" * 50)
    print(f"转换完成！")
    print(f"  ✅ 成功: {success_count}")
    print(f"  ❌ 失败: {fail_count}")
    print(f"  📊 总计: {len(markdown_files)}")


if __name__ == '__main__':
    main()
