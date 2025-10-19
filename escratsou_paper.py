import sys
import os
import shutil

import yaml


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
		self.output_name = ''
		self.overide = False
		self.extension = 'mcfunction'

		self.files = []
		self.compiled_files = []

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

		self.compiled_files.append({'path': file_name, 'content': sub_file})
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

		self.compiled_files.append({'path': self.main_file_name, 'content': self.main_file})

	def write_files(self):
		output_path = os.path.abspath(self.output_path)

		if self.overide:
			try:
				shutil.rmtree(output_path)
			except FileNotFoundError:
				pass
		os.mkdir(output_path)

		for file in self.compiled_files:
			with open(f'{output_path}/{file['path']}.{self.extension}', 'x') as opened_file:
				opened_file.write(file['content'])

	def loop_file(self, file, name):
		split_file_name = name.split('.')
		if split_file_name[-1] != 'esp':
			return

		with open(file, 'r') as opened_file:
			file_content = opened_file.read()

		self.files.append({'name': split_file_name[0], 'content': file_content})

	def loop_folder(self, folder):
		for file in os.listdir(folder):
			current_file = os.path.join(folder, file)
			if os.path.isfile(current_file):
				self.loop_file(current_file, file)
			else:
				self.loop_folder(current_file)

	def compile(self, path, output_path='output', overide=False):
		config_file = os.path.join(path, 'config.yml')
		with open(config_file, 'r') as opened_config_file:
			config = yaml.safe_load(opened_config_file)

		self.display_path = config['name'] + ':'

		self.output_path = output_path
		self.output_name = f'{config['display_name']}_{config['format']}'
		self.overide = overide

		self.files = []
		self.compiled_files = []

		self.loop_folder(path)

		for code in self.files:
			self.code = code['content']
			self.main_file_name = code['name']
			self.convert()

		self.write_files()
