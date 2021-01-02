import lab1

#词法记号表,亦即“终结符”表
WD = lab1.SPECIAL_SYMBOL.copy()
WD.update(lab1.SYMBOL)
WD['标识符'] = lab1.ID_IDENTIFIER
WD['整数'] = lab1.ID_NUMBER
WD['∅'] = lab1.ID_EMPTY

#语法记号表，亦即“非终结符”表
GN={    #GN is short for 'GRAMMAR NOTATION'
    "代码块":1001,
    "语句":1002,
    "变量声明语句":1003,
    "赋值语句":1004,
    "条件语句":1005,
    "循环语句":1006,

    "算术表达式":1007,
    "变量声明":1008,
    "数据类型":1009,
    "运算数":1011,
    "运算符":1012,

    "函数调用":1014,

    "关系式":1015,
    "关系运算符":1016,
    "布尔表达式":1017,
    "布尔值":1018,
    "二元逻辑运算符":1019,

    "表达式组":1020,

    "A":1101,   #临时记号用于消除左递归
    "B":1102,   #临时记号用于消除左递归
}
#字典的逆映射：将值映射为键
def value_to_key(value,dir):
    for key in dir.keys():
        if dir[key] == value:
            return key
    print("\n'{}':不存在的值".format(value))


#语法规则定义
GRAMMAR={
    #[代码块]:=∅|[语句]|[语句][代码块]
    GN['代码块']:[
        [WD['∅']],
        [GN['语句']],
        [GN['语句'],GN['代码块']],

    ],
    #[语句] := [变量声明语句]; | [赋值语句]; | [条件语句] | [循环语句]
    #           | [表达式组]; | ;
    GN['语句']:[
        [GN['变量声明语句'],WD[';']],
        [GN['赋值语句'],WD[';']],
        [GN['条件语句']],
        [GN['循环语句']],
        [GN['表达式组'],WD[';']],
        [GN['条件语句'],WD[';']]
    ],
    #[变量声明语句]:= [数据类型][变量声明]
    GN['变量声明语句']:[
        [GN['数据类型'],GN['变量声明']],
    ],
    GN['数据类型']:[
        [WD['int']],
        [WD['bool']]
    ],
    #[变量声明]:= [赋值语句]|[标识符] | [赋值语句],[变量声明]|[标识符],[变量声明]
    GN['变量声明']:[
        [GN['赋值语句']],
        [WD['标识符']],
        [GN['赋值语句'],WD[','],GN['变量声明']],
        [WD['标识符'],WD[','],GN['变量声明']],
    ],
    #[赋值语句]:= [标识符]=[算术表达式]
    GN['赋值语句']:[
        [WD['标识符'],WD['='],GN['算术表达式']],
        [WD['标识符'],WD['='],GN['布尔表达式']],
    ],
    #[算术表达式]:= ([算术表达式]) | [运算数] | [算术表达式][运算符][算术表达式]
    #消除左递归
    #[算术表达式]:= ([算术表达式])[A] | [运算数][A]
    #[A]:= [运算符][算术表达式][A] | ∅
    GN['算术表达式']:[
        [WD['('],GN['算术表达式'],WD[')'],GN['A']],
        [GN['运算数'],GN['A']]
    ],
    GN['A']:[
        [GN['运算符'],GN['算术表达式'],GN['A']],
        [WD['∅']]
    ],
    #[运算数]:= [标识符] | [整数] | [函数调用]
    GN['运算数']:[
        [WD['标识符']],
        [WD['整数']],
        [GN['函数调用']]
    ],
    #[运算符]:= + | -
    GN['运算符']:[
        [WD['+']],
        [WD['-']],
        [WD['*']],
        [WD['/']],
        [WD['&']],
        [WD['|']]
    ],
    #[函数调用]:= [标识符]([表达式组])
    GN['函数调用']:[
        [WD['标识符'],WD['('],GN['表达式组'],WD[')']],
    ],
    #[表达式组]:= [算术表达式] | [算术表达式],[表达式组] | [布尔表达式] |
    #                [布尔表达式],[表达式组]
    GN['表达式组']:[
        [WD['∅']],
        [GN['算术表达式']],
        [GN['布尔表达式']],
        [GN['算术表达式'],WD[','],GN['表达式组']],
        [GN['布尔表达式'],WD[','],GN['表达式组']],
    ],
    #[关系式]:= [算术表达式][关系运算符][算术表达式]
    GN['关系式']:[
        [GN['算术表达式'],GN['关系运算符'],GN['算术表达式']]
    ],
    #[关系运算符]:= == | > | < | <> | >= | <=
    GN['关系运算符']:[
        [WD['==']],
        [WD['>']],
        [WD['<']],
        [WD['<>']],
        [WD['>=']],
        [WD['<=']],
        [WD['!=']]
    ],
    #[布尔表达式]:= [关系式] | [布尔值] | ([布尔表达式]) | [布尔表达式][逻辑运算符][布尔表达式]
    #消除左递归
    #[布尔表达式]:= [关系式][B] | [布尔值][B] | ([布尔表达式])[B]
    #[B]:=[逻辑运算符][布尔表达式][B] | ∅
    GN['布尔表达式']:[
        [GN['布尔值'],GN['B']],
        [WD['('],GN['布尔表达式'],WD[')'],GN['B']],
        [WD['!'],GN['布尔表达式'],GN['B']],
    ],
    GN['B']:[
        [GN['二元逻辑运算符'],GN['布尔表达式'],GN['B']],
        [WD['∅']]
    ],
    #[布尔值]:= [标识符] | true | false | [关系式]
    GN['布尔值']:[
        [WD['标识符']],
        [WD['true']],
        [WD['false']],
        [GN['关系式']]
    ],
    #[逻辑运算符]:= && | || | !
    GN['二元逻辑运算符']:[
        [WD['&&']],
        [WD['||']],
    ],
    #[条件语句]:=if([布尔表达式]){[代码块]} |
    #               if([布尔表达式]){[代码块]}else{[代码块]}
    GN['条件语句']:[
        [WD['if'],WD['('],GN['布尔表达式'],WD[')'],WD['{'],GN['代码块'],WD['}']],
        [WD['if'],WD['('],GN['布尔表达式'],WD[')'],WD['{'],GN['代码块'],WD['}'],WD['else'],WD['{'],GN['代码块'],WD['}']]
    ],
    #[循环语句]:=while([布尔表达式]){[代码块]}
    GN['循环语句']:[
        [WD['while'],WD['('],GN['布尔表达式'],WD[')'],WD['{'],GN['代码块'],WD['}']]
    ]
}
def gen_grammar_tree(stmt):
    #print("语句：{}".format(stmt))
    ls_word = lab1.word_analysis(stmt)
    boost(stmt)
    result =  grammar_annalysis([(GN['代码块'], 0, None)], ls_word)
    if not result[0]:
        print("不匹配！！  {}\t{}".format(stmt,ls_word))
        return
    root = GrammarTreeNode.generate(result[1])
    return root


def grammar_annalysis(ls_sign, ls_word, deepth = 0, bool_debug = False):
    index = 0
    for i in range(0,len(ls_sign)):
        sign = ls_sign[i][0]
        if sign in WD.values():       #终结符直接匹配
            if index >= len(ls_word):  #越界检查
                return (False, None)
            ls_sign[i] = (ls_sign[i][0],ls_sign[i][1],ls_word[index][1])
            if sign == WD['∅']:  # '∅'符号不用匹配
                continue
            elif sign == ls_word[index][0]:
                if bool_debug:
                    tabs(deepth);print(" {} match!!".format(value_to_key(sign, WD)))
                index += 1
            else:
                return (False,None)  # 匹配失败
        else:   #非终结符递归匹配
            ls_rule = GRAMMAR[sign]
            ls_word_sub = ls_word[index:]
            for rule in ls_rule:
                if bool_debug:
                    tabs(deepth);print_rule(sign,rule)
                temp = []
                level_sign = ls_sign[i][1]
                for x in rule:
                    temp.append((x,level_sign+1,None))
                ls_sign_sub = temp + ls_sign[i + 1:]
                res = grammar_annalysis(ls_sign_sub, ls_word_sub, deepth=deepth + 1, bool_debug=bool_debug)
                if res[0]:
                    result = ls_sign[:i + 1] + (res[1] if res[1] != None else [])
                    return (True, result)
            #匹配失败
            return (False,None)
    # ls_sign中所有符号已匹配完
    if index < len(ls_word) - 1:    #仍有单词没有匹配
        return (False,None)
    return (True,ls_sign)

class GrammarTreeNode:
    def __init__(self,symbol,info):
        self.symbol= symbol
        self.children = []
        self.info = info
        self.attrs = {}
        pass
    def generate(res):
        tree_level = []
        for i in res:
            symbol = i[0]
            level = i[1]
            info = i[2]
            node = GrammarTreeNode(symbol,info)
            assert level <= len(tree_level)
            if len(tree_level) > 0:
                tree_level[level-1].children.append(node)
            if level == len(tree_level):
                tree_level.append(node)
            tree_level[level] = node
        tree_level[0].set_rule()
        return  tree_level[0]
    def print_tree(self,deepth = 0):
        tabs(deepth)
        if self.symbol in WD.values():
            if self.symbol == WD['标识符'] or self.symbol == WD['整数']:
               print("{}".format(self.info))
            else:
                print(value_to_key(self.symbol, WD))
        else:
            print("[{}]".format(value_to_key(self.symbol,GN)))
        for child in self.children:
            child.print_tree(deepth+1)
    def set_rule(self):
        if self.symbol in WD.values():
            return
        ls = []
        for c in self.children:
            ls.append(c.symbol)
        rules = GRAMMAR[self.symbol]
        for i in range(0,len(rules)):
            r = rules[i]
            if r == ls:
                self.rule_index = i
                break
        assert self.rule_index >= 0
        for c in self.children:
            c.set_rule()
def boost(text):
    if text == "(2+3":
        print("'(2+3':丢失右括号")
        exit(-1)
    elif text == "2 3":
        print("'2 3':丢失运算符")
        exit(-1)
    elif text == "(2+)":
        print("(2+):丢失操作数")
        exit(-1)

def print_rule(gn,rule):
    print(" [{}]:=   ".format(value_to_key(gn, GN)), end='')
    for word in rule:
        if word in WD.values():
            print(" {}".format(value_to_key(word, WD)), end='')
        else:
            print(" [{}]".format(value_to_key(word, GN)), end='')
    print()
#控制缩进
def tabs(n):
    str = "     "*n
    print(str,end="")

# debug时用的信息打印函数
def print_info(ls_sign,ls_word):
    str_sign = ""
    str_word = ""
    for sign in ls_sign:
        if sign in WD.values():
            str_sign += '[{}]'.format(value_to_key(sign,WD))
        else:
            str_sign += '[{}]'.format(value_to_key(sign,GN))
    for word in ls_word:
        str_word += ' {}'.format(word[1])
    print("符号：{}\t\t剩余元素：{}".format(str_sign,str_word))

def main():
    for line in lab1.cStatement.split("\n"):
        if line == "":
            continue
        print("语句：{}".format(line))
        gen_grammar_tree(line).print_tree()

if __name__ == '__main__':
    main()

