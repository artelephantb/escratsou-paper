from escratsou_paper import Compiler

compiler = Compiler()

file_name = 'my_file.mcfunction.esp'
split_file_name = file_name.split('.')
with open(file_name, 'r') as file:
	file_content = file.read()

compiler.compile(file_content, split_file_name[1], split_file_name[0], 'my_datapack:', overide=True)
