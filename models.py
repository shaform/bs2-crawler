# coding=utf-8

import config
from peewee import *


class Teacher(Model):
    author = CharField(max_length=513)
    title = CharField(max_length=513)
    pub_time = CharField()
    article = TextField()

    class Meta:
        database = config.DATABASE


config.DATABASE.connect()


if __name__ == '__main__':
    import os
    import re
    import logging

    logger = logging.getLogger( __name__ )
    chinese_keyword = {
        'board': '看板',
    }
    
    file_dir = './NCTU-Teacher/'
    for filename in os.listdir(file_dir):
        with open(os.path.join(file_dir, filename)) as f:
            author_line = f.readline().split()
            if not chinese_keyword['board'] in author_line:
                continue
            _i = author_line.index(chinese_keyword['board'])
            author = ' '.join(author_line[1:_i])

            title_line = f.readline().split()[1:]
            title = ' '.join(title_line)

            time_line = f.readline().split()[1:]
            time = ' '.join(time_line)

            article = f.read()

            try:
                post = Teacher.get(id=filename)
                post.article = article
                post.save()
                logger.info('Update: ' + filename)
            except Teacher.DoesNotExist:
                post = Teacher.create(author=author,
                    title=title,
                    pub_time=time,
                    article=article,
                    id=int(filename)
                )
                logger.info('Insert: ' + filename)
