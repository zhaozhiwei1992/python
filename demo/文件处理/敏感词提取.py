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
    def replace_wait(self, text: str) -> Tuple[str, str]:
        """
        使用正则表达式进行替换，并返回替换对

        返回值:
            tuple: (替换后的文本, 替换对字符串)
        """
        replacement_pairs = []
        matched_words = set()  # 用于去重，避免重复记录相同的替换对

        def replace_func(match):
            matched_word = match.group(0)
            replacement = self.word_mapping.get(matched_word, matched_word)

            # 记录替换对（去重）
            if matched_word not in matched_words and matched_word != replacement:
                replacement_pairs.append(f'"{matched_word}"→"{replacement}"')
                matched_words.add(matched_word)

            return replacement

        result = self.pattern.sub(replace_func, text)

        # 构建替换对字符串
        pairs_str = "; ".join(replacement_pairs)

        return result, pairs_str

    # 先将敏感词value全部替换成空，防止重复替换
    def replace_text(self, text: str) -> Tuple[str, str]:
        sensitive_words = sorted(
            self.word_mapping.values(),
            key=lambda x: len(x),
            reverse=True
        )
        """构建正则表达式模式"""
        # 对敏感词进行转义，避免正则表达式特殊字符影响
        # 去掉多个*号的字符串
        sensitive_words = [word for word in sensitive_words if "*" not in word]
        escaped_words = [re.escape(word) for word in sensitive_words]
        # 创建正则表达式，使用|分隔多个模式
        pattern = re.compile('|'.join(escaped_words))

        def replace_func(match):
            matched_word = match.group(0)
            return ""

        result = pattern.sub(replace_func, text)

        return result

def main(arg1: str, arg2: str) -> dict:
    # 简单使用示例
    # filter_tool = SensitiveWordFilter(word_mapping={"敏感词": "***"})
    my_word_mapping = json.loads("{" + arg2 + "}")
    filter_tool = SensitiveWordFilter(word_mapping=my_word_mapping)

    # print("原始文本:")
    # print(arg1)

    # 将原始文本内容使用value进行替换
    arg1 = filter_tool.replace_text(arg1)
    # print("\n替换后的文本:")
    # print(arg1)

    result, replacement_pairs = filter_tool.replace_wait(arg1)

    # print("\n替换后的文本:")
    # print(result)

    if replacement_pairs:
        # print("\n替换对:")
        # print(replacement_pairs)
        return {
            "result": replacement_pairs,
        }
    else:
        # print("\n没有需要替换的敏感词")
        return {
            "result": "",
        }


if __name__ == "__main__":
    sample_text = """
    在市十二次党代会上，我们回顾了中国共产党建党100周年的辉煌历程。
    国家实验室取得了重要突破，重点人才在其中发挥了关键作用替换词1。
    长鑫公司的戴夫、宋道军和姚凯等专家做出了突出贡献替换词1。
    门要认真学习党的二十届四中全会
    """

    my_word_mapping = """
        "敏感词1": "替换词1",
        "敏感词2": "***",
        "办事实":"办实事",
        "党的二十":"党的二十大",
        "能够更好的":"能够更好地"
    """
    result = main(sample_text, my_word_mapping)
    print(result)
