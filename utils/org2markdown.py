import re
import sys
import os.path
import time


TitleList = ['#', '##', '###', '####', '#####']


def GenTitle(line):
    LevelNum = -1
    for each in line:
        if each == '*':
            LevelNum = LevelNum + 1
        else:
            break
    if LevelNum >= 0:
        line = TitleList[LevelNum] + line.lstrip('*')
    return line


def parser(fnamein, fnameout):
    fin = open(fnamein, 'r')
    fout = open(fnameout, 'w')

    # ---
    # title: my_site_demo
    # date: 2018 - 06 - 23
    # 13: 13:03
    # tags:
    # ---
    fout.write("---\n")
    fout.write("title: "+os.path.basename(sys.argv[2]).split(".")[0]+"\n")
    fout.write("date: "+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+"\n")
    fout.write("tags:\n")
    fout.write("---\n")

    print("Start parsing...")
    reg = re.compile('#\+BEGIN_SRC.*|#\+END_SRC|#\+BEGIN_EXAMPLE|#\+END_EXAMPLE')
    for eachline in fin:
        if eachline[0] == '*':
            eachline = GenTitle(eachline)
        elif reg.match(eachline.lstrip()) is not None:
            eachline = "```\n"
        fout.write(eachline)
    print("Transfer finished")
    fin.close()
    fout.close()

if __name__ == "__main__":
    # org2markdown xxx.org xxx.md
    if len(sys.argv) < 3:
        print("eg org2markdown  xxx.org xxx.md")
        exit(0)
    print("=============================")
    print("Input Filename: " + sys.argv[1])
    print("Output Filename:" + sys.argv[2])
    parser(sys.argv[1], sys.argv[2])
    print("=============================")
