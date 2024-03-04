# Websocket-related functions
import json
from sys import stdin, stdout, stderr, exit
def cons(*tt): [(stderr.write('^'+t + '\n'), stderr.flush()) for t in tt] 
def send(d): stdout.write(d+'\n'); stdout.flush();#cons(d[:80])
def stat(msg=None, clear = False): send(f'I{"" if clear else "A"};#stat;{msg}<br>' if msg else f'I;#stat;')
