from escratsou_paper import Compiler
import sys


input_directory = sys.argv[1]

compiler = Compiler()
compiler.compile(input_directory, overide=True)
