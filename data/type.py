import sqlalchemy
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import orm
from data.db_session import SqlAlchemyBase


class Type(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'type'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    type = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    item = orm.relation('Item')
