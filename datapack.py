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

		self.main_file = ''
		self.files = []

		self.replace_previous = replace_previous


	def create_file_name(self):
		return str(self.clip.counter)

	def _on_sub_paper_finnished(self, content):
		file_name = self.create_file_name()

		self.files.append([file_name, 'mcfunction', content])
		return file_name


	def convert(self, content: str):
		main_file = self.clip.run(content, self._on_sub_paper_finnished)
		self.main_file = main_file


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
		with open(location, 'x') as final_file:
			final_file.write(str(content))


	def create_files(self, output_location: str):
		pack_location = os.path.join(output_location, 'My Pack')
		try:
			os.mkdir(pack_location)
		except FileExistsError:
			if self.replace_previous:
				rmtree(pack_location)
			else:
				raise DatapackExistsError(location=os.path.abspath(output_location))

			os.mkdir(pack_location)

		# Create files
		self.write_pack_meta_file(os.path.join(pack_location, 'pack.mcmeta'))

		with open(os.path.join(pack_location, 'main.mcfunction'), 'x') as final_file:
			final_file.write(self.main_file)

		for file in self.files:
			with open(os.path.join(pack_location, f'{file[0]}.{file[1]}'), 'x') as final_file:
				final_file.write(file[2])


	def generate(self, content: str, output_location: str):
		'''
		Converts string to datapack, then written to output location

		:param content: String to be converted to datapack
		:type content: str

		:param output_location: Location to output datapack
		:type output_location: str
		'''

		self.convert(content)
		self.create_files(output_location)


datapack_generator = DatapackGenerator(replace_previous=True)
datapack_generator.generate('function ${say Hello!}$', 'output')
