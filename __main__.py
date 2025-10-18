from escratsou_paper import Commandizer

commandizer = Commandizer('my_datapack')

print(commandizer.convert('function *{execute if entity @a run function *{say Created using escratsou!}*}*', 'main'))
