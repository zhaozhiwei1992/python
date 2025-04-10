import json

obj = json.loads(open("./json/data.json", "r").read())

# print(obj['arg1'])
# str = obj['arg1'].upper()
# print(str)
dataObj = json.loads(obj['arg1'])
print(dataObj)
templateText = obj['arg2'][0]['content']
print(templateText)
templateText = templateText.format(**dataObj)
print(templateText)