import logging
import os

from django.conf import settings
from django.utils import simplejson
from django.template.loader import get_template
from django.template import Context
from google.appengine.ext import webapp

import base.constants

class BaseHandler(webapp.RequestHandler):
    def _render_template(self, template_file_name, template_values={}):
        # Even though we set the DJANGO_SETTINGS_MODULE environment variable in
        # both main.py and cron_tasks.py, there appear to be other app
        # entrypoints that cause it to get started without the environment
        # variable set. Since rendering templates is the only Django
        # functionality we actually need, as a workaround we set the environment
        # variable here.
        # TODO(mihaip): figure out why this is happening
        if 'DJANGO_SETTINGS_MODULE' not in os.environ:
            logging.error('DJANGO_SETTINGS_MODULE was not in the environment')
            os.environ['DJANGO_SETTINGS_MODULE'] = 'django_settings'

        # Temporarily insert the template's directory into the template path,
        # so that templates in the same directory may be included without
        # needing their full path
        previous_template_paths = list(settings.TEMPLATE_DIRS)
        template_directory = os.path.join(
            settings.TEMPLATE_DIRS[0], os.path.dirname(template_file_name))
        settings.TEMPLATE_DIRS += (template_directory,)

        template = get_template(template_file_name)
        template_values.update(base.constants.CONSTANTS)
        rendered_template = template.render(Context(template_values))
        # Django templates are returned as utf-8 encoded by default
        if not isinstance(rendered_template, unicode):
          rendered_template = unicode(rendered_template, 'utf-8')

        # Restore template path.
        settings.TEMPLATE_DIRS = previous_template_paths

        return rendered_template

    def _write_template(
            self,
            template_file_name,
            template_values={},
            content_type='text/html',
            charset='UTF-8'):
        self.response.headers['Content-Type'] = '%s; charset=%s' % (content_type, charset)
        self.response.headers['X-Content-Type-Options'] = 'nosniff'
        self.response.out.write(
            self._render_template(template_file_name, template_values))

    def _write_error(self, error_code):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.set_status(error_code)

    def _write_not_found(self):
        self._write_error(404)

    def _write_input_error(self, error_message):
        self._write_error(400)
        self.response.out.write('Input error: %s' % error_message)

    def _write_json(self, obj):
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(simplejson.dumps(obj))
