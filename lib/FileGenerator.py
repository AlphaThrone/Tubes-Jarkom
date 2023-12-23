import os
import random
import string

file_path = 'random_5mb_file.md'

random_content = ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation + ' ', k=(5 * 1024 * 1024)))

with open(file_path, 'w') as file:
    file.write(random_content)

print(f"File created: {file_path}")
