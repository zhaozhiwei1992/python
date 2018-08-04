import re
regex = re.compile(r"(\d\d\d)-(\d\d\d\d)")
mc = regex.search("my phone 666-6688")
print(mc.group())
print("第一组匹配: " + mc.group(1))
print(mc.groups())

"""贪心匹配， 非贪心匹配"""
greedyRegex = re.compile(r"(Hello){3,5}")
greedyRegexMc = greedyRegex.search("HelloHelloHelloHelloHelloHello")
print(greedyRegexMc.group())

nogreedyRegex = re.compile(r"(Hello){3,5}?")
nogreedyRegexMc = nogreedyRegex.search("HelloHelloHelloHelloHelloHello")
print(nogreedyRegexMc.group())
