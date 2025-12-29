def license():
	return '''MIT License

Copyright (c) 2025 Artitapheiont (artelephantb)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

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
