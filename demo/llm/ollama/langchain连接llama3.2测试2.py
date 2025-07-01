from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langchain_core.messages.system import SystemMessage

# 参考: https://medium.com/@netanel.margalit/basic-llama-3-2-3b-tool-calling-with-langchain-and-ollama-47ad29b11f34

# @tool：这是一个装饰器，用于将下面的函数标记为工具函数，这样它们就可以被ChatOllama模型使用。
@tool
def pig_latin(phrase) -> str:
    """Returns the pig latin pronounciation of a phrase"""
    def convert_word(word) -> str:
        if word[0] in "aeiouAEIOU":
            return word + "way"
        else:
            for index, letter in enumerate(word):
                if letter in "aeiouAEIOU":
                    return word[index:] + word[:index] + "ay"
            return word + "ay"

    words = phrase.split()
    pig_latin_words = [convert_word(word) for word in words]
    return " ".join(pig_latin_words)


@tool
def reverse(phrase) -> str:
    """Return a phrase in reversed form"""
    return "".join(reversed(phrase))

tools = [pig_latin, reverse]

# 创建一个ChatOllama实例，绑定上面定义的工具函数。
model = ChatOllama(model="llama3.2:3b").bind_tools(tools)

# 定义一个包含系统消息和用户消息的列表。
messages = [
    SystemMessage("You are provided questions by the human, and the computation of the answers by tools. Give them an answer using the tool results only. Use the personality of Socrates"),
    HumanMessage("How do I to write 'love' in pig latin?"),
    HumanMessage("How do I to write 'donkey' in reverse?")
    ]

# ai_msg = model.invoke(messages)：调用ChatOllama模型的invoke方法，传入消息列表，模型将使用工具函数来回答这些问题。
ai_msg = model.invoke(messages)

# print(ai_msg.tool_calls)：打印模型在处理消息时调用的工具函数的记录。
print(ai_msg.tool_calls)

# 分别调用每个工具函数，将返回值添加到消息列表中。
for tool_call in ai_msg.tool_calls:
    selected_tool = {"pig_latin": pig_latin, "reverse": reverse}[tool_call["name"].lower()]
    tool_msg = selected_tool.invoke(tool_call)
    messages.append(tool_msg)
    print(tool_msg)

print(model.invoke(messages).content)