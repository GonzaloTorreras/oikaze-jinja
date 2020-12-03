from markdown2 import markdown
from os import listdir, path, getcwd
from pathlib import Path
from shutil import rmtree, copytree
#import configparser # TODO: the whole config parser

from jinja2 import Environment, PackageLoader


import config_app
import config_site

app_options = config_app.app_options
site_options = config_site.site_options




# TODO: Organize all, move to class or module

###############
#  FUNCTIONS  #
###############


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


def splitAll(pa):
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


def outputF(filePath, data):
    global app_options
    global site_options

    if(data["slug"] != "/" and data["slug"] != "index" and data["slug"] != "home"):
        slug = data["slug"]
    else:
        slug = ""

    if type(filePath) == str:
        filePath = path.join(filePath)

    filePath = splitAll(filePath)
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
        outputFile = path.join(*filePath, slug)
    else:
        outputFile = path.join(*filePath)

    return outputFile


def parseFile(fileName):
    with open(path.join(fileName), 'r') as file:
        parsed_md = markdown(file.read(), extras=['metadata'])
    data = parsed_md.metadata
    data["body"] = parsed_md

    # default template to post
    if not "template" in data:
        data["template"] = "blog-post.html"

    return data


def parseContentFolder(allFiles):
    global app_options

    counter = 0
    env = loadJinjaEnv()

    for fileName in allFiles:
        counter += 1
        data = parseFile(fileName)
        html = buildContent(env, data)

        if html:
            #print(data)
            outputFile = outputF(fileName, data)

            if outputFile:

                if generateOutput(html, outputFile):
                    print(str(counter) + " " + fileName +
                        " processed to -> " + outputFile + "/index.html")
                else:
                    print(str(counter) + " " + "ERROR generating" +
                        outputFile + "/index.html")
            else:
                print("Error getting output folder for %s", fileName)
        
            
    # Generate listing pages


def loadJinjaEnv():
    global app_options

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


def buildContent(env, data):
    global site_options

    if "template" in data:
        template = data["template"]
    else:
        template = "base.html"  # TODO: add app setting to change name of default template name?

    try:
        render = env.get_template(template)
    except:
        print("Error, can't find the template: templates/" + template)
        return False
        
    try:
        r = render.render(content=data, globals=site_options)
    except:
        print("Error rendering")
        print(render)
        return False
    return r

def copyAssets(customFolder = False):
    if customFolder:
        orig = customFolder
    else:
        orig = app_options["assets_folder"]
    
    end = app_options["output_folder"] + "/" + orig.split("/")[-1]
    try:
        copytree(orig, end)
    except:
        print("Error copying the assets/static folder: " + orig + " -> " + end)

    print("Assets cloned")



def generateOutput(html, file):
    if str(file).startswith("/"):
        file = file[1:]
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


allFiles = getListOfFiles(app_options["content_folder"])
parseContentFolder(allFiles)
copyAssets()
print(str(allFiles))