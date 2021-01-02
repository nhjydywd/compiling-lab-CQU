import lab2,lab1
#引入终结符表和非终结符表,以及记录语法规则的数据结构
from lab2 import WD,GN,GRAMMAR
WD.update(lab1.INST_SYMBOL)

#符号表
ST = {}#Symbol Table
#语义函数
FUN = {}

#中间代码操作符映射到汇编指令
ASM={
    WD[":"]:"li",
    WD[":="]:"move",
    WD["+"]:"add",
    WD["-"]:"sub",
    WD["*"]:"mul",
    WD["/"]:"div",
    WD["goto"]:"j",
    WD['==']:"beq",
    WD['!=']:"bne",
    WD['>']:"bgt",
    WD['>=']:"bge",
    WD['<']:"blt",
    WD['<=']:"ble",
    WD['call']:"jal",
    WD['&']:"and",
    WD['|']:"or"
}
#代码块的语义函数
def fun_代码块(node):
    code = []
    if node.rule_index == 0: #[代码块]:= ∅
        pass
    else:   #[代码块]:=[语句];
        stmtnode = node.children[0]
        caculate_attr(stmtnode)
        code += stmtnode.attrs['code']
    if node.rule_index == 2:#[代码块]:=[语句];[代码块]
        subnode = node.children[1]
        caculate_attr(subnode)
        code += subnode.attrs['code']
    node.attrs['code'] = code

#变量声明语句的语义函数
def fun_变量声明语句(node):
    type = node.children[0].children[0].symbol
    node.children[1].attrs['type'] = type
    caculate_attr(node.children[1])
    node.attrs = node.children[1].attrs
def fun_变量声明(node):
    type = node.attrs['type']
    i = node.rule_index
    if i == 0 or i == 2:#[变量声明]:= [赋值语句]
        id = node.children[0].children[0].info
    elif i == 1 or i == 3:#[变量声明]:= [标识符]
        id = node.children[0].info
    if (id in ST.keys()):
        print("{}:已存在的标识符".format(id))
        exit(-1)
    ST[id]={}
    ST[id]['type'] = type
    code = []
    if i == 0 or i == 2:#[变量声明]:=[赋值语句]|[赋值语句],[变量声明]
        caculate_attr(node.children[0])
        code += node.children[0].attrs['code']
    if i == 2 or i == 3:  # #[变量声明]:=[赋值语句],[变量声明]|[标识符],[变量声明]
        c = node.children[2]
        c.attrs['type'] = type
        caculate_attr(c)
        code += c.attrs['code']
    node.attrs['code'] = code

#赋值语句的语义函数
def fun_赋值语句(node):
    expnode = node.children[2]
    caculate_attr(expnode)
    id = node.children[0].info
    check_symbol(id)
    type = ST[id]['type']
    if type != expnode.attrs['type']:
        print("不能将 {} 型赋值给 {} 型".format(lab2.value_to_key(expnode.attrs['type'],WD)
                                        ,lab2.value_to_key(type,WD),))
        exit(-1)
    code = []
    code+=expnode.attrs['code']
    # 产生四元式   rt := rs
    rs = expnode.attrs['place']
    rt = node.children[0].info
    code.append((WD[':='],rt,rs,None))
    node.attrs['code'] = code

#算术表达式的语义函数
def fun_算术表达式(node):
    if node.rule_index == 0:#[算术表达式]:= ([算术表达式])[A]
        lnode = node.children[1]
        A = node.children[3]
    else:#[算术表达式]:= [运算数][A]
        lnode = node.children[0]
        A = node.children[1]

    caculate_attr(lnode)
    A.attrs['left'] = lnode.attrs
    caculate_attr(A) #计算A的属性
    node.attrs = A.attrs
#A的语义函数
def fun_A(node):
    lattrs = node.attrs['left']
    node.attrs['type'] = lattrs['type'] #需要一个type域标记类型
    if node.rule_index == 0:#[A]:= [运算符][算术表达式][A]
        expnode = node.children[1]  # 算术表达式结点
        caculate_attr(expnode)
        #分配汇编临时变量
        node.attrs['place'] = NewTemp()
        code = []
        code+=lattrs['code']
        code+=expnode.attrs['code']
        #产生四元式   rd := rs op rt
        op = node.children[0].children[0].symbol
        rd = node.attrs['place']
        rs = lattrs['place']
        rt = expnode.attrs['place']
        code.append((op,rs,rt,rd))
        node.attrs['code'] = code
    else:   #[A]:= ∅
        node.attrs = lattrs

#运算数的语义函数
def fun_运算数(node):
    c = node.children[0]
    node.attrs['type'] = WD['int']
    if node.rule_index == 0:#[运算数]:= [标识符]
        id = c.info
        check_symbol(id)
        node.attrs['place'] = c.info  #地址就是标识符地址
        node.attrs['code'] = []
        node.attrs['type'] = ST[id]['type'] #类型就是标识符的类型
    elif node.rule_index == 1:#[运算数]:=[整数]
        node.attrs['place'] = NewTemp()  #立即数（整数）
        imm = c.info
        rs = node.attrs['place']
        node.attrs['code'] = [(WD[":"],rs,imm,None)]
    else:#[运算数]:=[函数调用]:
        caculate_attr(c)
        node.attrs['place'] = None
        node.attrs['code'] = c.attrs['code']

#函数调用的语义函数
def fun_函数调用(node):
    op = WD['call']
    fname = node.children[0].info
    node.attrs['code'] = [(op,fname,None,None)]

#布尔表达式的语义函数
def fun_布尔表达式(node):
    if node.rule_index == 1:#[布尔表达式]:= ([布尔表达式])[B]
        lnode = node.children[1]
        B = node.children[3]
    else:#[布尔表达式]:= [布尔值][B] | ! [布尔值][B]
        lnode = node.children[0]
        B = node.children[1]

    caculate_attr(lnode)
    B.attrs['left'] = lnode.attrs
    caculate_attr(B) #计算A的属性
    node.attrs = B.attrs
    if node.rule_index == 2:    #[布尔表达式]:= ! [布尔值][B]
        assert False
#B的语义函数
def fun_B(node):
    lattrs = node.attrs['left']
    if node.rule_index == 0:#[B]:= [二元逻辑运算符][布尔表达式][B]
        assert False        #暂不支持
    else:   #[B]:= ∅
        node.attrs = lattrs
#布尔值的语义函数
def fun_布尔值(node):
    c = node.children[0]
    i = node.rule_index
    if i == 0:      #[布尔值]:= [标识符]
        id = c.info
        check_symbol(id)
        node.attrs['place'] = c.info  #地址就是标识符地址
        node.attrs['code'] = []
    elif i == 1 or i == 2:      #[布尔值]:=  true | false
        node.attrs['place'] = NewTemp()
        rs = node.attrs['place']
        boolean = 1 if i == 1 else 0
        node.attrs['code'] = [(WD[":"],rs,boolean,None)]
    else:#[布尔值]: = [关系式]
        caculate_attr(c)
        node.attrs = c.attrs
    node.attrs['type'] = WD['bool']
#关系式的语义函数
def fun_关系式(node):
    #计算左右两个表达式
    expnode1 = node.children[0]
    expnode2 = node.children[2]
    caculate_attr(expnode1)
    caculate_attr(expnode2)
    code = []
    code += expnode1.attrs['code']
    code += expnode2.attrs['code']

    #判断左右是否相等
    node.attrs['place'] = NewTemp()
    code.append((WD[':'],node.attrs['place'],1,None))
    op = node.children[1].children[0].symbol
    rs = expnode1.attrs['place']
    rt = expnode2.attrs['place']
    label = NewLabel("label")
    code += [(op, rs, rt, label),
             (WD[':'],node.attrs['place'],0,None),
             (label,None,None,None)]
    node.attrs['code'] = code

#条件语句的语义函数
def fun_条件语句(node):
    lbl_else = NewLabel("else")
    lbl_endif = NewLabel("endif")
    code = gen_if_code(node,lbl_else,lbl_endif)               #if代码段的代码
    code += [(lbl_else,None,None,None)]             #else标签
    if node.rule_index == 1:                        #带else的if语句
        elsenode = node.children[9]                 #else的代码块
        caculate_attr(elsenode)
        code += elsenode.attrs['code']
    code += [(lbl_endif,None,None,None)]
    node.attrs['code'] = code

#循环语句的语义函数
def fun_循环语句(node):
    lbl_while = NewLabel("while")
    lbl_endwhile = NewLabel("endwhile")
    code = []
    code += [(lbl_while,None,None,None)]    #while标签
    code += gen_if_code(node,lbl_endwhile,lbl_while)
    code += [(lbl_endwhile, None, None, None)]  # else标签
    node.attrs['code'] = code

#辅助函数，生成if代码段的汇编代码
def gen_if_code(node,lbl_false,goto_lbl):
    ifnode = node.children[5]     #if语句中的代码块
    boolnode = node.children[2]     #条件语句的条件
    caculate_attr(ifnode)
    caculate_attr(boolnode)
    bool_place = boolnode.attrs['place']  # 布尔值的地址
    true_place = NewTemp()
    code = []
    code += boolnode.attrs['code']
    code += [(WD[':'],true_place,1,None)]                     #将true装入临时寄存器，用于比较
    code += [(WD['!='],bool_place,true_place,lbl_false)]      #布尔值不为True，则跳到对应代码
    code += ifnode.attrs['code']                    #if的代码块
    code += [(WD['goto'],goto_lbl,None,None)]       #if结束后跳转
    return code
#∅的语义函数
def fun_empty(node):
    node.attrs['code'] = []

#缺省语义函数
def fun_default(node):
    symbol = node.symbol
    d = WD if symbol in WD.values() else GN
    #print("default function excute for node：{}-{}".format(symbol,lab2.value_to_key(symbol,d)))
    if len(node.children) == 0:
        return
    c = node.children[0]
    caculate_attr(c)
    node.attrs = c.attrs

FUN[GN['代码块']] = fun_代码块
FUN[GN['变量声明语句']] = fun_变量声明语句
FUN[GN['变量声明']] = fun_变量声明
FUN[GN['算术表达式']] = fun_算术表达式
FUN[GN['A']] = fun_A
FUN[GN['运算数']] = fun_运算数
FUN[GN['函数调用']] = fun_函数调用
FUN[GN['赋值语句']] = fun_赋值语句
FUN[GN['布尔表达式']] = fun_布尔表达式
FUN[GN['B']] = fun_B
FUN[GN['布尔值']] = fun_布尔值
FUN[GN['关系式']] = fun_关系式
FUN[GN['条件语句']] = fun_条件语句
FUN[GN['循环语句']] = fun_循环语句
FUN[WD['∅']] = fun_empty

#计算结点及其所有子结点的属性
def caculate_attr(node):
    if node.symbol in FUN.keys():
        FUN[node.symbol](node)
    else:
        fun_default(node)

#打印四元式
def print_code(node,bool_asm):
    for c in node.attrs['code']:
        if type(c[0]) == NewLabel:
            print("{}".format(c[0]))
            continue
        op = ASM[c[0]] if bool_asm else lab2.value_to_key(c[0],WD)
        if c[3] != None:
            print("{},{},{},{}".format(op,c[1],c[2],c[3]))
        elif c[2] != None:
            print("{},{},{}".format(op,c[1],c[2]))
        elif c[1] != None:
            print("{},{}".format(op, c[1]))

#检查标识符是否已声明
def check_symbol(id):
    if id not in ST.keys():
        print("{}:未被声明的标识符".format(id))
        exit(-1)

#汇编的临时变量
class NewTemp():
    def __init__(self):
        self.index = len(TEMP)
        TEMP.append(self.index)
    def __str__(self):
        return "R{}".format(self.index)
TEMP = []
class NewLabel():
    def __init__(self,name):
        if not name in LABEL.keys():
            LABEL[name] = []
        ls = LABEL[name]
        self.index = len(ls)
        self.name = name
        ls.append(self.index)
    def __str__(self):
        return "{}_{}:".format(self.name,self.index)
LABEL = {}


testStr = lab1.cStatement2
testStr = "int a =3; int a =5;"
print(testStr)
print("翻译结果：")
gt = lab2.gen_grammar_tree(testStr)
caculate_attr(gt)
print_code(gt,True)
print("\n符号表: {}".format(ST))
