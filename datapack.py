from text_clip import TextClip

import yaml
import json

import os
from shutil import rmtree

import sys


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
	'''
	Generates a datapack from a string
	'''

	def __init__(self, replace_previous: bool = False):
		self.clip = TextClip('${', '}$')

		self.functions = []
		self.tags = []

		self.current_functions = []
		self.current_tags = []

		self.current_namespace = ''

		self.file_translations = {}

		self.next_name = 0

		self.replace_previous = replace_previous


	def create_file_name(self):
		return str(self.next_name) + '_' + str(self.clip.counter)


	def _on_sub_paper_finnished(self, content):
		file_name = self.create_file_name()

		self.current_functions.append((file_name, 'mcfunction', content))
		return f'{self.current_namespace}:{file_name}'

	def _on_reference_translation_finnished(self, content):
		return self.file_translations[content]


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
			file_name, file_extension = os.path.splitext(file)

			main_file = self.clip_reference_translation(file_content)
			main_file = self.clip_inline_function(main_file)

			name = file_name + self.create_file_name()
			self.file_translations[file_name] = name
			self.current_functions.append((name, file_extension, main_file))

			self.next_name += 1

	def convert_tag_files(self, path: str):
		files = self.get_all_files(os.path.join(path, 'tags'))

		for file, file_content in files:
			file_name, file_extension = os.path.splitext(file)

			main_file = self.clip_reference_translation(file_content)
			main_file = self.clip_inline_function(main_file)

			self.current_tags.append((file_name, file_extension, main_file))

			self.next_name += 1

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
		pack_file = 'demos/My Pack'
		print('Running demo: demos/My Pack')

	# Pack output
	try:
		output = sys.argv[2]
		print('Using output directory:', sys.argv[2])
	except IndexError:
		output = 'output'
		print('Using default output directory: output')


	datapack_generator.generate(pack_file, output)
