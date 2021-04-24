title: Post from notion
description: Desc
slug: notion
lang: es
date: 04/10

# ES - Post 

# How Hubspot handles and order dependencies (CSS & JS)

Status: To review

I wanted to optimize and speed up Hubspot as much as possible, so I have dug pretty hard on how Hubspot CMS handles all the dependencies and in which order it places all the CSS and JS that are attached to a page from different scopes.
We will leave the reverse engineering of`{{ standard_header_includes }}` for a later post #TODO#.

## TL;DR:

I have used different snippets to test the different locations where CSS or JS can be called, what are the default files that Hubspot includes and how they are ordered. The `{% require_* %}` generate a enqueue list that follows this order:

### CSS

- Hardcoded tags in the template before the `standard_header_includes` (without wrapper).
- `{% require_css %}` from the template head.
- Global settings with `{% require_css %}`
- `{% require_css %}` from page head HTML (in the content editor &#8594; advanced settings).
- `{% require_css %}` from the template after the `standard_header_includes`.
- `{% require_css %}` from the modules in cascading.
- HTML from the global settings **without** the wrapper `{% require_css %}`.
- HTML from the page head without the wrapper.

### JS

We can see the same patern for JS:

- Wrapped JS from the global settings.
- Wrapped JS from page head.
- Wrapped JS from page head.
- Wrapped JS from the template.

## How I did it

### Global settings:

```html
<!-- global settings -->
{% require_css %}
  <!-- require_css from global settings -->
{% end_require_css %}
{% require_js %}
  <!-- require_js from global settings -->
{% end_require_js %}
```

### Template:

3 modules in total, although I am using 2 instances of the same one.

```html
[...]
<meta name="description" content="{{ page_meta.meta_description }}">
<link rel="stylesheet" id="template-hardcoded" src="(unknown)">
{{ require_css(get_asset_url("./style/style.css")) }}
{% require_css %}
  <!-- require_css from template head before standard_header_includes -->
{% end_require_css %}
{{ standard_header_includes }}
<!-- template head -->
{% require_css %}
  <!-- require_css from template head after standard_header_includes -->
{% end_require_css %}
{% require_js %}
  <!-- require_js from template head -->
{% end_require_js %}
</head>
<body>
{% module "hero" path="./modules/test" label="Test" %}
{% module "module2" path="./modules/test2" label="Test2" %}
{% module "module3" path="./modules/test2" label="Test3" %}
{{ standard_footer_includes }}
```

### Modules:

Inside the modules I have filled the CSS and JS tab and also added the following snippet to the HTML:

```html
<!-- page head -->
{% require_css %}
  <!-- require_css from module{2} -->
{% end_require_css %}
{% require_js %}
  <!-- require_js from module{2} -->
{% end_require_js %}
```

### Page settings:

I attached a CSS file to the page and used the following snippet in the head (this is the setting you can find in the page content behind the *advanced settings*):

```html
<!-- page head -->
{% require_css %}
  <!-- require_css from page head -->
{% end_require_css %}
{% require_js %}
  <!-- require_js from template head -->
{% end_require_js %}
```

## The result

```html
	<meta name="description" content="desc">
	<link rel="stylesheet" id="template-hardcoded" src="(unknown)">
	<meta property="og:description" content="desc">
	<meta property="og:title" content="Speed tests">
	<meta name="twitter:description" content="desc">
	<meta name="twitter:title" content="Speed tests">
	<style>
	a.cta_button{-moz-box-sizing:content-box !important;-webkit-box-sizing:content-box !important;box-sizing:content-box !important;vertical-align:middle}.hs-breadcrumb-menu{list-style-type:none;margin:0px 0px 0px 0px;padding:0px 0px 0px 0px}.hs-breadcrumb-menu-item{float:left;padding:10px 0px 10px 10px}.hs-breadcrumb-menu-divider:before{content:'›';padding-left:10px}.hs-featured-image-link{border:0}.hs-featured-image{float:right;margin:0 0 20px 20px;max-width:50%}@media (max-width: 568px){.hs-featured-image{float:none;margin:0;width:100%;max-width:100%}}.hs-screen-reader-text{clip:rect(1px, 1px, 1px, 1px);height:1px;overflow:hidden;position:absolute !important;width:1px}
	</style>
	<link rel="stylesheet" href="[...]/hub_generated/template_assets/[...]/css/style.css">
	<!-- require_css from template head before standard_header_includes -->
	<!-- require_css from global settings -->
	<!-- require_css from page head  -->
	<!-- require_css from template head after standard_header_includes -->
	<link rel="stylesheet" href="[...]/hub_generated/module_assets/[...]/module_44280299560_test.css">
	<!-- require_css from module -->
	<link rel="stylesheet" href="[...]/hub_generated/module_assets/[...]/module_44359556170_test2.min.css">
	<!-- require_css from module2 -->
	<!-- require_css from module2 -->
	<link rel="canonical" href="...">
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<!-- global settings -->
	<meta property="og:url" content="[...]">
	<meta name="twitter:card" content="summary">
	<meta http-equiv="content-language" content="en">
	<link rel="stylesheet" href="[...]/template_assets/[...]/css_from_page_head.css">
	<!-- page head -->
	<meta name="generator" content="HubSpot">
	<script src="https://js.hscollectedforms.net/collectedforms.js" type="text/javascript" id="CollectedForms-19609909" crossorigin="anonymous" data-leadin-portal-id="19609909" data-leadin-env="prod" data-loader="hs-scriptloader" data-hsjs-portal="19609909" data-hsjs-env="prod" data-hsjs-hublet="na1"></script>
	<script src="https://js.hs-banner.com/19609909.js" type="text/javascript" id="cookieBanner-19609909" data-cookieconsent="ignore" data-loader="hs-scriptloader" data-hsjs-portal="19609909" data-hsjs-env="prod" data-hsjs-hublet="na1"></script>
	<script src="https://js.hs-analytics.net/analytics/1617439200000/19609909.js" type="text/javascript" id="hs-analytics"></script>
	<script type="text/javascript" referrerpolicy="no-referrer-when-downgrade" async="" src="https://app.hubspot.com/content-tools-menu/api/v1/tools-menu/has-permission?portalId=19609909&amp;callback=jsonpHandler"></script>
</head>
<body>
	[...]
	<script>
	(function () {
	    window.addEventListener('load', function () {
	        setTimeout(function () {
	            var xhr = new XMLHttpRequest();
					    [...]
	    });
	})();
	</script>
	<!-- require_js from global settings -->
	<!-- require_js from page head -->
	<script>console.log("Test from page head");</script>
	<!-- require_js from template -->
	<script>console.log("Test from template");</script>
	<script>
	if (typeof hsVars !== 'undefined') { hsVars['language'] = 'en'; }
	</script>
	<script src="/hs/hsstatic/cos-i18n/static-1.27/bundles/project.js"></script>
	<script src="[...]/hub_generated/module_assets/[...]/module_44280299560_test.min.js"></script>
	<!-- require_js from module -->
	<script src="[...]/hub_generated/module_assets/[...]/module_44359556170_speed-test.min.js"></script>
	<!-- require_js from module2 -->
	<!-- Start of HubSpot Analytics Code -->
	<script type="text/javascript">
	var _hsq = _hsq || [];
	_hsq.push(["setContentType", "standard-page"]);
	[...]
	}]);
	</script>
	<script type="text/javascript" id="hs-script-loader" async="" defer="" src="/hs/scriptloader/19609909.js"></script>
	<!-- End of HubSpot Analytics Code -->
	<script type="text/javascript">
	var hsVars = {
	    ticks: 1617439431214,
	    [...]
	}
	</script>
	<script defer="" src="/hs/hsstatic/HubspotToolsMenu/static-1.99/js/index.js"></script>
	<iframe owner="archetype" title="archetype" style="display: none; visibility: hidden;"></iframe>
```

---

First we find the description `<meta>` followed by our hardcoded `<link>` .  After that is where we really see what comes from the `{{ standard_header_includes }}`.

There are some `<meta>` tags for social networks and an injected `<style>` tag with some default HS CSS, related to cta_button (even if our test page had NO CTA in place) and default components such as hs-breadcrumb-menu, etc.

```html
<meta name="description" content="desc">
<link rel="stylesheet" id="template-hardcoded" src="(unknown)">
<meta property="og:description" content="desc">
<meta property="og:title" content="Speed tests">
<meta name="twitter:description" content="desc">
<meta name="twitter:title" content="Speed tests">
<style>
a.cta_button{-moz-box-sizing:content-box !important;-webkit-box-sizing:content-box !important;box-sizing:content-box !important;vertical-align:middle}.hs-breadcrumb-menu{list-style-type:none;margin:0px 0px 0px 0px;padding:0px 0px 0px 0px}.hs-breadcrumb-menu-item{float:left;padding:10px 0px 10px 10px}.hs-breadcrumb-menu-divider:before{content:'›';padding-left:10px}.hs-featured-image-link{border:0}.hs-featured-image{float:right;margin:0 0 20px 20px;max-width:50%}@media (max-width: 568px){.hs-featured-image{float:none;margin:0;width:100%;max-width:100%}}.hs-screen-reader-text{clip:rect(1px, 1px, 1px, 1px);height:1px;overflow:hidden;position:absolute !important;width:1px}
</style>
```

Then we see a couple of require_css being processed. Those are the two first require_css that we placed **before** the `{{ standard_header_includes }}`, one with the `{{ require_css() }}` function format and the other as the `{% require_css %}` tag.

```html
<link rel="stylesheet" href="[...]/hub_generated/template_assets/[...]/css/style.css">
<!-- require_css from template head before standard_header_includes -->
```

Then we find that the next CSS is the one you place in the global head settings. I think this makes sense because with the new coded templates and themes you have much more control about the HTML markup and therefore you can place your "general" styles right before the standard_header_includes. Now you have the potential use of fragmented global settings based on the domains to overwrite styles which in combinations with CSS variables can do some wonderful *easy peasy* brand customizations within your themes.  

```html
<!-- require_css from global settings -->
```

What surprised me is that the `{% require_css %}` from the **page head** (when you are editing the page content in advance settings) came before the one from the template (after standard_header_includes). While I understand why this happens, I think it's not a good approach as a template `require_css` will be more general than one contained in the page head. However, it shouldn't be a big deal as `{% require_css %}` on templates can be placed at your own discretion (before or after the standard_header_includes) and it is unlikely to mess up anything because you have full control over the HTML markup. Despite this, it definitely is something to keep in mind (although now I am curious about old dnd templates &#x1f601;).

```html
<!-- require_css from page head  -->
<!-- require_css from template head after standard_header_includes -->
```

After that, we find the CSS file that comes from the CSS tab module followed by the `{% require_css %}` inside its HTML tab. You can imagine that any other module added to the page will follow here using the same pattern. It makes sense, as the HTML tab will be processed before the next module and therefore added to the queue right before the next module goes in place. It is worth mentioning that the CSS tab file is injected just once even if you have more than one instance, but you probably already knew that.

Also, you may have noticed how the first module `test.css` is not minified while second module test2.min.css is. This is because in the first one there is one CSS selector empty (without properties). While in the second module has a selector with a font-size property. There are several things that break the CSS minifier (and the combinator).  Something I will go in-depth in a different post. #TODO#

```html
<link rel="stylesheet" href="[...]/hub_generated/module_assets/[...]/module_44280299560_test.css">
<!-- require_css from module -->
<link rel="stylesheet" href="[...]/hub_generated/module_assets/[...]/module_44359556170_test2.min.css">
<!-- require_css from module2 -->
<!-- require_css from module2 -->
```

Then we find some meta tags of the page. Whatever you placed inside the global settings (without any `{% require_* %}` wrapper, like the `<!-- global settings -->`) is located in-between.

```html
<link rel="canonical" href="[...]">
<meta name="viewport" content="width=device-width, initial-scale=1">
<!-- global settings -->
<meta property="og:url" content="[...]">
<meta name="twitter:card" content="summary">
<meta http-equiv="content-language" content="en">
```

Here we can see that the attached CSS from the *Page stylesheets* setting (in the page editor, do not confuse with the page head) is placed right before what you place in your page head setting (without wrappers). So those would be the latest to load (unless you have in your template or modules not wrapped tags).

```html
<link rel="stylesheet" href="[...]/template_assets/[...]/css_from_page_head.css">
<!-- page head -->
```

We finish the `</head>` tag with some Hubspot related javascript. It is worth mentioning that just one of the 4`<script>` tags is actually async, leaving the others to render block your content without even defer &#x1f644;.

```html
<meta name="generator" content="HubSpot">
<script src="https://js.hscollectedforms.net/collectedforms.js" type="text/javascript" id="CollectedForms-19609909" crossorigin="anonymous" data-leadin-portal-id="19609909" data-leadin-env="prod" data-loader="hs-scriptloader" data-hsjs-portal="19609909" data-hsjs-env="prod" data-hsjs-hublet="na1"></script>
<script src="https://js.hs-banner.com/19609909.js" type="text/javascript" id="cookieBanner-19609909" data-cookieconsent="ignore" data-loader="hs-scriptloader" data-hsjs-portal="19609909" data-hsjs-env="prod" data-hsjs-hublet="na1"></script>
<script src="https://js.hs-analytics.net/analytics/1617439200000/19609909.js" type="text/javascript" id="hs-analytics"></script>
<script type="text/javascript" referrerpolicy="no-referrer-when-downgrade" async="" src="https://app.hubspot.com/content-tools-menu/api/v1/tools-menu/has-permission?portalId=19609909&amp;callback=jsonpHandler"></script>
</head>
```

I didn't place in the HTML module tab any style or script without the wrappers because it is very easy to imagine that those will appear within the HTML module on the page. 

Basically, the require_css will be enqueue when it get processed, therefor a require_css in a module is processed sonner than one near the footer.

## Conclusion

You may think that you basically want to wrap all your `<style>` and `<script>` tags with the wrapper `{% require_* %}` so it's placed correctly by Hubspot. And while you are correct that most of the time that would do, you will find a better approach to achieve the most performant website hosted in Hubspot CMS later in this post series.

¡Subscribe so you don't miss out!
