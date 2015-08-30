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


######### This function strips the unicode u's from the dictionary version of the returning bytes not unicode characters
def byteify(input):
    if isinstance(input, dict):
        return {byteify(key):byteify(value) for key,value in input.iteritems()}
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input


class TestAPI(unittest.TestCase):
    """ Tests for the tuneful API """

    def setUp(self):
        """ Test setup """
        self.client = app.test_client()

        # Set up the tables in the database
        Base.metadata.create_all(engine)

        # Create folder for test uploads
        os.mkdir(upload_path())
        
        
    def testGetSongs(self):
        """ Getting posts from a populated database """
        
        songA = models.Song(id=200,song_name='mysongname')
        
        fileA = models.File(id= 200, file_name = 'nosetestfile1',song_id= 200)

        session.add_all([songA,fileA])
        
        session.commit()
        
        # print "******************************** testGetSongs *****************************"
        
        # print "This is the song ID: {}".format(json.dumps(songA.id))
        # print "This is the song name: {}".format(json.dumps(songA.song_name))
        # print "This is the song file name {}".format(json.dumps(fileA.file_name))
        # print "This is the song file name {}".format(json.dumps(songA.file_name.as_dictionary()))
       
        song_list = session.query(models.Song).all()
        
        song_json = json.dumps([x.as_dictionary() for x in song_list])
        
        song_dict = json.loads(song_json)
        
        new_dict = byteify(song_dict)
        
        # print "Song List: {}".format(song_list)
        # print "***********************************************************************"
        # print "Song List JSON format {}".format(song_json)
        # print "***********************************************************************"
        # print "Song List Dictionary format {}".format(song_dict)
        # print "***********************************************************************"
        # for x in song_dict:
        #     print x["file_name"]["file_name"]
        # print "***********************************************************************"
        # print "Try getting the song name from the dict {}".format(song_dict[0][u'file_name'][u'file_name'])
        # print "************************************************************************"
        # print "Try getting info from bytify version of dict {}".format(new_dict[0]['file_name']['file_name'])
        
        
        response = self.client.get("/api/songs",
            headers=[("Accept", "application/json")]
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
    
        self.assertEqual(new_dict[0]['file_name']['file_name'], "nosetestfile1")
        
        
    def testAddSong(self):
        
        # data1 is a dictionary in python
        data1 = {"song_name":"testsong100",
        "id":100,
        "file_name":"testfilename100"}
        
        ### does my json post need to be a string or a list?
        
        print "********************************* add song response follows ***************************************"
        
        print "data1 is: {} ".format(data1)
        print "song name from data1 is {}: ".format(data1['song_name'])
        
        data2=json.loads("{'song_name':'testsong100','id':100,'file_name':'testfilename100'}") # converts data1 dict to json
        
        print "data2 is json as follows: {}".format(data2)
        
        # print "data2 is a dictionary: {} ".format(data2['song_name'])
        
        response = self.client.post("/api/songs/post",data=data2)
        
        # headers=[("Accept", "application/json")]
       
        print "This is the response object: {}".format(response)
        

        # self.assertEqual(response.status_code, 302)
        # self.assertEqual(urlparse(response.location).path, "/")
        get_song = session.query(models.Song).get(1)
        # for song in all_songs:
        #     print all_songs[song] 
        self.assertEqual(0,0)

        data = json.loads(response.data)
        print "This is the response data {}".format(data)
        # post = posts[0]
        # self.assertEqual(post.title, "Test Post")
        # self.assertEqual(post.content, "<p>Test content</p>\n")
        # self.assertEqual(post.author, self.user)
       

    def tearDown(self):
        """ Test teardown """
        session.close()
        # Remove the tables and their data from the database
        Base.metadata.drop_all(engine)

        # Delete test upload folder
        shutil.rmtree(upload_path())


