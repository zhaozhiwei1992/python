person={"name":"ligoudan", "sex":"男"}

print(person)

# 这个类似js语法是不支持的
# person.age=18
person['age'] = 18
#  累死java中map.keys
for k in person.keys():
    print("keys: " + k)

# python2 print(person.has_key("age"))
print(True if "age" in person.keys() else False)


for v in person.values():
    print("values: ", v)

#  类似java中 entryset
for item in person.items():
    print('完整item', item)
    print('item中key %s value %s' %(item[0], item[1]))
    # print(item[1])

