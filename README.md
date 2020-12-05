# oikaze-jinja
(Work in progress) Static site generator based on Jinja2 and TailwindCSS.
Right now is more like a POC than a real product.

## Features
- [X] Agnostic jinja2 template parser.
- [X] Flexible for pages, blog, or any other use case.
- [X] Support for YAML header for each element/page, (I would like to expand in the future to others too).
- [X] Beautiful slug generator: blog/my-blog-post.html -> blog/my-blog-post/

## In progress
- [ ] Convert to a full class/module to make it more clear and independent of each app/web.
## In the pipe
- [ ] Help to autogenerate listings (inside app_config, define the YAML prop to check like `{"category":"blog-category.html"}` and, the folder slugs + the template also for general listings (such `/blog`). `{"listings":{"/blog":"blog-listing.html"} }`. Current status: hardcoded.
- [ ] Improve and automate how tailwindcss is generating the files (current status: manually).
- [ ] Create workflows for autodeploy in Netlify and github.
- [ ] Create a system to work based on modules so you can have Jinja2 custom modules (with tailwind or whatever you want) and call those form the "body" of each post/page.
- [ ] Add support to easily override templates from custom app folder.
- [ ] Expand usability on config editor/generator.

## Random ideas to check viability:
- [ ] Add support to pure JSON data.
- [ ] Add Hubspot templates converter.
- [ ] Hubspot CMS to static site deploy?

# How it works
`/content` folder will have one file for each page/post you want to publish.
Basic example:
```markdown
title: My post entry
slug: my-post-entry
date: 4/08/20
template: blog-post.html

# This is my post content

It supports markdown, and HTML.
Right now its parsed using <a href="https://github.com/trentm/python-markdown2">markdown2</a> lib
```
You probably already noticed, but let me explain anyway. This file has two main parts. The first one, defines the metadata. It uses a basic YAML format that will be converted and send it to Jinja parser inside the `content` variable.
<a id="post-example"></a>
```yaml
title: My post entry
slug: my-post-entry
date: 4/08/20
lang: en
template: blog-post.html
```
Will be available inside the template like:
```jinja
{{ content.title }}
{{ content.slug }}
{{ content.date }}
{{ content.lang }}
{{ content.template }}

```
<b style="font-size:.9em">NOTE</b>: While the default templates expects `title`, `slug`, `date`, `lang` and `body`. The only really statics are `slug` and `body`(which will be generated in the second part of the file. If you are working on your own templates, you can use whatever metadata you want, or even expand the defaults with extra data you can find useful, for example `category: my-cat`. 


The second one will be parsed from Markdown or pure HTML to `content.body`
```markdown
# This is my post content

It supports markdown, and HTML.
Right now its parsed using <a href="https://github.com/trentm/python-markdown2">markdown2</a> lib
```

The app will iterate each file inside `content/` (can be renamed with `config_app['content_folder']`). It will grab the data inside as described, render to jinja with the selected template in the YAML header `template: my-template.html`. It will look up for the template inside the folder `/templates` (once again, it can be customized with `config_app['template_folder']`), if no `template` property is provided will use the fallback to `base.html` (which, can be customized in `config_app['base_template']`).
##### TODO: config_app['base_template'] is actually not yet implemented.
Finally will write the output HTML to the `/output` folder (`config_app['output_folder']`) following the next logic:
First check if `lang` is provided in the YAML header and find the defined slug in `config_site.py`.
For example given this config:
<a id="example-lang_slugs"></a>
```python
    ...
    "lang_slugs": {
        "en": "",
        "es": "es"
    },
    ...
```
It will output `/es/` for `lang: es`, but if not provided `YAML-lang` or `lang: en` it will use `/` as main lang.

It will be followed by the actual folder path inside `content/`. For example, given the file `content/page-1/blog/file.md`, it will output `page-1/blog/file/`, and will finally concatenate with the slug provided in `YAML-slug` header.
#### Summary:
`{{ config_site.lang_slugs[ {{ content.lang }} ] }}` / `{{ folder/structure/inside/content }}` / `{{ YAML-slug }}`/

Example:
- We are using the `lang_slugs` configuration that we showed before [here](#example-lang_slugs)
- We are using the [post example](#post-example), inside `content/blog/en.my-post.md`.
- We are using a translated version of the post as `content/blog/es.my-post.md`. And the file will be almost the same but swapping the YAML `lang: en` to `lang: es`.

We will have an output folder like this:
```sh
output/
    blog/
        my-post-entry/
            index.html
    es/
        blog/
            my-post-entry/
                index.html
```
#### the URL ends up being site.com/blog/my-post-entry and site.com/es/blog/my-post-entry. Notice that as we just used the same slug for ES translated post it will have the same, but probably you will translate it too.

## How to use
As it current POC status you will need: `config_app.py`,`config_app.py` and `oikaze_jinja.py`. If you want to use tailwind you want to probably have a config too so you can use: `tailwind.config.js` or [generate your own](https://tailwindcss.com/docs/installation#create-your-configuration-file).
Put them in your project folder.
Create (or copy)` templates` folder, `output` folder and `content` folder (those names can be change in the  `app_config.py`).
```
/
 /content/
 /templates/
 /output/
 - config_app.py
 - config_site.py
 - oikaze_jinja.py
```

From here you can now:
- Populate your content folder with all the post and pages you want to publish.
- Customize `config_site.py` with your desirable options.
- Customize your templates as you like.

## Run!
`python oikaze_jinja.py`

If you want to debug locally you can run a basic HTTP server with:
`python3 -m http.server --directory output/`

##### TODO: Add commands to the app, like the HTTP server.

If using **tailwind** you can run it manually (for now):
`NODE_ENV=production npx tailwindcss-cli@latest build ./templates/assets/css/style.css -o ./output/assets/css/style.css`

**NOTE**: You will need to edit the paths with your desires.
##### TODO: Run tailwind within Python process. In the future it will probably run for each module/block?