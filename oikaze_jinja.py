import socketserver
import http.server
from markdown2 import markdown
from os import listdir, path, getcwd
from pathlib import Path
from shutil import rmtree, copytree
#import configparser # TODO: the whole config parser

from jinja2 import Environment, PackageLoader, select_autoescape

import htmlmin # html minifier

import config_app
import config_site

app_options = config_app.app_options
site_options = config_site.site_options



class OikazeJinja(object):

    def __init__(self):
        self.app_options = app_options
        self.site_options = site_options
        self.allFiles = self.getListOfFiles()
        self.env = self.loadJinjaEnv()
        
        # exec
        self.clearOutputFolder()
        
        self.parseContentFolder(self.allFiles)
        self.copyAssets()


    def getListOfFiles(self, dirName = False):

        if not dirName:
            dirName = self.app_options['content_folder']

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
                allFiles = allFiles + self.getListOfFiles(fullPath)
            else:
                allFiles.append(fullPath)

        self.allFiles = allFiles
        return allFiles


    def splitAll(self,pa):
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


    def outputF(self, filePath, data):
        global app_options
        global site_options

        if(data['slug'] != "/" and data['slug'] != "index" and data['slug'] != "home"):
            slug = data['slug']
        else:
            slug = ""

        if type(filePath) == str:
            filePath = path.join(filePath)

        filePath = self.splitAll(filePath)
        #replace first folder (content/ by default) for output folder (output/ by default)
        filePath[0] = app_options['output_folder']

        # Add lang slug if needed
        if "lang_slugs" in site_options:
            if data['lang'] in site_options['lang_slugs']:
                filePath.insert(1, site_options['lang_slugs'][data['lang']])
            else:
                print("site_options[lang_slug] is missing lang: " + data['lang'])
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


    def parseFile(self,fileName):
        with open(path.join(fileName), 'r') as file:
            parsed_md = markdown(file.read(), extras=['metadata'])
        data = parsed_md.metadata
        data['body'] = parsed_md

        # default template to post
        if not "template" in data:
            data['template'] = self.app_options['template_default']

        return data


    def parseContentFolder(self,allFiles):
        global app_options

        counter = 0

        for fileName in allFiles:
            counter += 1
            data = self.parseFile(fileName)
            html = self.buildContent(data)

            if html:
                #print(data)
                outputFile = self.outputF(fileName, data)

                if outputFile:

                    if self.generateOutput(html, outputFile):
                        print(str(counter) + " " + fileName +
                            " processed to -> " + outputFile + "/index.html")
                    else:
                        print(str(counter) + " " + "ERROR generating" +
                            outputFile + "/index.html")
                else:
                    print("Error getting output folder for %s", fileName)
            
                
        # Generate listing pages


    def loadJinjaEnv(self):

        env = Environment(
            loader=PackageLoader('oikaze_jinja', self.app_options['template_folder']),
            autoescape=select_autoescape([
                #'html',
                'xml'
            ]),
            auto_reload=True,
            cache_size=0 #disable cache so it rebuilts when watching for changes
        )
        env.trim_blocks = True
        env.lstrip_blocks = True
        env.strip_trailing_newlines = True

        # TODO: Test in depth if this parser of jinja2 extra config works
        if "jinja2_env" in app_options:
            for k, v in self.app_options['jinja2_env']:
                env[k] = v

        return env


    def buildContent(self, data):

        if "template" in data:
            template = data['template']
        else:
            template = "base.html"  # TODO: add app setting to change name of default template name?

        try:
            render = self.env.get_template(template)
        except:
            print("Error, can't find the template: templates/" + template)
            return False
            
        try:
            r = render.render(content=data, globals=self.site_options)
        except:
            print("Error rendering")
            print(render)
            return False
        #minify HTML
        
        r = htmlmin.minify(r,
                    remove_empty_space=True
                    , remove_all_empty_space=True
                    , remove_comments=True)
        
        return r

    def clearOutputFolder(self):
        if self.app_options['clean_output']:

            output_folder = self.app_options['output_folder']
            
            if self.app_options['output_folder'][1] != "/":
                output_folder = "/" + output_folder

            try:
                rmtree(path.join(getcwd(), self.app_options['output_folder']))
                print("Output folder cleaned")
                return True
            except:
                # TODO: false positive error?
                print("Error cleaning up output folder:" +
                      getcwd() + self.app_options['output_folder'])
        return False


    def copyAssets(self,customFolder = False):
        if customFolder:
            orig = customFolder
        else:
            orig = self.app_options['assets_folder']
        
        end = self.app_options['output_folder'] + "/" + orig.split("/")[-1]
        try:
            copytree(orig, end)
        except:
            print("Error copying the assets/static folder: " + orig + " -> " + end)

        print("Assets cloned")


    def generateOutput(self, html, file):
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

if __name__ == "__main__":
    import sys
    args = [x.replace("--","") for x in sys.argv[1:] ]
    print(args)
    OikazeJinja()

    if "http" in args:

        PORT = 8000
        DIRECTORY = "output"
        class Handler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=DIRECTORY, **kwargs)

        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print("serving at port", PORT)
            httpd.serve_forever()
