import logging
import os
import sys

from google.appengine.dist import use_library
use_library('django', '1.2')

os.environ['DJANGO_SETTINGS_MODULE'] = 'django_settings'

# Tweak import path so that httplib2 (which lives in datasources) can be
# imported as httplib2 while the app is running.
# TODO(mihaip): move httplib2 (and oauth2 and python-twitter) into a third_party
# directory.
APP_DIR = os.path.abspath(os.path.dirname(__file__))
DATASOURCES_DIR = os.path.join(APP_DIR, 'datasources')
sys.path.insert(0, DATASOURCES_DIR)

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

import birdfeeder.handlers.update
import feedplayback.handlers

def main():
    application = webapp.WSGIApplication([
            ('/cron/feed-playback/advance', feedplayback.handlers.AdvanceCronHandler),
            ('/tasks/feed-playback/advance', feedplayback.handlers.AdvanceTaskHandler),

            ('/cron/bird-feeder/update', birdfeeder.handlers.update.UpdateCronHandler),
            ('/tasks/bird-feeder/update', birdfeeder.handlers.update.UpdateTaskHandler),
            ('/tools/bird-feeder/update-feed', birdfeeder.handlers.update.UpdateFeedToolHandler),
        ],
        debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
