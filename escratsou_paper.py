INNER_COMMAND_START = '*{'
INNER_COMMAND_END = '}*'


class Commandizer:
	def __init__(self, namespace: str):
		self.namespace = namespace
		self.main_file_name = ''

		self.code = ''
		self.character_index = 0
		self.main_file = ''

		self.files = []

	def inner_command(self):
		sub_file = ''
		while self.character_index < len(self.code):
			character = self.code[self.character_index]
			if character == INNER_COMMAND_START[0] and self.code[self.character_index + 1] == INNER_COMMAND_START[1]:
				self.character_index += 2
				sub_file += self.inner_command()
				self.character_index += 1
			elif character == INNER_COMMAND_END[0] and self.code[self.character_index + 1] == INNER_COMMAND_END[1]:
				break
			else:
				sub_file += character
			self.character_index += 1

		random_name = f'inner_{self.main_file_name}_{str(self.character_index)}'
		namespace_name = f'{self.namespace}:{random_name}'

		self.files.append({'path': namespace_name, 'content': sub_file})
		return namespace_name

	def convert(self, code: str, main_file_name: str):
		self.code = code
		self.main_file_name = main_file_name

		self.character_index = 0
		self.main_file = ''

		self.files = []

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
		return self.files
