######################################################
#
# Paper Clip (Commit 6), Under MIT liscense at https://github.com/artelephantb/paper-clip
#
######################################################

class PaperClip:
	def __init__(self, sub_cue_start: str, sub_cue_end: str, on_sub_paper_export, on_paper_export):
		self.sub_cue_start = sub_cue_start
		self.sub_cue_end = sub_cue_end
		self.on_sub_paper_export = on_sub_paper_export
		self.on_paper_export = on_paper_export

		self.papers = []
		self.current_paper = ''
		self.index = 0

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

	def get_sub_paper(self):
		combined_list = []
		combined = ''

		while self.index < len(self.current_paper):
			if self.is_cue(self.sub_cue_start):
				combined_list.append(combined)
				combined = ''

				self.index += len(self.sub_cue_start)
				combined_list.append(self.get_sub_paper())
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

	def get_paper(self, content: str):
		self.current_paper = content

		self.index = 0
		return self.get_sub_paper()

	def add_paper(self, title: str, content: str):
		self.papers.append([title, self.get_paper(content)])

	def export_sub_paper(self, name: str, content: list):
		combined = ''
		for paper in content:
			if type(paper) != list:
				combined += paper
				continue
			sub_paper = self.export_sub_paper(name, paper)
			combined += self.on_sub_paper_export(name, sub_paper)

			self.counter += 1

		return combined

	def export_papers(self):
		for paper in self.papers:
			self.counter = 0
			sub_paper = self.export_sub_paper(paper[0], paper[1])

			self.on_paper_export(sub_paper)
