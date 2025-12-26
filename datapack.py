from text_clip import TextClip

import os
from shutil import rmtree


class DatapackExistsError(Exception):
	'''
	Outputs an error for when a datapack already exists in a location
	'''

	def __init__(self, message: str = 'Datapack already exists in output file location', location: str = None):
		final_message = message
		if location:
			final_message = f'{message}: "{location}"'

		super().__init__(final_message)


class DatapackGenerator:
	'''
	Generates a datapack from a string
	'''

	def __init__(self, replace_previous: bool = False):
		self.clip = TextClip('${', '}$')
		self.functions = []

		self.replace_previous = replace_previous


	def create_file_name(self):
		return str(self.clip.counter)

	def _on_sub_paper_finnished(self, content):
		file_name = self.create_file_name()

		self.functions.append([file_name, 'mcfunction', content])
		return file_name

	def convert(self, content: dict):
		for key in content.keys():
			main_file = self.clip.run(content[key], self._on_sub_paper_finnished)
			self.functions.append([key, 'mcfunction', main_file])


	def write_pack_meta_file(self, location: str, min_format: int = 94, max_format: int = 94, description: str | list = 'My Description'):
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


	def export(self, output_location: str):
		pack_location = os.path.join(output_location, 'My Pack')
		try:
			os.mkdir(pack_location)
		except FileExistsError:
			if self.replace_previous:
				rmtree(pack_location)
			else:
				raise DatapackExistsError(location=os.path.abspath(output_location))

			os.mkdir(pack_location)

		os.makedirs(os.path.join(pack_location, 'data', 'my-pack', 'function'))

		# Create files
		self.write_pack_meta_file(os.path.join(pack_location, 'pack.mcmeta'))

		for file in self.functions:
			with open(os.path.join(pack_location, 'data', 'my-pack', 'function', f'{file[0]}.{file[1]}'), 'x') as final_file:
				final_file.write(file[2])


	def generate(self, content: dict, output_location: str):
		'''
		Converts string to datapack, then written to output location

		:param content: Dictionary to be converted to datapack
		:type content: dict

		:param output_location: Location to output datapack
		:type output_location: str
		'''

		self.convert(content)
		self.export(output_location)


datapack_generator = DatapackGenerator(replace_previous=True)
datapack_generator.generate({'main': 'function my-pack:${say Hello!}$'}, 'output')
