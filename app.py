from markdown2 import markdown
from os import listdir,path,getcwd
from pathlib import Path
from shutil import rmtree

from jinja2 import Environment, PackageLoader

app_options ={
    "clean_output": True
}
global_options = {
    "lang": "en",
    "is_rtl": False,

    "site_title": "My Site"
}


def getListOfFiles(dirName):
    # create a list of file and sub directories
    # names in the given directory
    listOfFile = listdir(dirName)
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = path.join(dirName, entry)
        # If entry is a directory then get the list of files in this directory
        if path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(fullPath)
        else:
            allFiles.append(fullPath)

    return allFiles

def parseContent():
    counter = 0
    for filename in getListOfFiles("content"):
        # ERROR: tries to open the subfolder(posts) as file here
        with open(path.join(filename), 'r') as file:
            parsed_md = markdown(file.read(), extras=['metadata'])
        data = parsed_md.metadata
        data["body"] = parsed_md
            
        html = buildContent(data)

        #print(data)
        if(data["slug"] != "/" and data["slug"] != "index" and data["slug"] != "home"):
            slug = data["slug"]
        else:
            slug = ""
        
        outputFile = path.join(getcwd(),"output", slug )
        
        
        
        if generateOutput(html, outputFile):
            print(str(counter) + " " + filename +
                  " processed to -> " + outputFile + "/index.html")
        else:
            print(str(counter) + " " + "ERROR generating" +
                  outputFile + "/index.html")
        
        counter += 1


def buildContent(data,template="base.html"):
    env = Environment(loader=PackageLoader('app','templates'))
    render = env.get_template(template)

    return render.render(content=data, globals=global_options) 


def generateOutput(html,file):
    #create folder(s) if doesn't exists
    try:
        Path(file).mkdir(parents=True, exist_ok=True)
    except:
        print("Wrong SLUG?\n" + file)
        return False

    with open(path.join(file + "/index.html"), 'w') as output:
        output.write(html)

    return True


if app_options["clean_output"]:
    try:
        rmtree(path.join(getcwd(), 'output') )
        print("Output folder cleaned")
    except:
        # TODO: false positive error?
        print("Error cleaning up output folder:" + getcwd() + '/output' )

parseContent( )
