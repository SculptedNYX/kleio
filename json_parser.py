import json, codecs, os

async def select_text(lang, path):

    el = path.split('.')
    with open(f'data/{lang}.json', 'r', encoding='utf-8') as f:
        data = f.read()

    texts = json.loads(data)

    return texts[el[0]][el[1]]

def auth(token):

    with open(os.path.join(os.path.abspath('data'),"auth.json"), 'r') as f:
        data = f.read()

    tokens = json.loads(data)

    return tokens[token]
