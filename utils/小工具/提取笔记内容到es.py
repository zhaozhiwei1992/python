from elasticsearch import Elasticsearch
import os
import re

# Elasticsearch配置
es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
index_name = 'org_notes'

# 正则表达式匹配orgmode文件中的标题和内容
title_pattern = re.compile(r'^\*+\s+(.*)$')
content_pattern = re.compile(r'\n\s*')


def parse_org_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    lines = content.split('\n')
    title = None
    body = []

    for line in lines:
        match = title_pattern.match(line)
        if match:
            # 标题行
            title = match.group(1).strip()
        else:
            # 内容行
            body.append(line.strip())

    return title, '\n'.join(body)


def index_org_files(directory):
    for root, _, files in os.walk(directory):
        for file_name in files:
            if file_name.endswith('.org'):
                file_path = os.path.join(root, file_name)
                title, content = parse_org_file(file_path)
                if title:
                    # 将标题和内容存储到Elasticsearch中
                    doc = {'title': title, 'content': content}
                    es.index(index=index_name, body=doc)
                    print(f"Indexed: {title}")


if __name__ == "__main__":
    # 指定orgmode文件所在的目录
    org_directory = '/path/to/org/files'
    index_org_files(org_directory)
