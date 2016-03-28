from flask import Flask
import os
import re
import json

verbose = True

gnugocmd = 'gnugo --boardsize 19 --mode gtp'
to_gnugo, from_gnugo = os.popen2(gnugocmd)
gtpnr = 1

def gtp(command):
    global gtpnr
    cmd = str(gtpnr)+' '+command
    if verbose:
        print 'cmd: '+cmd
    to_gnugo.write(cmd+"\n")
    to_gnugo.flush()
    line = from_gnugo.readline()
    x = line.split(' ')
    isok = x[0][0] == '='
    gtpnr_confirm = int(x[0][1:])
    assert(gtpnr == gtpnr_confirm)
    msg = ' '.join(x[1:])
    while len(line) > 1:
        line = from_gnugo.readline()
        msg += line
    if verbose:
        print 'msg: '+msg
    gtpnr = gtpnr + 1
    return isok, msg

def parseBoard(msg):
    lines = msg.split('\n')
    letters = lines[1].lstrip().rstrip().split(" ")
    boardSize = len(letters)
    board = []
    blackCaptures = None
    whiteCaptures = None
    for line in lines[2:(2+boardSize)]:
        m = re.search('^\s*\d+\s([^\d]+)\s\d+\s*.*$', line)
        board.append(m.group(1).split(' '))
        m = re.search('.*(WHITE \(O\)|BLACK \(X\)) has captured (\d+) stones', line)
        if m != None:
            if m.group(1).startswith('WHITE'):
                whiteCaptures = int(m.group(2))
            else:
                blackCaptures = int(m.group(2))
    return {'board': board, \
            'blackCaptures': blackCaptures, \
            'whiteCaptures': whiteCaptures, \
            'boardSize': boardSize}

app = Flask(__name__)

@app.route('/showboard')
def showboard():
    isok, msg = gtp('showboard')
    if isok:
        return json.dumps(parseBoard(msg)), 200, {'Content-Type': 'application/json; charset=utf-8'}
    else:
        return msg, 400

@app.route('/<path:command>')
def gtpCommand(command):
    isok, msg = gtp(' '.join(command.split('/')))
    return msg, 200 if isok else 400

if __name__ == '__main__':
    app.run()
