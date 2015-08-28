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

#from .models import Song  #ask Sam why I can't comment this if I'm importing all of models above.

@app.route("/api/songs", methods=["GET"])
@decorators.accept("application/json")
def songs_get():
    """ Get  all the songs """
    # Get the songs from the database
    all_songs = session.query(models.Song).all()

    # Return the post as JSON
    
    ## make sure to use the as_dictionary() method with the brackets here to get serializable dictionary
    ## song in line below is arbitrary could be x y or z
    if len(all_songs):
        print len(all_songs)
        data = json.dumps([song.as_dictionary() for song in all_songs])
        return Response(data, 200, mimetype="application/json")
    else:
        data = "No songs to show you yet"
        return Response(data,404, mimetype="application/json")
    

@app.route("/api/songs/post", methods=["POST"])
@decorators.accept("application/json")
def song_post():
    """ post a song """
    headers = {"Location": url_for("song_post")}
    # get the data from the form
    
    data = request.json
    
    post_song = models.Song(song_name=data["song_name"],id=data["id"])  ## ask sam if we really need to post seperately.
    post_file = models.File(id=data["id"],file_name=data["file_name"])
  
 
    if not session.query(models.Song).get(post_song.id):  #consider adding a check here for duplicate fileID too
        f = open('workfile', 'w+')
        f.write("list of all the ids {}".format(session.query(models.Song.id).all()))
        f.close()
        session.add_all([post_song,post_file])
        session.commit()
    else:
        print "************* ELSE ***************"
        session.rollback()
        f = open('workfile', 'w+')
        f.write("list of all the ids {}".format(session.query(models.Song.id).all()))
        f.close()
        session.flush()
        return Response(json.dumps({"status":"failed - that song already exists"}),500,mimetype="application/json")
    
    return Response(json.dumps({"status":"posted"}), 200, headers=headers, mimetype="application/json")
    
    

@app.route("/api/songs/delete", methods=["delete"])
@decorators.accept("application/json")
def song_delete():
    """ post a song """
    headers = {"Location": url_for("song_delete")}
    # get the data from the form
    
    data = request.json
    
    post_song = models.Song(song_name=data["song_name"],id=data["id"])  ## ask sam if we really need to post seperately.
    #delete_file = models.File(id=data["id"],file_name=data["file_name"])
  
    if session.query(models.Song).get(post_song.id):  #consider adding a check here for duplicate fileID too
        del_song=session.query(models.Song).get(post_song.id)
        session.delete(del_song)
        session.commit()
    else:
        print "************* ELSE ***************"
        session.rollback()
        f = open('workfile', 'w+')
        f.write("list of all the ids {}".format(session.query(models.Song.id).all()))
        f.close()
        session.flush()
        return Response(json.dumps({"status":"failed - that song doesnt exists"}),500,mimetype="application/json")
    
    return Response(json.dumps({"status":"deleted"}), 200, headers=headers, mimetype="application/json")
