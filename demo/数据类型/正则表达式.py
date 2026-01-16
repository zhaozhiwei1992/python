import re
p = re.compile('[a-z]+')
my_src = 'abcd测试'
print(p)
print(p.match(my_src))

# sub_p = p.sub('*', my_src)
def rep_fun(match):
    print(match.group(0))
    return '*'
sub_p = p.sub(rep_fun, my_src)
print(sub_p)