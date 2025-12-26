from text_clip import TextClip

import os
from shutil import rmtree


class DatapackExistsError(Exception):
	def __init__(self, message: str = 'Datapack already exists in output file location', location: str = None):
		final_message = message
		if location:
			final_message = f'{message}: "{location}"'

		super().__init__(final_message)


class DatapackGenerator:
	def __init__(self, replace_previous: bool = False):
		self.clip = TextClip('${', '}$')
		self.files = {}

		self.replace_previous = replace_previous


	def create_file_name(self):
		return str(self.clip.counter)

	def _on_sub_paper_finnished(self, content):
		file_name = self.create_file_name()

		self.files.update({file_name: content})
		return file_name


	def convert(self, content: str):
		main_file = self.clip.run(content, self._on_sub_paper_finnished)
		self.files.update({'main': main_file})

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

		with open(os.path.join(pack_location, 'main.mcfunction'), 'x') as file:
			file.write(self.files['main'])

	def generate(self, content, output_location: str):
		self.convert(content)
		self.create_files(output_location)


datapack_generator = DatapackGenerator(replace_previous=True)
datapack_generator.generate('function ${say Hello!}$', 'output')
