from markdown2 import markdown
import os


for filename in os.listdir("./content"):
    with open("./content/" + filename, 'r') as file:
        parsed_md = markdown(file.read(), extras=['metadata'])

    print('Metadata: ', parsed_md.metadata)
    print('Content: ', parsed_md)