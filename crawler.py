# coding=utf-8
import argparse
import errno
import pyte
import re
import time
import os

from telnetlib import Telnet


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


class Conv(object):
    def conv(self, s):
        return s.decode('big5', 'ignore').encode('utf8')

    def conv_chunk(self, s):
        return s.decode('big5', 'ignore').encode('utf8')


class Crawler(object):
    convert = Conv()

    def __init__(self, host, board_name):
        self.host = host
        self.delay = 0
        self.conn = Telnet(host, 3456)
        self.screen = pyte.Screen(80, 24)
        self.stream = pyte.Stream()
        self.screen.mode.discard(pyte.modes.LNM)
        self.stream.attach(self.screen)
        self.display
        self.login()
        self.display
        print self.screen_shot
        self.board_name = board_name
        self.enter_board(board_name)
        print self.screen_shot
        for i in range(
                input('n - ' + self.last_id + ': '), int(self.last_id) + 1):
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
        self.send_enter(4)

    def enter_board(self, board):
        '''
        Save current board name in self.board
        and lastest article_id in self.last_id
        '''
        self.send('s{}\r'.format(board))
        print self.screen_shot
        time.sleep(1)
        while '(Tab/z)' not in self.screen_shot:
            self.send('\r')
            time.sleep(1)
        print self.screen_shot
        line = self.screen.cursor.y
        self.last_id = re.search(r'(?P<last_id>^\d+) ',
                                 self.screen.display[line].strip()).group()
        self.board = board

    def get_article(self, num=None):
        print 'try get %d' % num
        if not num:
            return

        self.send('{}\r\r'.format(num))
        if '(Tab/z)' in self.screen_shot:
            return
        raw_artcle = self.screen.display[:-1]

        status_line = self.screen.display[-1]
        if 'p%' not in status_line:
            return
        if status_line.find('[Y/n]') != -1:
            self.send('n')
        while status_line.find('(100%)') == -1:
            self.send('OB')
            status_line = self.screen.display[-1]
            raw_artcle.append(self.screen.display[-2])
        self.save_article(num, raw_artcle)
        print self.screen_shot

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
        article = '\n'.join(content).encode('utf-8')

        root_dir = os.path.join('articles', self.board_name)
        mkdir_p(root_dir)
        path = os.path.join(root_dir, str(num))
        with open(path, 'w') as f:
            f.write(article)
        print '%d saved' % num


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Bs2 Crawler')
    parser.add_argument('--board-name', required=True)
    args = parser.parse_args()

    bs2 = Crawler('bs2.to', args.board_name)
