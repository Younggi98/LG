# practice 1 : Search all files under 0_YG Project
from pathlib import Path
p = Path('D:/0_YG Project')
print(list(p.glob('*')))

""" my version
for filename in p.glob('*'):
    while Path(filename).is_dir():
        for files in Path(filename).rglob('*'): # rglob recursively search more in depth
            print(files)
        break    """
            
# better version : while loop is unnecessary as it only executes one time
for filename in p.glob('*'):
    if Path(filename).is_dir():
        for files in Path(filename).rglob('*'):
            print(files)

# Practice 2 : Writes a txt file
p2 = Path('D:/0_YG Project/0_Python Practice\quizes_2026-05-21\capital_quiz_1.txt')
p2.write_text('Hello world')
p2.read_text()

# Calling p.exists() returns True if the path exists, and returns False if it doesn’t exist.
p.exists()
#Calling p.is_file() returns True if the path exists and is a file, and returns False otherwise.
p.is_file()
#Calling p.is_dir() returns True if the path exists and is a directory, and returns False otherwise.
p.is_dir()

# open -> read / write -> close
p1 = Path('D:/0_YG Project/0_Python Practice/quizes_2026-05-21') # Path to the directory
quiz1= open(p1 / 'capital_quiz_1.txt', encoding='UTF-8') # Open the exact file 

# Write first -> close it at the end
quiz1_alt =  open('capital_quiz_1.txt', 'w', encoding='UTF-8')
quiz1_alt.write('Hello, world \n')
quiz1_alt.close()

# Read only and close it at the end
quiz1_alt= open('capital_quiz_1.txt', encoding='UTF-8')
content = quiz1_alt.read()
quiz1_alt.close()
print(content)

# Alternative way
with open('data.txt', 'w', encoding='UTF-8') as data1:
    data1.write('This is data 1!')

with open('data.txt', encoding='UTF-8') as data1:
    content = data1.read()

    