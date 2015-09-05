import os.path

from flask import url_for
from sqlalchemy import Column, Integer, String, Sequence, ForeignKey
from sqlalchemy.orm import relationship

from tuneful import app
from database import Base, engine

import re

class Song(Base):
    __tablename__ = "song"

    id = Column(Integer, primary_key=True)
    song_name = Column(String(64), nullable = True)
    file = relationship("File", uselist=False, backref = "file")
    
    def as_dictionary(self):
        song = {
            "song_id": self.id,
            "song_name":self.song_name,
            "file": self.file.as_dictionary(),
            }
        return song
        
    
    
        
class File(Base):
    __tablename__ = "file"

    id = Column(Integer, primary_key=True)
    file_name = Column(String(64), nullable=False)
    song_id = Column(Integer, ForeignKey('song.id'))

    def as_dictionary(self):
        
        
        ## tried to use this to fix the build error I'm getting for this path statement
        def stripUnicode(self, input_string):
            """ This function takes a string as input.  Generally from response.json and adjusts format to better fit json 
                requirements by stripping leading u and substituting " for '. """
            self.tmp_string = re.sub('u\'','\'',str(input_string))  # replace u' with blank'.
            self.final_string = re.sub('\'','\"',self.tmp_string) # replace single quote with double quote
            return self.final_string 
        
        file = {
            "file_id": self.id,
            "file_name": self.file_name,
            "song_id":self.song_id,
            #"path": url_for("uploaded_file", filename=stripUnicode(self, self.file_name)),  # think about commenting this out to test why crashing
            "path": url_for("uploaded_file", file_name=self.file_name)
            }
        return file       
    
     