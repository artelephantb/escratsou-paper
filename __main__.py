from escratsou_paper import Compiler

compiler = Compiler()

compiler.compile('function *{execute if entity @a run function *{say Created using escratsou!}*}*', 'main', 'my_datapack:', overide=True)
