from subprocess import Popen, PIPE, STDOUT
import multiprocessing
import os,sys
import argparse
import numpy as np
import matplotlib.pyplot as plt
import asyncio

#taken from https://stackoverflow.com/questions/55003789/python-call-callback-after-async-function-is-done
def run_async(callback):
    def inner(func):
        def wrapper(*args, **kwargs):
            def __exec():
                out = func(*args, **kwargs)
                callback(out)
                return out
            return asyncio.get_event_loop().run_in_executor(None, __exec)
        return wrapper
    return inner

# forced flush after print
def displ(l): 
    print(l, flush=True)

# global variable for current engine index
currentId = 0

class Engine():

    def __init__(self, filename, debug=False):
        self.engine = Popen([filename], stdin=PIPE, stdout=PIPE, stderr=STDOUT, encoding="utf8", shell=True)
        self.debug = debug
        self.uci_isready()
        self.searching = False;

    def writeline(self, line):
        self.engine.stdin.write(line)
        self.engine.stdin.flush()
        if self.debug:
            displ('info string --> [{}] {}'.format(self.engine.pid, line.rstrip()))

    def readline(self):
        line = self.engine.stdout.readline()
        if self.debug:
            displ('info string <-- [{}] {}'.format(self.engine.pid, line.rstrip()))
        return line.rstrip()

    def uci_uci(self):
        self.writeline('uci\n')
        # wait for uciok
        while True:
            l = self.readline()
            if 'uciok' in l:
                # uci ok will be sent by the proxy
                return
            else:
                displ(l)

    def uci_isready(self):
        self.writeline('isready\n')
        # wait for isready
        while True:
            l = self.readline()
            if 'readyok' in l:
                # readyok ok will be sent by the proxy
                return
            else:
                displ(l)

    def uci_set_option(self, line):
        self.uci_isready()
        self.writeline(line)
        self.uci_isready()

    def uci_ucinewgame(self):
        self.uci_isready()
        self.writeline('ucinewgame\n')
        self.uci_isready()

    def uci_quit(self):
        self.uci_isready()
        self.writeline('quit\n')

    def search_callback(self, *args):
        # access the global
        global currentId        
        currentId += 1

        self.searching = False
        
    @run_async(search_callback)
    def uci_search(self, line):
        self.searching = True
        self.writeline(line)
        # wait for bestmove, printing everything else before that
        while True:
            l = self.readline()
            displ(l)
            if l.startswith('bestmove'):
                return


parser = argparse.ArgumentParser(description='Multiple engine proxy')
parser.add_argument('-e', '--engines', type=str, nargs='+', help='a list of engines to check')
args = parser.parse_args()

engines = args.engines
if not engines or engines and len(engines) == 0:
    parser.error('At least one engine needs to be specified')

print('info string {}'.format(engines))

def uci():
    # access the global
    global currentId

    # create each engine processe
    procs = {}
    for engine in engines:
        procs[engine] = Engine(engine,False)

    while True:
        # change engine every 5 played moves
        currentName = list(procs)[currentId//5]
        current = procs[currentName]        
        displ('info string current engine is {}'.format(currentName))
        t = input()

        if t == 'quit':
            # quit all engines
            for engine in engines:
                procs[engine].uci_quit()            
            break

        elif t == 'uci': 
            displ('id name Pr0xy\nid author xr_a_y\n')
            # init all engine
            for engine in engines:
                procs[engine].uci_uci()
            displ('uciok')

        elif t == 'isready': 
            # broadcast to each engine
            for engine in engines:
                procs[engine].uci_isready()
            displ('readyok')

        elif t == 'ucinewgame': 
            # broadcast to each engine
            for engine in engines:
                procs[engine].uci_ucinewgame()

        elif t.startswith('setoption'):
            # broadcast to each engine
            for engine in engines:
                procs[engine].uci_set_option(t + '\n')

        elif t.startswith('go'):
            # this is an async call !
            current.uci_search(t + '\n')

        else:
            # only send to current engine
            current.writeline(t + '\n')


if __name__ == '__main__':
    uci()