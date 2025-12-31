from text_clip import TextClip

import yaml
import json

import os
from shutil import rmtree

import sys
import random


def split_path(path: str):
	'''
	Splits path into file name and extension
	
	:param path: Path to split
	:type path: str
	'''

	file_name, file_extension = os.path.splitext(path)
	file_extension = file_extension.removeprefix('.')

	return file_name, file_extension

def generate_file_name(current_name: str = ''):
	return current_name + str(random.randint(1000, 9999))


class DatapackExistsError(Exception):
	def __init__(self, message: str = 'Datapack already exists in output file location', location: str = None):
		final_message = message
		if location:
			final_message = f'{message}: "{location}"'

		super().__init__(final_message)

class InvalidPackGenerator(Exception):
	def __init__(self, message: str = 'Pack generator id does not match this programs generator', generator: str = None):
		final_message = message
		if generator:
			final_message = f'{message}: "{generator}"'

		super().__init__(final_message)


class DatapackGenerator:
	def __init__(self, replace_previous: bool = False):
		self.clip = TextClip('${', '}$')

		self.functions = []
		self.tags = []

		self.indexed_files = {}

		self.current_functions = []
		self.current_tags = []

		self.current_namespace = ''

		self.file_translations = {}

		self.replace_previous = replace_previous


	def _on_sub_paper_finnished(self, content):
		file_name = generate_file_name()

		self.current_functions.append((file_name, 'mcfunction', content))
		return f'{self.current_namespace}:{file_name}'

	def _on_reference_translation_finnished(self, content):
		try:
			return self.file_translations[content]
		except KeyError:
			raise KeyError(f'Function \'{content}\' not found')


	def clip_reference_translation(self, content: str):
		self.clip.sub_cue_start = '%{'
		self.clip.sub_cue_end = '}%'
		output = self.clip.run(content, self._on_reference_translation_finnished)

		return output

	def clip_inline_function(self, content: str):
		self.clip.sub_cue_start = '${'
		self.clip.sub_cue_end = '}$'
		output = self.clip.run(content, self._on_sub_paper_finnished)

		return output


	def index_files(self, path: str):
		contents = os.listdir(path)
		index = {}

		for file in contents:
			file_path = os.path.join(path, file)

			if os.path.isdir(file_path):
				index.update({file: self.index_files(file_path)})
				continue

			with open(file_path, 'r') as opened_file:
				file_content = opened_file.read()

			file_name, file_extension = split_path(file)

			translated_file_name = generate_file_name(file_name)
			self.file_translations.update({file_name: translated_file_name})

			index.update({translated_file_name: (file_content, file_extension)})

		return index

	def get_all_files(self, path: str):
		contents = os.listdir(path)
		files = []

		for file in contents:
			file_path = os.path.join(path, file)

			if os.path.isdir(file_path):
				files += self.get_all_files(file_path)
				continue

			with open(file_path, 'r') as opened_file:
				file_content = opened_file.read()

			files.append((file, file_content))

		return files

	def convert_function_files(self, path: str):
		files = self.get_all_files(os.path.join(path, 'function'))

		for file, file_content in files:
			file_name, file_extension = split_path(file)

			main_file = self.clip_reference_translation(file_content)
			main_file = self.clip_inline_function(main_file)

			name = self.file_translations[file_name]
			self.current_functions.append((name, file_extension, main_file))

	def convert_tag_files(self, path: str):
		files = self.get_all_files(os.path.join(path, 'tags'))

		for file, file_content in files:
			file_name, file_extension = split_path(file)

			main_file = self.clip_reference_translation(file_content)
			main_file = self.clip_inline_function(main_file)

			self.current_tags.append((file_name, file_extension, main_file))

	def convert_files(self, path: str):
		try:
			self.convert_function_files(path)
		except FileNotFoundError:
			pass

		try:
			self.convert_tag_files(path)
		except FileNotFoundError:
			pass


	def write_pack_meta_file(self, location: str, min_format: int, max_format: int, description: str | list | dict):
		'''
		Writes a pack.mcmeta file

		:param location: Location of the pack.mcmeta
		:type location: str

		:param min_format: The minimum datapack version supported
		:type min_format: int

		:param max_format: The maximum datapack version supported
		:type max_format: int

		:param description: Description of the pack
		:type description: str | list
		'''

		content = {'pack': {'min_format': min_format, 'max_format': max_format, 'description': description}}
		content = json.dumps(content)

		with open(location, 'x') as final_file:
			final_file.write(content)


	def export(self, output_location: str, min_format: int, max_format: int, description: str | list | dict, output_name: str):
		pack_location = os.path.join(output_location, output_name)
		try:
			os.mkdir(pack_location)
		except FileExistsError:
			if self.replace_previous:
				rmtree(pack_location)
			else:
				raise DatapackExistsError(location=os.path.abspath(output_location))

			os.mkdir(pack_location)

		# Create files
		self.write_pack_meta_file(os.path.join(pack_location, 'pack.mcmeta'), min_format, max_format, description)

		for namespace in self.functions:
			name = namespace[0]
			data = namespace[1]

			os.makedirs(os.path.join(pack_location, f'data/{name}/function'))

			for file in data:
				with open(os.path.join(pack_location, f'data/{name}/function/{file[0]}.{file[1]}'), 'x') as final_file:
					final_file.write(file[2])

		for namespace in self.tags:
			name = namespace[0]
			data = namespace[1]

			os.makedirs(os.path.join(pack_location, f'data/{name}/tags/function'))

			for file in data:
				with open(os.path.join(pack_location, f'data/{name}/tags/function/{file[0]}.{file[1]}'), 'x') as final_file:
					final_file.write(file[2])

		# Create Notice
		with open(os.path.join(pack_location, 'NOTICE.txt'), 'x') as notice_file:
			notice_file.write('''It is not recommended to edit or change this datapack directly, please use Escratsou Paper instead (requires source code access).''')


	def generate(self, input_location: str, output_location: str):
		'''
		Converts string to datapack, then written to output location

		:param input_location: Path to be converted to datapack
		:type content: str

		:param output_location: Location to output datapack
		:type output_location: str
		'''

		with open(os.path.join(input_location, 'pack.espmeta'), 'r') as file:
			pack = yaml.safe_load(file)

		escratsou_generator = pack['generator']
		if escratsou_generator != 'esp':
			raise InvalidPackGenerator(generator=pack['generator'])

		output_name = pack['output_name']

		min_format = pack['mc_min']
		max_format = pack['mc_max']
		description = pack['description']

		self.indexed_files = self.index_files(input_location)

		for namespace in os.listdir(f'{input_location}/data'):
			self.current_functions = []
			self.current_tags = []

			self.current_namespace = namespace

			path = os.path.join(f'{input_location}/data', namespace)
			self.convert_files(path)

			self.functions.append((namespace, self.current_functions))
			self.tags.append((namespace, self.current_tags))

		self.export(output_location, min_format, max_format, description, output_name)


if __name__ == '__main__':
	datapack_generator = DatapackGenerator(replace_previous=True)

	# Pack data
	try:
		pack_file = sys.argv[1]
		print('Running file:', sys.argv[1])
	except IndexError:
		pack_file = 'demos/Demo Pack'
		print('Running demo: demos/Demo Pack')

	# Pack output
	try:
		output = sys.argv[2]
		print('Using output directory:', sys.argv[2])
	except IndexError:
		output = 'output'
		print('Using default output directory: output')


	datapack_generator.generate(pack_file, output)
