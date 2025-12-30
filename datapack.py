from text_clip import TextClip

import yaml

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
		self.current_namespace = ''

		self.next_name = 0

		self.replace_previous = replace_previous


	def create_file_name(self):
		return str(self.next_name) + '_' + str(self.clip.counter)

	def _on_sub_paper_finnished(self, content):
		file_name = self.create_file_name()

		self.current_functions.append([file_name, 'mcfunction', content])
		return f'{self.current_namespace}:{file_name}'

	def convert_functions(self, functions: dict):
		for key in functions.keys():
			main_file = self.clip.run(functions[key], self._on_sub_paper_finnished)
			self.current_functions.append([key + self.create_file_name(), 'mcfunction', main_file])

			self.next_name += 1

	def convert_events(self, events: dict):
		try:
			tag = events['on_load']

			content = {'replace': False, 'values': ['my-pack:' + tag]}
			content = str(content).replace('\'', '"')
			content = str(content).replace('False', 'false')

			self.tags.append(['load', content])
		except KeyError:
			pass


	def convert_sub_files_function(self, path: str):
		contents = os.listdir(path)
		functions = {}

		for file in contents:
			file_path = os.path.join(path, file)

			if os.path.isdir(file_path):
				functions.update(self.convert_sub_files_function(file_path))
				continue

			with open(file_path, 'r') as opened_file:
				file_content = opened_file.read()

			functions.update({file.removesuffix('.mcfunction'): file_content})

		return functions

	def convert_files(self, path: str):
		files = self.convert_sub_files_function(os.path.join(path, 'function'))

		for key in files.keys():
			main_file = self.clip.run(files[key], self._on_sub_paper_finnished)
			self.current_functions.append((key + self.create_file_name(), 'mcfunction', main_file))

			self.next_name += 1


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
		content = str(content).replace('\'', '"')

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

		os.makedirs(os.path.join(pack_location, 'data/minecraft/tags/function'))

		# Create files
		self.write_pack_meta_file(os.path.join(pack_location, 'pack.mcmeta'), min_format, max_format, description)

		for namespace in self.functions:
			name = namespace[0]
			data = namespace[1]

			os.makedirs(os.path.join(pack_location, f'data/{name}/function'))

			for file in data:
				with open(os.path.join(pack_location, f'data/{name}/function/{file[0]}.{file[1]}'), 'x') as final_file:
					final_file.write(file[2])


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
			self.current_namespace = namespace

			path = os.path.join(f'{input_location}/data', namespace)
			self.convert_files(path)

			self.functions.append((namespace, self.current_functions))

		self.export(output_location, min_format, max_format, description, output_name)


datapack_generator = DatapackGenerator(replace_previous=True)

if __name__ == '__main__':
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
