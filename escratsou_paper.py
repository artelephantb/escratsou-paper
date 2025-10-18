import os
import shutil


INNER_COMMAND_START = '*{'
INNER_COMMAND_END = '}*'


class Compiler:
	def __init__(self):
		self.main_file_name = ''

		self.code = ''
		self.character_index = 0
		self.main_file = ''
		self.display_path = ''
		self.output_path = ''
		self.overide = False

		self.files = []

	def inner_command(self):
		sub_file = ''
		while self.character_index < len(self.code):
			character = self.code[self.character_index]
			try:
				next_character = self.code[self.character_index + 1]
			except IndexError:
				next_character = ''

			if character == INNER_COMMAND_START[0] and next_character == INNER_COMMAND_START[1]:
				self.character_index += 2
				sub_file += self.inner_command()
				self.character_index += 1
			elif character == INNER_COMMAND_END[0] and next_character == INNER_COMMAND_END[1]:
				break
			else:
				sub_file += character
			self.character_index += 1

		file_name = f'inner_{self.main_file_name}_{str(self.character_index)}'
		display_name = self.display_path + file_name

		self.files.append({'path': file_name, 'content': sub_file})
		return display_name

	def convert(self):
		self.character_index = 0
		self.main_file = ''

		while self.character_index < len(self.code):
			character = self.code[self.character_index]
			try:
				next_character = self.code[self.character_index + 1]
			except IndexError:
				next_character = ''

			if character == INNER_COMMAND_START[0] and next_character == INNER_COMMAND_START[1]:
				self.character_index += 2
				self.main_file += self.inner_command()
				self.character_index += 1
			else:
				self.main_file += character

			self.character_index += 1

		self.files.append({'path': self.main_file_name, 'content': self.main_file})

	def write_files(self):
		output_path = os.path.abspath(self.output_path)

		if self.overide:
			shutil.rmtree(output_path)
		os.mkdir(output_path)

		for file in self.files:
			with open(f'{output_path}/{file['path']}.{self.extension}', 'x') as opened_file:
				opened_file.write(file['content'])

	def compile(self, code: str, extension: str, main_file_name: str, display_path: str, output_path='output', overide=False):
		self.code = code
		self.extension = extension
		self.main_file_name = main_file_name
		self.display_path = display_path

		self.output_path = output_path
		self.overide = overide

		self.files = []

		self.convert()
		self.write_files()
