"Template support for jinja2"
from __future__ import absolute_import, division, print_function

import os
import inspect
import jinja2
from bazman import templatetags


def is_mod_function(mod, func):
    return inspect.isfunction(func) and inspect.getmodule(func) == mod


def list_functions(mod):
    return [func for func in mod.__dict__.itervalues()
            if is_mod_function(mod, func)]


class TurboJinja(object):
    extension = "html"
    templatetags = None

    def __init__(self, extra_vars_func=None, options=None):
        self.get_extra_vars = extra_vars_func
        if options:
            self.options = options
        else:
            self.options = dict()

        self.__auto_register_module(templatetags)

    def __auto_register_module(self, module):
        self.templatetags = list_functions(module)

    def load_template(self, template_name):
        """template_name == dotted.path.to.template (without .ext)

        Searches for a template along the Python path.

        Template files must end in ".html" and be in legitimate packages.
        """

        divider = template_name.rfind(".")
        if divider > -1:
            package = template_name[0:divider]
            basename = template_name[divider+1:]
        else:
            raise ValueError("All templates must be in a package")
        templates_path = package.replace(".", os.sep)
        template_loader = jinja2.FileSystemLoader(searchpath=templates_path)
        template_env = jinja2.Environment()
        if self.templatetags:
            for filt in self.templatetags:
                template_env.filters[filt.__name__] = filt
        template_env.loader = template_loader
        template_obj = template_env.get_template(
            '%s.%s' % (basename, self.extension)
        )
        return template_obj

    def render(self, info, format="html", fragment=False, template=None):
        render_vars = info

        if callable(self.get_extra_vars):
            render_vars.update(self.get_extra_vars())

        tclass = self.load_template(template)

        return tclass.render(**render_vars)
