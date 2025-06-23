from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from app.models import Base

# Base de datos en memoria
engine = create_engine('sqlite:///:memory:', echo=True)

# Crear tablas
Base.metadata.create_all(engine)

# Crear sesión
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)
