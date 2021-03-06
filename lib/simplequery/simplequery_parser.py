
# Lex
tokens = (
    'BUILDIN',
    'NAME',
    'FLOAT',
    'INT',
    'STR',
    'COMMA',
    'SEMI',
    'DOT',
    'LPAREN',
    'RPAREN',
    'LBRACKET',
    'RBRACKET',
    'VLINE',
    'EQU',
    'GT',
    'LT',
    'GTE',
    'LTE',
)

t_COMMA     = ','
t_SEMI      = ';'
t_DOT       = '\.'
t_LPAREN    = '\('
t_RPAREN    = '\)'
t_LBRACKET  = '\['
t_RBRACKET  = '\]'
t_VLINE     = '\|'
t_EQU       = '='
t_GT        = '>'
t_LT        = '<'
t_GTE       = '>='
t_LTE       = '<='

reserved = {
    
}

use_lex_print = False
use_yacc_print = False


def lex_print(*p):
    if not use_lex_print:
        return
    print('Lex:', p)

def yacc_print(*p):
    if not use_yacc_print:
        return    
    print('Yacc:', p)


def t_BUILDIN(t):
    r'@[_A-Za-z0-9]*'
    t.type = reserved.get(t.value, 'BUILDIN')    # Check for reserved words
    lex_print(t)
    return t

def t_NAME(t):
    r'[A-Za-z_][_A-Za-z0-9]*'
    t.type = reserved.get(t.value, 'NAME')    # Check for reserved words
    lex_print(t)
    return t



def t_FLOAT(t):
    r'\d+(\.\d+)'
    t.value = float(t.value)
    return t 

def t_INT(t):
    r'[+|-]?\d+'
    t.value = int(t.value)
    return t

def t_STR(t):
    r'\'([^\'\\\n]|(\\.))*?\''
    t.value = t.value.strip("\"'")
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    # symprint("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


t_ignore            = ' \t'
t_ignore_COMMENT    = '\#.*'
######################################################################
# yacc
def p_error(p):
    yacc_print("Error:", p)


def p_rvalue(p):
    """rvalue       : filter
                    | arrval
                    | symbol
                    | func
                    | list
                    | INT
                    | FLOAT
                    | STR"""
    p[0] = p[1]

def p_symbol(p):
    """symbol       : NAME
                    | symbol DOT NAME"""
    yacc_print('symbol', p)
    if len(p) == 2:
        p[0] = ('sym', p[1])
    elif len(p) == 4:
        p[0] = ('sym', p[1], p[3])

def p_arrval(p):
    """arrval       : symbol LBRACKET INT RBRACKET"""
    yacc_print('arrval', p)
    if len(p) == 5:
        p[0] = ('arrval', p[1], p[3])

def p_list_items(p):
    """list_items   : list_items COMMA rvalue
                    | rvalue"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1]
        p[0].append(p[3])

# [1, 2, ....]
def p_list(p):
    """list         : LBRACKET list_items RBRACKET"""
    p[0] = p[2]


def p_filter_item(p):
    """filter_item  : NAME
                    | func"""
    p[0] = p[1]

def p_filter_items(p):
    """filter_items : filter_items COMMA filter_item
                    | filter_item"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1]
        p[0].append(p[3])

def p_filter(p):
    """filter       : symbol VLINE filter_items VLINE"""
    
    p[0] = ('filter', p[1], p[3])


def p_param(p):
    """param        : rvalue"""
    p[0] = ('param', p[1])

def p_param_list(p):
    """param_list   : param_list COMMA param
                    | param"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1]
        p[0].append(p[3])


def p_params(p):
    """params       : LPAREN param_list RPAREN
                    | LPAREN RPAREN"""
    if len(p) == 4:
        p[0] = p[2]
    else:
        p[0] = []
    

def p_condition(p):
    """condition        : symbol EQU rvalue
                        | BUILDIN EQU rvalue
                        | symbol GT rvalue
                        | symbol LT rvalue
                        | symbol GTE rvalue
                        | symbol LTE rvalue"""
    p[0] = ('condition', p[2], p[1], p[3])

def p_condition_list(p):
    """condition_list   : condition_list COMMA condition
                        | condition"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1]
        p[0].append(p[3])

def p_conditions(p):
    """conditions       : LPAREN condition_list RPAREN
                        | LPAREN RPAREN"""
    if len(p) == 4:
        p[0] = p[2]
    else:
        p[0] = []


def p_func(p):
    """func         :   BUILDIN params"""
    p[0] = ('func', p[1], p[2])

def p_redis_query(p):
    """redis_query  :   NAME DOT BUILDIN DOT NAME params"""
    p[0] = ('redis_query', p[1], p[3], p[5], p[6])

def p_query(p):
    """query        :   NAME DOT NAME DOT NAME conditions"""
    p[0] = ('query', p[1], p[3], p[5], p[6])
    

def p_statement(p):
    """statement    :   NAME EQU func SEMI
                    |   NAME EQU query SEMI
                    |   NAME EQU redis_query SEMI
                    |   func SEMI
                    |   query SEMI
                    |   redis_query SEMI"""
    if len(p) > 3:
        yacc_print("statement", p[1], p[3])
        p[0] = ("statement", p[1], p[3])
    else:    
        yacc_print("statement", '_r', p[1])
        p[0] = ("statement", '_r', p[1])

"""
yacc start 
"""
def p_statements(p):
    """statements   :   statements statement
                    |   statement """
    # print("#", len(p))
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1]
        p[0].append(p[2])


if __name__ == '__main__':
    import ply.lex as lex
    import ply.yacc as yacc

    use_lex_print = True
    use_yacc_print = True
    lex.lex()
    parser = yacc.yacc(start = 'statements')
    
    code = """
redis = @redis('localhost', 0);

abc = redis.@0.abc();

@p(abc);
    """
    statements = parser.parse(code)
    print("=" * 40)
    for s in statements:
        print(s)
