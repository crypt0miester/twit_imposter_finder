from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Binary, Float, Boolean, BigInteger
from sqlalchemy_utils import database_exists


engine = create_engine('sqlite:///twit_imposter_finder.db', echo=False) # , echo=True)

Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()


class Me(Base):
    __tablename__ = 'me'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    bio = Column(String)
    image_hash = Column(String)
    profile_name = Column(String)
    
    def __repr__(self):
        return f'me {self.username}'
    

class Imposter(Base):
    __tablename__ = 'imposters'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    profile_name = Column(String)
    username_confidence_level = Column(Float)
    profile_bio = Column(String)
    bio_confidence_level = Column(Float)
    image_hash = Column(String)
    # twitter_id = Column(BigInteger)
    reported = Column(Boolean, default=False)
    

    def __repr__(self):
        return f'imposter {self.username}'

if not database_exists(engine.url):
    Base.metadata.create_all(engine)