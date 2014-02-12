"Template support for jinja2"
from __future__ import absolute_import, division, print_function

import os
import jinja2


class TurboJinja(object):
    extension = "html"

    def __init__(self, extra_vars_func=None, options=None):
        self.get_extra_vars = extra_vars_func
        if options:
            self.options = options
        else:
            self.options = dict()

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
