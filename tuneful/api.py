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
        data = json.dumps([song.as_dictionary() for song in all_songs])  ################  Key concept
        return Response(data, 200, headers = headers, mimetype="application/json")
    else:
        data = json.dumps({"status":"No songs to show you yet"})
        return Response(data,404, headers = headers, mimetype="application/json")
    

#@app.route("/api/songs/post", methods=["POST"])
@app.route("/api/songs/", methods=["POST"])
@decorators.accept("application/json")
def song_post():
    """ post a song """
    headers = {"Location": url_for("song_post"),"Content-Type": "application/json"}
   
    ######### get the data from the form
    data = request.json

    post_song = models.Song(song_name=data["song_name"])  ## ask sam if we really need to post seperately.
    
    session.add(post_song)
    session.commit()
    
    post_file = models.File(filename=data["filename"],song_id=data["song_id"])
    
    session.add(post_file)
    session.commit()
    
    # new_id = session.query(models.Song).order_by('id').first()
    
    # print "*************** new_id here ***********  {}".format(new_id.id)
    
    # ObjectRes.query.order_by('-id').first()


    # if not session.query(models.Song).get(new_id):  #consider adding a check here for duplicate fileID too
    #     session.add_all([post_song,post_file])
    #     session.commit()
    # else:
    #     print "************* ELSE ***************"
    #     session.rollback()
    #     session.flush()
    #     return Response(json.dumps({"status":"failed - that song already exists"}),500, mimetype="application/json")
        
    return Response(stripUnicode(data), 200, headers=headers, mimetype="application/json")
    

@app.route("/api/songs/delete", methods=["delete"])
@decorators.accept("application/json")
def song_delete():
    """ delete a song """
    headers = {"Location": url_for("song_delete")}
    # get the data from the form
    
    data = request.json
    
    post_song = models.Song(song_name=data["song_name"],id=data["song_id"])  ## ask sam if we really need to post seperately.
    post_file = models.File(id=data["song_id"],filename=data["filename"])
    
    del_song=session.query(models.Song).get(post_song.id)
    session.delete(del_song)
        
    del_file = session.query(models.File).get(post_file.id)
    session.delete(del_file)
    session.commit()
    
    return Response(json.dumps({"status":"deleted"}), 200, headers=headers, mimetype="application/json")
    
def stripUnicode(input_string):
    """ This function takes a string as input.  Generally from response.json and adjusts format to better fit json 
        requirements by stripping leading u and substituting " for '. """
    tmp_string = re.sub('u\'','\'',str(input_string))  # replace u' with blank'.
    final_string = re.sub('\'','\"',tmp_string) # replace single quote with double quote
    return final_string
    
##################### file upload section #######################################
@app.route("/uploads/<filename>", methods=["GET"])
def uploaded_file(filename):
    return send_from_directory(upload_path(), filename)
    
@app.route("/api/files", methods=["POST"])
@decorators.require("multipart/form-data")
#@decorators.accept("application/json")
def file_post():
    file = request.files.get("file")
    if not file:
        data = {"message": "Could not find file data"}
        return Response(json.dumps(data), 422, mimetype="application/json")

    filename = secure_filename(file.filename)
    db_file = models.File(filename=filename)
    session.add(db_file)
    session.commit()
    file.save(upload_path(filename))

    data = db_file.as_dictionary()
    return Response(json.dumps(data), 201, mimetype="application/json")


####################################################################################################################################
""" Notes

Talk to Sam about json client is sending api.  Right now it is sending the key fields.  Seems like those should increment automatically
otherwise client needs to keep track of them which makes no sense.

Talk to Sam about the stripUnicode function.  Much simpler than bytify which was used in the api_test.py.  Maybe ask about escaping
vs raw function

Also review python path and unittest with Sam since this nosetest bug is a pain.

Revisit headers - I think that the api/post seems good.  Returns json. also  added accept application/json to test request

test json - old test json modified now.  
{"song_id": 8, "song_name": "song99", "song_id": 8, "file_id": 8}}

json.dumps encodes python to json
json.loads encodes json to python

changed api and tests to account for nested dict e.g., dict of dict problems with flask testing

grep -r "filename" - recursively looks for files with the text filename in them.


"""