import unittest
import os
import shutil
import json
from urlparse import urlparse
from StringIO import StringIO

import sys; print sys.modules.keys()

# Configure our app to use the testing databse
# os.environ["CONFIG_PATH"] = "tuneful.config.TestingConfig"

from tuneful import app
from tuneful import models
from tuneful.utils import upload_path
from tuneful.database import Base, engine, session
from tuneful.api import stripUnicode

client = app.test_client()

# Set up the tables in the database
Base.metadata.create_all(engine)

# Create folder for test uploads
# os.mkdir(upload_path())

for x in range(1,10):    

    post_response = client.post('/api/songs/post',
                               data=json.dumps({"song_name":"songname"+str(x),"filename":"testfilename"+str(x),"song_id":x}),
                               content_type='application/json',
                               follow_redirects=True,
                               headers=[("Accept", "application/json")]) # need this header or the decorator will send 406