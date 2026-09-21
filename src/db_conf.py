from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, JSON
from sqlalchemy.orm import declarative_base, sessionmaker
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit = False, autoflush=False, bind=engine)
Base = declarative_base()

class PokemonDB(Base):
    __tablename__ = 'pokemons'

    _id = Column(Integer, primary_key=True)
    nome = Column(String, index=True)
    altura = Column(Integer)
    peso = Column(Integer)
    tipos = Column(JSON)

Base.metadata.create_all(bind=engine)

def session_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()