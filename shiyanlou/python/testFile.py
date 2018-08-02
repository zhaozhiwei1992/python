#/usr/bin/env python3
# name = input("please input the file name: ")
# fobj = open(name)
# for x in fobj:
#     print(x, end = ' ')
#
# fobj.close()
fobj = open("ircnicks.txt", 'w')
fobj.write('powerpork\n')
fobj.write('indrag\n')
fobj.write('mishti\n')
fobj.write('sankarshan')
fobj.close()

fobj = open("ircnicks.txt")
print(fobj.read())
fobj.close()