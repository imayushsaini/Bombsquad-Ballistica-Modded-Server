import ba, _ba, json

textes_path = _ba.env()['python_directory_user']+'/Currency/Data/textes.json'


def CLstr(language, text):
	with open(textes_path, 'r') as f:
		textes = json.load(f)
		text = textes[language][text]
	return text


def Errorstr(language, text):
	with open(textes_path, 'r') as f:
		textes = json.load(f)
		t = textes[language]["errors"][text]
	return t

