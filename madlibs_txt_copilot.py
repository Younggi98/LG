from pathlib import Path
import re

parts_of_speech = ['ADJECTIVE', 'NOUN', 'ADVERB', 'VERB']
pattern = re.compile(r'\b(' + '|'.join(parts_of_speech) + r')\b')

def madLibs(madlibs_txt):
    path = Path(madlibs_txt)
    text = path.read_text(encoding='UTF-8')

    placeholders = pattern.findall(text)
    user_inputs = []
    for part in placeholders:
        user_inputs.append(input(f'Enter an {part}: '))

    def replace(match):
        return user_inputs.pop(0)

    result = pattern.sub(replace, text)

    output_path = path.with_name(path.stem + '_output' + path.suffix)
    output_path.write_text(result, encoding='UTF-8')

    print(result)
    print('Saved to', output_path)

madLibs('D:/0_YG Project/0_Python Practice/madlibs_txt.txt')