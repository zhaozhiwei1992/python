import re
from typing import Dict, List, Tuple
import time

class SensitiveWordFilter:
    def __init__(self, word_mapping = None):
        """
        初始化敏感词过滤器

        参数:
            word_mapping: 自定义敏感词映射字典，格式为 {敏感词: 替换词}
                            如果为None，则使用默认词库
        """
        # 设置默认敏感词库
        self.default_word_mapping = {
            '市十二次党代会': '市第十二次党代会',
            '中国共产党建党100周年': '中国共产党成立100周年',
            '国家实验室': '*****',
            '重点人才': '****',
            '长鑫': '**',
            '戴夫': '**',
            '宋道军': '***',
            '姚凯': '**'
        }

        # 如果传入word_mapping，则合并或覆盖默认词库
        if word_mapping is not None:
            self.word_mapping = {**self.default_word_mapping, **word_mapping}
        else:
            self.word_mapping = self.default_word_mapping.copy()

        # 对敏感词按长度降序排序，避免重叠替换问题
        self.sensitive_words = sorted(
            self.word_mapping.keys(),
            key=lambda x: len(x),
            reverse=True
        )

        # 构建正则表达式模式
        self._build_pattern()
    def _build_pattern(self):
        """构建正则表达式模式"""
        # 对敏感词进行转义，避免正则表达式特殊字符影响
        escaped_words = [re.escape(word) for word in self.sensitive_words]
        # 创建正则表达式，使用|分隔多个模式
        self.pattern = re.compile('|'.join(escaped_words))

    def replace_with_mapping(self, text: str) -> str:
        """使用映射表进行替换"""
        result = text
        for word, replacement in self.word_mapping.items():
            result = result.replace(word, replacement)
        return result

    def replace_with_regex(self, text: str) -> str:
        """使用正则表达式进行替换（更快速）"""
        def replace_func(match):
            matched_word = match.group(0)
            return self.word_mapping.get(matched_word, matched_word)

        return self.pattern.sub(replace_func, text)

    def replace_with_aho_corasick(self, text: str) -> str:
        """使用Aho-Corasick算法进行替换（适合大量敏感词）"""
        from ahocorasick import Automaton

        # 构建自动机
        automaton = Automaton()
        for idx, word in enumerate(self.sensitive_words):
            automaton.add_word(word, (idx, word))
        automaton.make_automaton()

        result_chars = list(text)
        for end_index, (idx, original_word) in automaton.iter(text):
            start_index = end_index - len(original_word) + 1
            replacement = self.word_mapping[original_word]

            # 替换敏感词
            result_chars[start_index:end_index + 1] = replacement

            # 将已替换部分填充为占位符，避免重复处理
            for i in range(start_index + len(replacement), end_index + 1):
                if i < len(result_chars):
                    result_chars[i] = '\0'

        # 清理占位符
        result = ''.join(c for c in result_chars if c != '\0')
        return result

    def fast_replace(self, text: str, method: str = 'regex') -> str:
        """
        快速替换敏感词

        参数:
            text: 待处理的文本
            method: 替换方法，可选 'regex' (默认), 'mapping', 'aho'

        返回:
            替换后的文本
        """
        if method == 'regex':
            return self.replace_with_regex(text)
        elif method == 'mapping':
            return self.replace_with_mapping(text)
        elif method == 'aho':
            return self.replace_with_aho_corasick(text)
        else:
            raise ValueError(f"不支持的替换方法: {method}")


def test_performance():
    """测试不同方法的性能"""
    filter_tool = SensitiveWordFilter()

    # 测试文本
    test_text = """
    在市十二次党代会上，我们回顾了中国共产党建党100周年的辉煌历程。
    国家实验室取得了重要突破，重点人才在其中发挥了关键作用。
    长鑫公司的戴夫、宋道军和姚凯等专家做出了突出贡献。
    这些成就是我们市十二次党代会精神的生动实践。
    """

    # 重复文本以增加测试量
    test_text = test_text * 1000

    methods = ['mapping', 'regex', 'aho']

    print("性能测试结果:")
    print("=" * 50)

    for method in methods:
        start_time = time.time()

        if method == 'aho':
            try:
                result = filter_tool.fast_replace(test_text, method=method)
            except ImportError:
                print("Aho-Corasick方法需要安装pyahocorasick库: pip install pyahocorasick")
                continue
        else:
            result = filter_tool.fast_replace(test_text, method=method)

        elapsed_time = time.time() - start_time

        # 统计替换情况
        original_words_count = sum(test_text.count(word) for word in filter_tool.sensitive_words)

        print(f"\n方法: {method.upper()}")
        print(f"处理时间: {elapsed_time:.4f}秒")
        print(f"文本长度: {len(test_text)}字符")
        print(f"检测到的敏感词数量: {original_words_count}")

        # 显示部分结果
        if method == 'regex':  # 只显示一种方法的结果示例
            print("\n替换结果示例（前200字符）:")
            print(result[:200])


def process_file(input_file: str, output_file: str, method: str = 'regex'):
    """处理文件中的敏感词"""
    filter_tool = SensitiveWordFilter()

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()

        result = filter_tool.fast_replace(content, method=method)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result)

        print(f"文件处理成功!")
        print(f"输入文件: {input_file}")
        print(f"输出文件: {output_file}")
        print(f"处理方法: {method}")

    except FileNotFoundError:
        print(f"错误: 找不到文件 {input_file}")
    except Exception as e:
        print(f"处理文件时出错: {e}")


def interactive_mode():
    """交互式模式"""
    filter_tool = SensitiveWordFilter()

    print("敏感词替换工具")
    print("=" * 50)
    print("当前敏感词库:")
    for word, replacement in filter_tool.word_mapping.items():
        print(f"  {word} -> {replacement}")
    print("=" * 50)

    while True:
        print("\n请选择操作:")
        print("1. 输入文本进行替换")
        print("2. 处理文件")
        print("3. 查看性能测试")
        print("4. 退出")

        choice = input("请输入选择 (1-4): ").strip()

        if choice == '1':
            text = input("\n请输入要处理的文本:\n")
            print("\n处理结果:")
            print("-" * 40)
            result = filter_tool.fast_replace(text, method='regex')
            print(result)
            print("-" * 40)

        elif choice == '2':
            input_file = input("请输入输入文件路径: ").strip()
            output_file = input("请输入输出文件路径: ").strip()
            process_file(input_file, output_file)

        elif choice == '3':
            test_performance()

        elif choice == '4':
            print("感谢使用，再见！")
            break

        else:
            print("无效选择，请重新输入！")


if __name__ == "__main__":
    # 简单使用示例
    # filter_tool = SensitiveWordFilter(word_mapping={"敏感词": "***"})

    my_word_mapping = {
        '敏感词1': '替换词1',
        '敏感词2': '***',
        '市十二次党代会': '市第12次党代会',  # 这会覆盖默认值
        '新增敏感词': '[已屏蔽]'
    }

    filter_tool = SensitiveWordFilter(word_mapping=my_word_mapping)

    # 示例文本
    sample_text = """
    在市十二次党代会上，我们回顾了中国共产党建党100周年的辉煌历程。
    国家实验室取得了重要突破，重点人才在其中发挥了关键作用。
    长鑫公司的戴夫、宋道军和姚凯等专家做出了突出贡献。
    """

    print("原始文本:")
    print(sample_text)
    print("\n替换后文本:")
    result = filter_tool.fast_replace(sample_text, method='regex')
    print(result)

    # 运行交互式模式
    # interactive_mode()

    # 运行性能测试
    # test_performance()