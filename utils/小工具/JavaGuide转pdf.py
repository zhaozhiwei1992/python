#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
JavaGuide Markdown to PDF Converter
This script converts all Markdown files in the docs directory
to a single PDF file with a Chinese table of contents.
"""

import os
import re
import glob
import argparse
from pathlib import Path
import logging
from collections import defaultdict

# Required libraries - install with pip
try:
    import markdown
    from xhtml2pdf import pisa
    from bs4 import BeautifulSoup
    from tqdm import tqdm
except ImportError:
    print("Please install required packages:")
    print("pip install markdown xhtml2pdf beautifulsoup4 tqdm")
    exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class JavaGuidePdfConverter:
    def __init__(self, docs_path, output_path, exclude_dirs=None):
        self.docs_path = os.path.abspath(docs_path)
        self.output_path = output_path
        self.exclude_dirs = exclude_dirs or [".vuepress", "snippets", "__pycache__", ".git"]
        self.toc = []
        self.html_content = []
        self.file_count = 0

        # Style for the PDF
        self.css = """
        <style>
            @font-face {
                font-family: 'NotoSansSC';
                src: url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;700&display=swap');
            }
            body {
                font-family: 'NotoSansSC', Arial, sans-serif;
            }
            h1, h2, h3, h4, h5, h6 {
                font-family: 'NotoSansSC', Arial, sans-serif;
                color: #333;
                margin-top: 24px;
                margin-bottom: 16px;
                font-weight: 600;
                line-height: 1.25;
            }
            h1 { font-size: 2em; border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }
            h2 { font-size:
 1.5em; border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }
            h3 { font-size: 1.25em; }
            h4 { font-size: 1em; }
            h5 { font-size: 0.875em; }
            h6 { font-size: 0.85em; color: #6a737d; }
            pre {
                background-color: #f6f8fa;
                border-radius: 3px;
                font-size: 85%;
                line-height: 1.45;
                overflow: auto;
                padding: 16px;
            }
            code {
                background-color: rgba(27, 31, 35, 0.05);
                border-radius: 3px;
                font-size: 85%;
                margin: 0;
                padding: 0.2em 0.4em;
                font-family: Consolas, "Liberation Mono", Menlo, Courier, monospace;
            }
            pre > code {
                background-color: transparent;
                border: 0;
                display: inline;
                line-height: inherit;
                margin: 0;
                overflow: visible;
                padding: 0;
            }
            blockquote {
                border-left: 4px solid #dfe2e5;
                color: #6a737d;
                padding: 0 1em;
                margin: 0 0 16px 0;
            }
            table {
                border-collapse: collapse;
                border-spacing: 0;
                display: block;
                overflow: auto;
                width: 100%;
            }
            table th {
                font-weight: 600;
                padding: 6px 13px;
                border: 1px solid #dfe2e5;
            }
            table td {
                padding: 6px 13px;
                border: 1px solid #dfe2e5;
            }
            table tr {
                background-color: #fff;
                border-top: 1px solid #c6cbd1;
            }
            table tr:nth-child(2n) {
                background-color: #f6f8fa;
            }
            img {
                max-width: 100%;
                height: auto;
            }
            .toc {
                background-color: #f8f9fa;
                border: 1px solid #a2a9b1;
                padding: 15px;
                margin-bottom: 20px;
                border-radius: 5px;
            }
            .toc-title {
                font-size: 1.5em;
                font-weight: bold;
                margin-bottom: 10px;
                text-align: center;
            }
            .toc-list {
                list-style-type: none;
                padding-left: 20px;
            }
            .toc-list-item {
                margin-bottom: 8px;
            }
            .toc-level-1 { margin-left: 0; }
            .toc-level-2 { margin-left: 20px; }
            .toc-level-3 { margin-left: 40px; }
            .toc-level-4 { margin-left: 60px; }
            .toc-level-5 { margin-left: 80px; }
            .toc-level-6 { margin-left: 100px; }
            a {
                color: #0366d6;
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }
            @page {
                size: A4;
                margin: 1cm;
                @frame footer {
                    -pdf-frame-content: footerContent;
                    bottom: 0cm;
                    margin-left: 1cm;
                    margin-right: 1cm;
                    height: 1cm;
                }
            }
        </style>
        """

    def generate_filename_to_title_map(self):
        """Generate a mapping of filenames to their original titles"""
        filename_to_title = {}
        for root, dirs, files in os.walk(self.docs_path):
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
            for file in files:
                if file.endswith('.md'):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # Try to extract title from first heading
                            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
                            if title_match:
                                title = title_match.group(1).strip()
                            else:
                                # Use filename as fallback
                                title = os.path.splitext(file)[0].replace('-', ' ').title()

                            # Store relative filepath and title
                            rel_path = os.path.relpath(filepath, self.docs_path)
                            filename_to_title[rel_path] = title
                    except Exception as e:
                        logger.error(f"Error processing {filepath}: {e}")

        return filename_to_title

    def convert_md_to_html(self, md_content, file_path=''):
        """Convert markdown content to HTML"""
        # Create Markdown instance with extensions
        md = markdown.Markdown(extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.toc',
            'markdown.extensions.tables',
            'markdown.extensions.fenced_code'
        ])

        # Convert Markdown to HTML
        html = md.convert(md_content)

        # Parse HTML with BeautifulSoup to fix image paths
        soup = BeautifulSoup(html, 'html.parser')

        # Fix image paths
        if file_path:
            dir_path = os.path.dirname(file_path)
            for img in soup.find_all('img'):
                src = img.get('src', '')
                if src and not src.startswith(('http://', 'https://', '/')):
                    # Make path relative to the current markdown file
                    full_img_path = os.path.normpath(os.path.join(dir_path, src))
                    # Check if image exists, if not, set a placeholder
                    if not os.path.exists(full_img_path):
                        img['src'] = ''
                        img['alt'] = f"[Image not found: {src}]"
                    else:
                        img['src'] = full_img_path

        return str(soup)

    def build_toc_tree(self):
        """Build a hierarchical table of contents"""
        logger.info("Building table of contents...")

        # Generate mapping of filenames to titles
        filename_to_title = self.generate_filename_to_title_map()

        # Create a directory structure
        dir_structure = defaultdict(list)

        for file_path, title in filename_to_title.items():
            dir_name = os.path.dirname(file_path)
            dir_structure[dir_name].append((file_path, title))

        # Create TOC HTML
        toc_html = ['<div class="toc">',
                    '<div class="toc-title">目录</div>',
                    '<ul class="toc-list">']

        # Sort directories for consistent ordering
        sorted_dirs = sorted(dir_structure.keys())

        for dir_name in sorted_dirs:
            # Skip empty directory name (root level files)
            if dir_name:
                # Get directory display name
                display_name = os.path.basename(dir_name).replace('-', ' ').title()
                toc_html.append(f'<li class="toc-list-item toc-level-1"><strong>{display_name}</strong></li>')
                toc_html.append('<ul>')

            # Sort files within directory
            sorted_files = sorted(dir_structure[dir_name], key=lambda x: x[0])

            for file_path, title in sorted_files:
                file_id = re.sub(r'[^a-zA-Z0-9]', '-', file_path)
                toc_html.append(f'<li class="toc-list-item toc-level-2"><a href="#{file_id}">{title}</a></li>')

            if dir_name:
                toc_html.append('</ul>')

        toc_html.append('</ul>')
        toc_html.append('</div>')

        return '\n'.join(toc_html)

    def process_markdown_files(self):
        """Process all markdown files"""
        logger.info(f"Processing Markdown files in {self.docs_path}...")

        all_md_files = []

        # First, collect all markdown files
        for root, dirs, files in os.walk(self.docs_path):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]

            for file in files:
                if file.endswith('.md'):
                    filepath = os.path.join(root, file)
                    all_md_files.append(filepath)

        # Sort files for consistent ordering
        all_md_files.sort()
        self.file_count = len(all_md_files)

        # Process each file
        content_sections = []

        for filepath in tqdm(all_md_files, desc="Converting files"):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    md_content = f.read()

                # Skip empty files
                if not md_content.strip():
                    continue

                # Convert MD to HTML
                html = self.convert_md_to_html(md_content, filepath)

                # Create section with file ID for linking from TOC
                relative_path = os.path.relpath(filepath, self.docs_path)
                file_id = re.sub(r'[^a-zA-Z0-9]', '-', relative_path)

                # Extract title from first heading or use filename
                title_match = re.search(r'^#\s+(.+)$', md_content, re.MULTILINE)
                if title_match:
                    title = title_match.group(1).strip()
                else:
                    title = os.path.splitext(os.path.basename(filepath))[0].replace('-', ' ').title()

                section = f'<div id="{file_id}" class="document-section">'
                section += f'<h1>{title}</h1>'
                section += html
                section += '</div>'
                section += '<div style="page-break-after: always;"></div>'

                content_sections.append(section)

            except Exception as e:
                logger.error(f"Error processing {filepath}: {e}")

        # Combine all HTML content
        self.html_content = content_sections

        return self.file_count

    def create_pdf(self):
        """Create the final PDF file"""
        logger.info(f"Creating PDF at {self.output_path}...")

        # Generate table of contents
        toc_html = self.build_toc_tree()

        # Combine all content
        html_content = f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <title>JavaGuide</title>
            {self.css}
        </head>
        <body>
            <h1 style="text-align:center;">JavaGuide</h1>
            {toc_html}
            <div style="page-break-after: always;"></div>
            {''.join(self.html_content)}
            <div id="footerContent" style="text-align: center; font-size: 10px;">
                <span>JavaGuide PDF | 第 <pdf:pagenumber> 页</span>
            </div>
        </body>
        </html>
        """

        # Convert HTML to PDF
        with open(self.output_path, "wb") as output_file:
            pisa_status = pisa.CreatePDF(
                html_content,
                dest=output_file,
                encoding='utf-8'
            )

        # Return True if PDF creation was successful
        return pisa_status.err == 0

def main():
    """Main function to run the converter"""
    parser = argparse.ArgumentParser(description='Convert JavaGuide Markdown files to a single PDF')
    parser.add_argument('--docs', default='docs', help='Path to the docs directory')
    parser.add_argument('--output', default='JavaGuide.pdf', help='Output PDF path')
    parser.add_argument('--exclude', nargs='*', help='Directories to exclude')
    args = parser.parse_args()

    logger.info("Starting JavaGuide Markdown to PDF conversion")

    # Create converter instance
    converter = JavaGuidePdfConverter(
        docs_path=args.docs,
        output_path=args.output,
        exclude_dirs=args.exclude
    )

    # Process Markdown files
    file_count = converter.process_markdown_files()

    if file_count > 0:
        # Create PDF
        success = converter.create_pdf()

        if success:
            logger.info(f"Successfully created PDF at {args.output}")
            logger.info(f"Processed {file_count} Markdown files")
        else:
            logger.error("Failed to create PDF")
    else:
        logger.warning("No Markdown files found to process")

if __name__ == "__main__":
    main()

"""
# JavaGuide Markdown to PDF 转换器

这个Python脚本可以将JavaGuide项目中的所有Markdown文件转换为一个单独的PDF文件，并提供中文目录。

## 功能特点

- 将docs目录下所有Markdown文件合并为一个PDF文件
- 自动生成带有层次结构的中文目录
- 保留原始文档的标题结构和格式
- 支持Markdown的大部分常用语法
- 包含页码和页脚
- 自动处理图片路径

## 安装依赖

在使用此脚本之前，请确保已安装所需的Python库：

```bash
pip install markdown xhtml2pdf beautifulsoup4 tqdm
```

## 使用方法

### 基本用法

```bash
python md_to_pdf_converter.py
```

这将使用默认设置，将`docs`目录中的Markdown文件转换为名为`JavaGuide.pdf`的PDF文件。

### 高级选项

```bash
python md_to_pdf_converter.py --docs <文档目录路径> --output <输出PDF路径> --exclude <要排除的目录>
```

参数说明:
- `--docs`: 指定Markdown文档所在的目录 (默认: "docs")
- `--output`: 指定输出PDF文件的路径 (默认: "JavaGuide.pdf")
- `--exclude`: 指定需要排除的目录 (可以指定多个)

### 示例

将自定义目录转换为PDF：
```bash
python md_to_pdf_converter.py --docs ./my_docs --output MyJavaGuide.pdf
```

排除某些目录：
```bash
python md_to_pdf_converter.py --exclude .vuepress snippets
```

## 目录结构

转换后的PDF将保持文档的层次结构，目录按照以下层次组织：
1. 顶层是目录名称
2. 二级是该目录下的文件，按文件名字母顺序排列

## 故障排除

- 如果遇到中文显示问题，请确保系统已安装中文字体
- 如果图片无法显示，检查图片路径是否正确，或者图片是否实际存在
- 对于特别大的文档集合，可能需要较长的处理时间和较大的内存

## 限制

- PDF生成使用xhtml2pdf库，可能不支持某些复杂的Markdown格式
- 某些特殊的HTML元素可能不会正确渲染
- 非常大的文档集合可能导致内存问题

## 许可

此脚本按原样提供，可自由使用和修改。 
"""

"""
markdown==3.4.4
xhtml2pdf==0.2.11
beautifulsoup4==4.12.2
tqdm==4.66.1 
"""