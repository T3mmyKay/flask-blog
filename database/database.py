from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


class Db(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Db)
