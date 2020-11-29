from jinja2 import Environment, select_autoescape

class jinja:
    env = Environment(autoescape=select_autoescape(
        enabled_extensions=('html', 'xml'),
        default_for_string=True,
    ))

    output_folder = "output/"
    template_folder = "templates/"

    

    def render_to_file(template,data):
        output = env.get_template(template_folder + template).render(data)
        with open(output_folder + "file","wb") as f:
            f.write(output)
        return output


