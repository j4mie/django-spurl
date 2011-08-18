# Spurl

**Super URLs for Django**

               .=.,
              ;c =\
            __|  _/
          .'-'-._/-'-._
         /..   ____    \
        /  {% spurl %}  \
       (  / \--\_>/-/'._ )
        \-;_/\__;__/ _/ _/
         '._}|==o==\{_\/
          /  /-._.--\  \_
         // /   /|   \ \ \
        / | |   | \;  |  \ \
       / /  | :/   \: \   \_\
      /  |  /.'|   /: |    \ \
      |  |  |--| . |--|     \_\
      / _/   \ | : | /___--._) \
     |_(---'-| >-'-| |       '-'
            /_/     \_\



**Spurl** is a Django template library for manipulating URLs. It's built on top of Zachary Voase's excellent [urlobject](https://github.com/zacharyvoase/urlobject/).

**Spurl is currently in alpha and is probably not ready for production use**.

## Installation

You can install Spurl from PyPI:

    pip install django-spurl

Add `spurl` to your `INSTALLED_APPS`:

    INSTALLED_APPS = (
        ...
        'spurl',
        ...
    )

Finally, whenever you want to use Spurl in a template, you need to load its template library:

    {% load spurl %}

## Usage

Spurl is **not** a replacement for Django's built-in `{% url %}` template tag. It is a general-purpose toolkit for manipulating URL components in templates. You can use it alongside `{% url %}` if you like (see below).

Spurl provides a single template tag, called (surprisingly enough), `spurl`. You call it with a set of `key=value` keyword arguments, which are described fully below.

To show some of the features of Spurl, we'll go over a couple of simple example use cases.

### Adding query parameters to URLs

Say you have a list of external URLs in your database. When you create links to these URLs in a template, you need to add a `referrer=mysite.com` query parameter to each. The simple way to do this might be:

    {% for url, title in list_of_links %}
        <a href="{{ url }}?referrer=mysite.com">{{ title }}</a>
    {% endfor %}

The problem here is that you don't know in advance if the URLs stored in your database *already* have query parameters. If they do, you'll generate malformed links like `http://www.example.com?foo=bar?referrer=mysite.com`.

Spurl can fix this. Because it knows about the components of a URL, it can add parameters onto an existing query, if there is one.

    {% for url, title in list_of_links %}
        <a href="{% spurl base=url add_query="referrer=mysite.com" %}">{{ title }}</a>
    {% endfor %}

Note that **when you pass a literal string to Spurl, you have to wrap it in double quotes**. If you don't, Spurl will assume it's a variable name and try to look it up in the template's context.

### SSL-sensitive external URLs.

Suppose your site needs to display a gallery of images, the URLs of which have come from some third-party web API. Additionally, imagine your site needs to run both in secure and non-secure mode - the same content is available at both `https` or `http` URLs (depending on whether a visitor is logged in, say). Some browsers will complain loudly (displaying "Mixed content warnings" to the user) if the page being displayed is `https` but some of the assets are `http`. Spurl can fix this.

    {% for image_url in list_of_image_urls %}
        <img src="{% spurl base=image_url secure=request.is_secure %}" />
    {% endfor %}

This will take the image URL you supply and replace the scheme component (the `http` or `https` bit) with the correct version, depending on the return value of `request.is_secure()`. Note that the above assumes you're using a `RequestContext` so that `request` is available in your template.

### Using alongside {% url %}

Notice that Spurl's functionality doesn't overlap with Django's built-in `{% url %}` tag. Spurl doesn't know about your urlconf, and doesn't do any URL reversing. In fact, Spurl is mostly useful for manipulating **external** URLs, rather than URLs on your own site. However, you can easily use Spurl with `{% url %}` if you need to. You just have to use the `as` keyword to put your reversed URL in a template variable, and then pass this to Spurl. As it's a relative path (rather than a full URL) you should pass it using the `path` argument. For example, say you want to append some query parameters to a URL on your site:

    {% url your_url_name as my_url %}
    <a href="{% spurl path=my_url query="foo=bar&bar=baz" %}">Click here!</a>

### Available arguments

Below is a full list of arguments that Spurl understands.

#### base

If you pass a `base` argument to Spurl, it will parse its contents and use this as the base URL upon which all other arguments will operate. If you *don't* pass a `base` argument, Spurl will generate a URL from scratch based on the components that you pass in separately.

#### scheme

Set the scheme component of the URL. Example:

    {% spurl base="http://example.com" scheme="ftp" %}

This will return `ftp://example.com`

#### host

Set the host component of the URL. Example:

    {% spurl base="http://example.com/some/path/" host="google.com" %}

This will return `http://google.com/some/path/`

#### path

Set the path component of the URL. Example:

    {% spurl base="http://example.com/some/path/" path="/different/" %}

This will return `http://example.com/different/`

#### add_path

Append a path component to the existing path. You can add multiple `add_path` calls, and the results of each will be combined. Example:

    {% spurl base=STATIC_URL add_path="javascript" add_path="lib" add_path="jquery.js" %}

This will return `http://cdn.example.com/javascript/lib/jquery.js` (assuming `STATIC_URL` is set to `http://cdn.example.com`)

#### fragment

Set the fragment component of the URL. Example:

    {% spurl base="http://example.com" fragment="myfragment" %}

This will return `http://example.com/#myfragment`

#### port

Set the port component of the URL. Example:

    {% spurl base="http://example.com/some/path/" port="8080" %}

This will return `http://example.com:8080/some/path/`

#### query

Set the query component of the URL. Example:

    {% spurl base="http://example.com/" query="foo=bar&bar=baz" %}

This will return `http://example.com/?foo=bar&bar=baz`

The `query` argument can also be passed a dictionary from your template's context.

    # View
    def my_view(request):
        my_query_params = {'foo': 'bar', 'bar': 'baz'}
        return render(request, 'path/to/template.html', {'my_query_params': my_query_params})

    # Template
    {% spurl base="http://example.com/" query=my_query_params %}

This will return `http://example.com/?foo=bar&bar=baz`

Finally, you can pass individual template variables to the query. To do this, Spurl uses Django's template system. For example:

    {% spurl base="http://example.com/" query="foo={{ variable_name }}" %}

#### add_query

Append a set of parameters to an existing query. If your base URL might already have a query component, this will merge the existing parameters with your new ones. Example:

    {% spurl base="http://example.com/?foo=bar" add_query="bar=baz" %}

This will return `http://example.com?foo=bar&bar=baz`

You can add multiple `add_query` calls, and the results of each will be combined:

    {% spurl base="http://example.com/" add_query="foo=bar" add_query="bar=baz" %}

This will return `http://example.com?foo=bar&bar=baz`

Like the `query` argument above, the values passed to `add_query` can also be dictionaries, and they can contain Django template variables.

#### set_query

Appends a set of parameters to an existing query, overwriting existing parameters with the same name. Otherwise uses the exact same syntax as `add_query`.

#### secure

Control whether the generated URL starts with `http` or `https`. The value of this argument can be a boolean (`True` or `False`), if you're using a context variable. If you're using a literal argument here, it must be a quoted string. The strings `"True"` or `"on"` (case-insensitive) will be converted to `True`, any other string will be converted to `False`. Example:

    {% spurl base="http://example.com/" secure="True" %}

This will return `https://example.com/`

#### autoescape

By default, Spurl will escape its output in the same way as Django's template system. For example, an `&` character in a URL will be rendered as `&amp;`. You can override this behaviour by passing an `autoescape` argument, which must be either a boolean (if passed from a template variable) or a string. The strings `"True"` or `"on"` (case-insensitive) will be converted to `True`, any other string will be converted to `False`.

#### Building a URL without displaying it

Like Django's `{% url %}` tag, Spurl allows you to insert the generated URL into the template's context for later use. Example:

    {% spurl base="http://example.com" secure="True" as secure_url %}
    <p>The secure version of the url is {{ secure_url }}</p>

## (Un)license

This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or distribute this
software, either in source code form or as a compiled binary, for any purpose,
commercial or non-commercial, and by any means.

In jurisdictions that recognize copyright laws, the author or authors of this
software dedicate any and all copyright interest in the software to the public
domain. We make this dedication for the benefit of the public at large and to
the detriment of our heirs and successors. We intend this dedication to be an
overt act of relinquishment in perpetuity of all present and future rights to
this software under copyright law.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

For more information, please refer to <http://unlicense.org/>

## Artwork credit

Superman ASCII art comes from <http://ascii.co.uk/art/superman>
