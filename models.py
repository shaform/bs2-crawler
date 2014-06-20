# coding=utf-8

import config
from peewee import *


class Teacher(Model):
    bbs_id = IntegerField(null=True)
    author = CharField(max_length=513)
    title = CharField(max_length=513)
    pub_time = DateTimeField()
    content = TextField()

    class Meta:
        database = config.DATABASE


config.DATABASE.connect()
