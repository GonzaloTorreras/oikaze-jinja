from markdown2 import markdown
from os import listdir,path,getcwd
from pathlib import Path
from shutil import rmtree

from jinja2 import Environment, PackageLoader

'''
app_options:
    clean_output: (bool) Will delete the output folder, will perform a full build
    output_folder: (str) Define the path (local) for the generated content. Default (output)
    content_folder: (str) Define the path (local) to read the content. Default (content)
    jinja2_conf: (dict) You can pass a dictionary of jinja2 env config such: { "trim_blocks": False} Default(empty dict)
'''

app_options = {
    "clean_output": True,
    "output_folder": "output",
    "content_folder": "content",
    "jinja2_conf": {}

}
site_options = {
    "default_lang": "en",
    "lang_slugs": {
        "en": "",
        "es": "es"
    },
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


def splitall(pa):
    allparts = []
    while 1:
        parts = path.split(pa)
        if parts[0] == pa:  # sentinel for absolute paths
            allparts.insert(0, parts[0])
            break
        elif parts[1] == pa:  # sentinel for relative paths
            allparts.insert(0, parts[1])
            break
        else:
            pa = parts[0]
            allparts.insert(0, parts[1])
    return allparts

def outputF(filePath,data):
    if(data["slug"] != "/" and data["slug"] != "index" and data["slug"] != "home"):
        slug = data["slug"]
    else:
        slug = ""
    
    if type(filePath) == str:
        filePath = path.join(filePath)
    
    filePath = splitall(filePath)
    #replace first folder (content/ by default) for output folder (output/ by default)
    filePath[0] = app_options["output_folder"]

    # Add lang slug if needed
    if "lang_slugs" in site_options:
        if data["lang"] in site_options["lang_slugs"]:
            filePath.insert(1, site_options["lang_slugs"][data["lang"]])
        else:
            print("site_options[lang_slug] is missing lang: " + data["lang"])
            return False
    else:
        print("site_options is missing [lang_slug] key")
        return False

    # pop last item which is the original file name.
    filePath.pop(-1)
    #combine filePath + slug if slug not empty
    if slug:
        outputFile = path.join( *filePath, slug)
    else:
        outputFile = path.join(*filePath)


    return outputFile


def parseContent():
    counter = 0
    env = loadJinjaEnv()

    for fileName in getListOfFiles(app_options["content_folder"]):
        # ERROR: tries to open the subfolder(posts) as file here
        with open(path.join(fileName), 'r') as file:
            parsed_md = markdown(file.read(), extras=['metadata'])
        data = parsed_md.metadata
        data["body"] = parsed_md

        
        html = buildContent(env, data)

        #print(data)
        outputFile = outputF(fileName,data)
        
        if outputFile:
        
            if generateOutput(html, outputFile):
                print(str(counter) + " " + fileName +
                    " processed to -> " + outputFile + "/index.html")
            else:
                print(str(counter) + " " + "ERROR generating" +
                    outputFile + "/index.html")
            
            counter += 1
        else:
            print("Error getting output folder for %s",fileName)


def loadJinjaEnv():
    env = Environment(
        loader=PackageLoader('app', 'templates')
    )
    env.trim_blocks = True
    env.lstrip_blocks = True
    env.strip_trailing_newlines = True

    # TODO: Test in depth if this parser of jinja2 extra config works
    if "jinja2_env" in app_options:
        for k, v in app_options["jinja2_env"]:
            env[k] = v

    return env
def buildContent(env,data):
    
    if "template" in data:
        template = data["template"]
    else:
        template = "base.html" # TODO: add app setting to change name of default template name?
    render = env.get_template(template)

    return render.render(content=data, globals=site_options) 


def generateOutput(html,file):
    #create folder(s) if doesn't exists
    try:
        Path(file).mkdir(parents=True, exist_ok=True)
    except:
        print("Wrong SLUG?" + file)
        return False

    with open(path.join(file + "/index.html"), 'w') as output:
        output.write(html)

    return True



###############
#     RUN     #
###############
if app_options["clean_output"]:
    try:
        rmtree(path.join(getcwd(), app_options["output_folder"]))
        print("Output folder cleaned")
    except:
        # TODO: false positive error?
        print("Error cleaning up output folder:" +
              getcwd() + app_options["output_folder"] )

parseContent()
