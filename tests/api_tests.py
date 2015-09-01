import unittest
import os
import shutil
import json
from urlparse import urlparse
from StringIO import StringIO

import sys; print sys.modules.keys()

# Configure our app to use the testing databse
os.environ["CONFIG_PATH"] = "tuneful.config.TestingConfig"

from tuneful import app
from tuneful import models
from tuneful.utils import upload_path
from tuneful.database import Base, engine, session
from tuneful.api import stripUnicode


class TestAPI(unittest.TestCase):
    """ Tests for the tuneful API """

    def setUp(self):
        """ Test setup """
        self.client = app.test_client()

        # Set up the tables in the database
        Base.metadata.create_all(engine)

        # Create folder for test uploads
        os.mkdir(upload_path())
        
    def testPostSong(self):
       """ This test posts a simple json record to the post endpoint """

       post_response = self.client.post('/api/songs/post',
                                   data=json.dumps({"song_id":"8" ,"song_name":"songname8","file_name":"filename8","file_id":"8"}),
                                   content_type='application/json',
                                   follow_redirects=True,
                                   headers=[("Accept", "application/json")]) # need this header or the decorator will send 406
    
       
       dict_response = json.loads(post_response.data) # convert json response to dictionary
       
       self.assertEqual(dict_response, {"song_id":"8" ,"song_name":"songname8","file_name":"filename8","file_id":"8"})


    def testGetSong(self):
        """ This test posts a record then gets it """
        ## post a record to the database
        
        post_response = self.client.post('/api/songs/post',
                                  data=json.dumps({"song_id":"8" ,"song_name":"songname8","file_name":"filename8","file_id":"8"}),
                                  content_type='application/json',
                                  follow_redirects=True,
                                  headers=[("Accept", "application/json")])
                                   
        
    #################### Now we can get the songs
       
        get_response = self.client.get("api/songs",
                                        content_type='application/json',
                                        follow_redirects=True,
                                        headers=[("Accept", "application/json")])
       
        # print "get response data is : {}".format(get_response.data)
        # print "**** get response data type is {}".format(type(get_response.data))
        
        ## we get back a string containing a nested dict formated like a list [ dict {dict}]
        # post api was modified to not send a nested json structure but because of model relationships
        # we get nested json back however in  the get request
        
       
        strip_response = get_response.data[1:-1]  # stripping the [] as api sends back a list of dictionary items
        
        dict_response = json.loads(strip_response) # convert json response to dictionary
        
        self.assertEqual(dict_response['song_id'], 8)
        self.assertEqual(dict_response['file']['file_name'], "filename8") # note the nested structures here

    def testDeleteSong(self):
        """ Post a record and then delete it """
        ## post a record to the database
        
        post_response = self.client.post('/api/songs/post',
                                  data=json.dumps({"song_id":"8" ,"song_name":"songname8","file_name":"filename8","file_id":"8"}),
                                  content_type='application/json',
                                  follow_redirects=True,
                                  headers=[("Accept", "application/json")])    
   
        ### delete the record we just posted
   
        delete_response = self.client.delete('/api/songs/delete',
                          data=json.dumps({"song_id":"8" ,"song_name":"songname8","file_name":"filename8","file_id":"8"}),
                          content_type='application/json',
                          follow_redirects=True,
                          headers=[("Accept", "application/json")]) 
                          
        self.assertEqual(delete_response.status_code,200)
       

    def tearDown(self):
        """ Test teardown """
        session.close()
        # Remove the tables and their data from the database
        Base.metadata.drop_all(engine)

        # Delete test upload folder
        shutil.rmtree(upload_path())


