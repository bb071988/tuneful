import os.path

from flask import url_for
from sqlalchemy import Column, Integer, String, Sequence, ForeignKey
from sqlalchemy.orm import relationship

from tuneful import app
from database import Base, engine

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
        file = {
            "file_id": self.id,
            "file_name": self.file_name,
            "song_id":self.song_id,
            
            }
        return file       
        