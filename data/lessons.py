import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Lesson(SqlAlchemyBase):
    __tablename__ = 'lessons'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    user = orm.relationship('User')
    cost = sqlalchemy.Column(sqlalchemy.Integer)
    date = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    time = sqlalchemy.Column(sqlalchemy.Integer)
