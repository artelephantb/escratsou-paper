def about():
	return 'Text Clip is a single-file libary used to add custom elements to other formats. Under MIT liscense at https://github.com/artelephantb/text-clip'

class TextClip:
	def _default_sub_paper_finished_method(content):
		return content

	def __init__(self, sub_cue_start: str, sub_cue_end: str):
		self.sub_cue_start = sub_cue_start
		self.sub_cue_end = sub_cue_end

		self.current_paper = ''
		self.index = 0

		self.sub_paper_finished_method = self._default_sub_paper_finished_method

		self.counter = 0

	def is_cue(self, cue: str):
		paper_character = ''
		cue_character = ''
		index = 0

		while self.index < len(self.current_paper) and index < len(cue):
			paper_character = self.current_paper[self.index + index]
			cue_character = cue[index]
			if paper_character != cue_character:
				return False
			index += 1

		return True

	def structurize_sub_paper(self):
		combined_list = []
		combined = ''

		while self.index < len(self.current_paper):
			if self.is_cue(self.sub_cue_start):
				combined_list.append(combined)
				combined = ''

				self.index += len(self.sub_cue_start)
				combined_list.append(self.structurize_sub_paper())
			elif self.is_cue(self.sub_cue_end):
				self.index += len(self.sub_cue_end) - 1
				if len(combined) > 0:
					combined_list.append(combined)
				return combined_list
			else:
				combined += self.current_paper[self.index]
			self.index += 1

		if len(combined) > 0:
			combined_list.append(combined)
		return combined_list

	def structurize_paper(self, content: str):
		self.current_paper = content

		self.index = 0
		return self.structurize_sub_paper()

	def run_sub_paper(self, content: list):
		combined = ''
		for paper in content:
			if type(paper) != list:
				combined += paper
				continue

			sub_paper = self.run_sub_paper(paper)
			combined += self.sub_paper_finished_method(sub_paper)

			self.counter += 1

		return combined

	def run(self, content: str, sub_paper_finished_method=_default_sub_paper_finished_method):
		self.sub_paper_finished_method = sub_paper_finished_method

		structurized_content = self.structurize_paper(content)

		self.counter = 0
		return self.run_sub_paper(structurized_content)
