import os
from docx import Document
"""
pip install python-docx
"""

def read_docx(file_path):
    """读取docx文件内容并返回文本"""
    doc = Document(file_path)
    return '\n'.join([para.text for para in doc.paragraphs])

def process_directories(base_dir='.'):
    # 自动检测所有4位数字命名的目录
    target_dirs = [d for d in os.listdir(base_dir)
                   if os.path.isdir(os.path.join(base_dir, d))
                   and d.isdigit()
                   and len(d) == 4]

    if not target_dirs:
        print("未找到符合要求的目录（4位数字命名）")
        return

    for dir_name in target_dirs:
        dir_path = os.path.join(base_dir, dir_name)
        docx_files = [f for f in os.listdir(dir_path) if f.endswith('.docx')]

        if not docx_files:
            print(f"目录 {dir_name} 中没有docx文件")
            continue

        # 合并文件内容
        combined = []
        for filename in sorted(docx_files):  # 按文件名排序
            filepath = os.path.join(dir_path, filename)
            try:
                content = read_docx(filepath)
                # 添加文件名作为分隔标识（可选）
                combined.append(f"* 源文件: {filename}\n{content}")
            except Exception as e:
                print(f"处理文件 {filename} 时出错: {str(e)}")
                continue

        # 写入org文件
        org_filename = f"指标发版计划评审_{dir_name}.org"
        with open(org_filename, 'w', encoding='utf-8') as f:
            f.write('\n\n'.join(combined))
        print(f"已生成: {org_filename}，合并了 {len(docx_files)} 个文件")

if __name__ == '__main__':
    process_directories()