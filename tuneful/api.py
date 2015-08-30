import os.path
import json

from flask import request, Response, url_for, send_from_directory
from werkzeug.utils import secure_filename
from jsonschema import validate, ValidationError

import models  # when we import like this we have to use models.METHOD to refer to the methods # if import * from models - risk overwrite of
# methods second import writes over first.
import decorators
from tuneful import app
from database import session
from utils import upload_path
import re  # addeed for stripUnicode function

#from .models import Song  #ask Sam why I can't comment this if I'm importing all of models above.

@app.route("/api/songs", methods=["GET"])
@decorators.accept("application/json")
def songs_get():
    """ Get  all the songs """
    # Get the songs from the database
    all_songs = session.query(models.Song).all()

    # set the headers
    headers = {"Location": url_for("songs_get"),"Content-Type": "application/json"}
    
    # Return the post as JSON
    
    ## make sure to use the as_dictionary() method with the brackets here to get serializable dictionary
    ## song in line below is arbitrary could be x y or z
    if len(all_songs):
        print len(all_songs)
        data = json.dumps([song.as_dictionary() for song in all_songs])  ################  Key concept
        return Response(data, 200, headers = headers, mimetype="application/json")
    else:
        data = "No songs to show you yet"
        return Response(data,404, headers = headers, mimetype="application/json")
    

@app.route("/api/songs/post", methods=["POST"])
#@decorators.accept("application/json")
def song_post():
    """ post a song """
    headers = {"Location": url_for("song_post"),"Content-Type": "application/json"}
    # print "this is the header {}".format(headers)
    # get the data from the form
    data = request.json  
    
    post_song = models.Song(song_name=data["song_name"],id=data["song_id"])  ## ask sam if we really need to post seperately.
    post_file = models.File(song_id=data["file"]["song_id"],file_name=data["file"]["file_name"],id=data["file"]["file_id"])


    if not session.query(models.Song).get(post_song.id):  #consider adding a check here for duplicate fileID too
        session.add_all([post_song,post_file])
        session.commit()
    else:
        print "************* ELSE ***************"
        session.rollback()
        session.flush()
        return Response(json.dumps({"status":"failed - that song already exists"}),500,mimetype="application/json")
        
    return Response(stripUnicode(data), 200, headers=headers, mimetype="application/json")
    

@app.route("/api/songs/delete", methods=["delete"])
@decorators.accept("application/json")
def song_delete():
    """ delete a song """
    headers = {"Location": url_for("song_delete")}
    # get the data from the form
    
    data = request.json
    
    post_song = models.Song(song_name=data["song_name"],id=data["song_id"])  ## ask sam if we really need to post seperately.
    post_file = models.File(song_id=data["file"]["song_id"],file_name=data["file"]["file_name"],id=data["file"]["file_id"])
  
    if session.query(models.Song).get(post_song.id):  #consider adding a check here for duplicate fileID too
        del_song=session.query(models.Song).get(post_song.id)
        session.delete(del_song)
        
        del_file = session.query(models.File).get(post_file.id)
        session.delete(del_file)
        
        session.commit()
    else:
        print "************* ELSE ***************"
        session.rollback()
        session.flush()
        return Response(json.dumps({"status":"failed - that song doesnt exists"}),500,mimetype="application/json")
    
    return Response(json.dumps({"status":"deleted"}), 200, headers=headers, mimetype="application/json")
    
def stripUnicode(input_string):
    """ This function takes a string as input.  Generally from response.json and adjusts format to better fit json 
        requirements by stripping leading u and substituting " for '. """
    tmp_string = re.sub('u\'','\'',str(input_string))  # replace u' with blank'.
    final_string = re.sub('\'','\"',tmp_string) # replace single quote with double quote
    return final_string


####################################################################################################################################
""" Notes
I think that the post endpoint could be reconfigured to take json in different format.  This is essentially processing
the request for the song and ignoring the file.

Talk to Sam about json client is sending api.  Right now it is sending the key fields.  Seems like those should increment automatically
otherwise client needs to keep track of them which makes no sense.

Talk to Sam about the stripUnicode function.  Much simpler than bytify which was used in the api_test.py.  Maybe ask about escaping
vs raw function

Also review python path and unittest with Sam since this nosetest bug is a pain.

Revisit headers - I think that the api/post seems good.  Returns json.

test json
{"song_id": 8, "song_name": "songname8", "file": {"file_name": "filename8", "song_id": 8, "file_id": 8}}


"""