from paper_clip import PaperClip

def _on_sub_paper_export(name, content):
	with open(f'{name}_{str(escratsou_paper.counter)}.mcfunction', 'w') as final:
		final.write(content)
	return f'my_datapack:{name}_{str(escratsou_paper.counter)}'

def _on_paper_export(content):
	print(content)

escratsou_paper = PaperClip('*{', '}*', _on_sub_paper_export, _on_paper_export)
escratsou_paper.add_paper('main', 'function *{function *{say Hello!}*}*')

escratsou_paper.export_papers()
