import re

#用于测试的C语言语句
cStatement = \
    "int a;\n" \
    "int a,b;\n" \
    "int a = 1;\n" \
    "a = b + 1;\n" \
    "a = b + c;\n" \
    "a = 1;\n" \
    "a = (b==c);\n" \
    "a = (b>c);\n" \
    "a = (b<c);\n" \
    "a = (b&&c);\n" \
    "a = (b||c);\n"\
    "a = (!b);\n" \
    "if(a==b){};\n" \
    "while(a==b){};\n" \
    "get(a);\n" \
    "put(a);\n" \

cStatement2 = \
    "int num1,num2,op,ans;\n" \
    "get(num1,num2,op);\n" \
    "if(op==0)\n" \
    "{\n"\
        "ans = num1 + num2;\n"\
    "};\n"\
    "if(op==1)\n"\
    "{\n"\
        "ans = num1 - num2;\n"\
    "};\n"\
    "if(op==2)\n"\
    "{\n"\
        "ans = num1 & num2;\n"\
    "};\n"\
    "if(op==3)\n"\
    "{\n"\
        "ans = num1 | num2;\n"\
    "};\n"\
    "put(ans);\n"\

cStatement3 = \
    "int num0,num1,out,op;\n"\
    "num1 = 3333;\n"\
    "num2 = 6666;\n"\
    "num3 = 9999;\n"\
    "op = 1;\n"\
    "while(op>0)\n"\
    "{\n"\
        "if(op==1)\n"\
    "{\n"\
         "out = num1;\n"\
    "};\n"\
    "if(op==2)\n"\
    "{\n"\
         "out = num2;\n"\
    "};\n"\
    "if(op==2)\n"\
    "{\n"\
         "out = num3;\n"\
    "};\n"\
    "put(out);\n"\
    "get(op);\n"\
    "};\n"\

#定义语法符号
SYMBOL = {"for":1,
          "if":2,
          "then":3,
          "else":4,
          "while":5,
          "do":6,
          "true":7,
          "false":8,
          "void":101,
          "int":102,
          "bool":103,
          }
#定义特殊符号
#与上面的区别在于不能包含在标识符中。
#例如对于符号"for"和符号"+"："afor"是合法标识符，但"a+"不是合法标识符
SPECIAL_SYMBOL = {
          "+":13,
          "-":14,
          "*":15,
          "/":16,
          ":":17,
          ":=":18,
          "<":20,
          "<>":21,
          "<=":22,
          ">":23,
          ">=":24,
          "=":25,
          ";":26,
          "(":27,
          ")":28,
          "[":29,
          "]":30,
          "{":31,
          "}":32,
          ",":33,
          "&&":34,
          "||":35,
          "!":36,
          "==":37,
          "#":38,
          "&":39,
          "|":40,
          "!=":41,
}

#将长度为2的特殊符号单独处理
#这是为了解决“前缀问题”
#例如符号“=”是符号“==”的前缀，如果不做特殊处理，会导致无法正确识别二者。
SET_2_LEN_SPECIAL_SYMBOL = set()
for key in SPECIAL_SYMBOL.keys():
    if len(key)>=2:
        SET_2_LEN_SPECIAL_SYMBOL.add(key)

ID_IDENTIFIER = 10  #标识符的记号
ID_NUMBER = 11      #数字的记号
ID_EMPTY = 12       #空记号

#指令记号定义，供实验4使用
INST_SYMBOL = {
    "call":90,
    "goto":91
}


#提取单词，处理每个单词
def word_analysis(stmt,bool_print = False):
    ls_line = re.split("[\n]",stmt)
    while("" in ls_line):
        ls_line.remove("")
    ls_result = []
    for i in range(0,len(ls_line)):
        ls_symbol = split_symbol(ls_line[i])
        print_info = ""
        #输出每一个符号对应的词法记号
        for symbol in ls_symbol:
            id = -1
            if  symbol in SYMBOL.keys():
                id = SYMBOL[symbol]
            elif symbol in SPECIAL_SYMBOL.keys():
                id = SPECIAL_SYMBOL[symbol]
            elif is_identifier(symbol):
                id = ID_IDENTIFIER
            elif is_number(symbol):
                id = ID_NUMBER
            else:
                #词法分析检测到非法输入，打印出错信息
                print("\n line {0} error：'{1}' 既不是一个合法的标识符，也不是一个合法的数字。".format(i,symbol))
                return []
            ls_result.append((id,symbol))
            print_info += "({0}, '{1}')".format(id,symbol)
        if(bool_print):
            print(ls_line[i])
            print(print_info)
    return ls_result

def main():
    s = cStatement2
    while True:
        print("\n词法分析的测试输出结果如下：")
        word_analysis(s,bool_print=True)
        s = input("\n请输入要进行词法分析的C语言语句：")

#分离记号，例如对于(a+b)，分离为5元列表：[(,a,+,b,)]
def split_symbol(line):
    ls_word = re.split(" ", line)
    ls_result = []
    for word in ls_word:
        ls_result += split_symbol_recursion(word)
    return ls_result

def split_symbol_recursion(word):
    if word == "":
        return []
    #当前单词是符号，直接返回
    if word in SYMBOL.keys() or word in SPECIAL_SYMBOL.keys():
        return [word,]
    else:
        #判断当前单词是否包含特殊符号
        #优先匹配2长度的特殊符号
        for symbol in SET_2_LEN_SPECIAL_SYMBOL:
            # 如果包含特殊符号，就要对符号两侧递归解析并返回
            if symbol in word:
                ls = devide_word(word,symbol)
                return split_symbol_recursion(ls[0])+[symbol,]+split_symbol_recursion(ls[1])
        for symbol in SPECIAL_SYMBOL.keys():
            #如果包含特殊符号，就要对符号两侧递归解析并返回
            if symbol in word:
                ls = devide_word(word,symbol)
                return split_symbol_recursion(ls[0])+[symbol,]+split_symbol_recursion(ls[1])
        #不包含特殊符号，则认为是标识符或数字，直接返回
        return [word,]

def devide_word(word,symbol):
    ls = word.split(symbol)
    tail = ""
    for i in range(1,len(ls)):
        tail += ls[i]
        if i < len(ls) - 1:
            tail += symbol
    return [ls[0],tail]

def is_identifier(symbol):
    #必须是字母开头
    if not char_is_letter(symbol[0]):
        return False
    for i in range(0,len(symbol)):
        #后续字符必须是字母或数字
        if (not char_is_letter(symbol[i])) and (not char_is_number(symbol[i])):
            return False
    return True;

def is_number(symbol):
    for i in range(0,len(symbol)):
        #必须是数字
        if not char_is_number(symbol[i]):
            return False
    return True;

def char_is_letter(char):
    return (char >= 'a' and char <= 'z') or (char >= 'A' and char <= 'Z')

def char_is_number(char):
    return (char >= '0' and char <= '9')



if __name__ == "__main__":
    main()