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
    "template_folder": "templates",
    "template_default": "blog-post.html",
    "assets_folder": "templates/assets",
    "jinja2_conf": {}

}
