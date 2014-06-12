# coding=utf-8
import logging
import pyte
import re
import time
import os

import config

from telnetlib import Telnet
from bsdconv import Bsdconv

from models import Teacher


logger = logging.getLogger( __name__ )


class Crawler(object):
    convert = Bsdconv("ansi-control,byte:big5-defrag:byte,ansi-control|skip,big5:utf-8,bsdconv_raw")

    def __init__(self, host):
        self.host = host
        self.delay = 0
        self.conn = Telnet(host, 3456)
        self.screen = pyte.Screen(80, 24)
        self.stream = pyte.Stream()
        self.screen.mode.discard(pyte.modes.LNM)
        self.stream.attach(self.screen)
        self.display
        self.login()
        self.enter_board('NCTU-Teacher')
        for i in range(input('n - ' + self.last_id + ': '), int(self.last_id) + 1):
            self.get_article(i)

    @property
    def display(self):
        s = self.conn.read_very_eager()
        while not s:
            s = self.conn.read_very_eager()
            time.sleep(self.delay)           
        s = self.convert.conv(s)
        self.stream.feed(s.decode('utf-8'))
        return self.screen_shot

    @property
    def screen_shot(self):
        return "\n".join(self.screen.display).encode("utf-8")

    def close(self):
        self.conn.close()

    def send_enter(self, count=1):
        for i in range(count):
            s = self.send('\r')
            if count == 1:
                return s
    
    def send(self, s):
        self.conn.write(s)
        ret = self.display
        return ret

    def login(self):
        username = 'guest'
        self.conn.write(username + '\r')
        self.conn.write('\rYY\r')
        self.send_enter(2)

    def enter_board(self, board):
        '''
        Save current board name in self.board
        and lastest article_id in self.last_id
        '''
        self.send('OBOC')
        self.send('s{}'.format(board))
        self.send_enter(2)
        line = self.screen.cursor.y
        self.last_id = re.search(r'(?P<last_id>^\d+) ', self.screen.display[line].strip()).group()
        self.board = board

    def get_article(self, num=None):
        if not num:
            return

        self.send('{}\rOC'.format(num))
        raw_artcle = self.screen.display[:-1]

        status_line = self.screen.display[-1]
        if status_line.find('[Y/n]') != -1:
            self.send('n')
        while status_line.find('(100%)') == -1:
            self.send('OB')
            status_line = self.screen.display[-1]
            raw_artcle.append(self.screen.display[-2])
        self.save_article(num, raw_artcle)

    def term_comm(feed=None, wait=None):
        if feed != None:
            self.conn.write(feed)
            if wait:
                s = self.conn.read_some()
                s = self.convert.conv_chunk(s)
                self.stream.feed(s.decode("utf-8"))
        if wait != False:
            time.sleep(0.1)
            s = self.conn.read_very_eager()
            s = self.convert.conv_chunk(s)
            self.stream.feed(s.decode("utf-8"))
        ret = "\n".join(self.screen.display).encode("utf-8")
        return ret

    def save_article(self, num, content):
        '''
        :param content: a list get from screen
        '''
        chinese_keyword = {
            'board': '看板',
        }

        author_line = content[0].encode('utf-8').split()
        if not chinese_keyword['board'] in author_line:
            return
        _i = author_line.index(chinese_keyword['board'])
        author = ' '.join(author_line[1:_i])

        title_line = content[1].encode('utf-8').split()[1:]
        title = ' '.join(title_line)

        time_line = content[2].encode('utf-8').split()[1:]
        time = ' '.join(time_line)

        article = '\n'.join(content[3:]).encode('utf-8')

        try:
            post = Teacher.get(id=num)
            post.article = article
            post.save()
            logger.info('Update: {id}'.format(id=num))
        except Teacher.DoesNotExist:
            post = Teacher.create(author=author,
                title=title,
                pub_time=time,
                article=article,
                id=num
            )
            logger.info('Insert: {id}'.format(id=num))


if __name__ == '__main__':
    bs2 = Crawler('bs2.to')
