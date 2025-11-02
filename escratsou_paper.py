from text_clip import TextClip
import yaml
import os


path = 'demos/01'
output_path = 'output'


class EscratsouPaper:
	def _on_sub_paper_finished(self, content):
		content_hash = str(hash(content))
		self.output_scripts.append([content_hash + '.mcfunction', content])

		return f'{self.name}:{content_hash}'


	def __init__(self):
		self.text_clip = TextClip('*{', '}*')

		self.loaded_scripts = []
		self.output_scripts = []

		self.current_script_name = ''

		self.name = ''
		self.display_name = ''
		self.format = 0


	def load_config_file(self, location: str):
		with open(location, 'r') as file:
			config = yaml.safe_load(file)

		self.name = config['name']
		self.display_name = config['display_name']
		self.format = config['format']

	def load_batch_scripts(self, location: str):
		for file_name in os.listdir(location):
			file_path = os.path.join(location, file_name)

			if os.path.isdir(file_path):
				self.load_batch_scripts(file_path)
				continue

			with open(file_path, 'r') as script:
				self.loaded_scripts.append([os.path.splitext(file_name)[0], script.read()])

	def dump_batch_scripts(self, scripts: list, location: str):
		for script in scripts:
			file_path = os.path.join(location, script[0])

			with open(file_path, 'w') as file:
				file.write(script[1])


	def export_pack_from_folder(self, location: str, output_location: str):
		self.loaded_scripts.clear()

		self.load_config_file(os.path.join(location, 'config.yml'))
		self.load_batch_scripts(os.path.join(location, 'scripts'))

		for script in self.loaded_scripts:
			self.current_script_name = script[0]
			self.output_scripts.append([self.current_script_name + '.mcfunction', self.text_clip.run(script[1], self._on_sub_paper_finished)])

		self.dump_batch_scripts(self.output_scripts, output_location)


escratsou_paper = EscratsouPaper()
escratsou_paper.export_pack_from_folder(path, output_path)
