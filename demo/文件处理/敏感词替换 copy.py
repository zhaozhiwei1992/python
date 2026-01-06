import re
from typing import Dict, List, Tuple
import time
import json

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
    def replace_with_regex(self, text: str) -> str:
        """使用正则表达式进行替换（更快速）"""
        def replace_func(match):
            matched_word = match.group(0)
            return self.word_mapping.get(matched_word, matched_word)

        return self.pattern.sub(replace_func, text)

def main(arg1: str, arg2: str) -> dict:
    # 简单使用示例
    # filter_tool = SensitiveWordFilter(word_mapping={"敏感词": "***"})

    my_word_mapping = json.loads("{" + arg2 + "}")

    filter_tool = SensitiveWordFilter(word_mapping=my_word_mapping)

    print("原始文本:")
    print(arg1)
    print("\n替换后文本:")
    result = filter_tool.replace_with_regex(arg1)
    print(result)
    return {
        "result": result,
    }

if __name__ == "__main__":
    sample_text = """
    在市十二次党代会上，我们回顾了中国共产党建党100周年的辉煌历程。
    国家实验室取得了重要突破，重点人才在其中发挥了关键作用。
    长鑫公司的戴夫、宋道军和姚凯等专家做出了突出贡献。
    """

    my_word_mapping = """
        "敏感词1": "替换词1",
        "敏感词2": "***",
        "市十二次党代会": "市第12次党代会"
    """
    result = main(sample_text, my_word_mapping)
    print(result)
