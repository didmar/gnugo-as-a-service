from flask import Flask
from flask.ext.cors import CORS
import optparse
import os
import re
import json

def gtp(command):
    global gtpnr, to_gnugo, from_gnugo, verbose
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
        board.insert(0, m.group(1).split(' '))
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
CORS(app)

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

    default_pathtognugo = '/usr/games/gnugo'
    default_host="127.0.0.1"
    default_port="5000"

    # Set up the command-line options
    parser = optparse.OptionParser()
    parser.add_option("-H", "--host",
                      help="Hostname of the Flask app " + \
                           "[default %s]" % default_host,
                      default=default_host)
    parser.add_option("-P", "--port",
                      help="Port for the Flask app " + \
                           "[default %s]" % default_port,
                      default=default_port)
    parser.add_option("-e", "--executable",
                      help="Path to the GnuGo executable " + \
                           "[default %s]" % default_pathtognugo,
                      default=default_pathtognugo)
    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose",
                      help=optparse.SUPPRESS_HELP)
    
    # Two options useful for debugging purposes, but 
    # a bit dangerous so not exposed in the help message.
    parser.add_option("-d", "--debug",
                      action="store_true", dest="debug",
                      help=optparse.SUPPRESS_HELP)
    parser.add_option("-p", "--profile",
                      action="store_true", dest="profile",
                      help=optparse.SUPPRESS_HELP)

    options, _ = parser.parse_args()

    # If the user selects the profiling option, then we need
    # to do a little extra setup
    if options.profile:
        from werkzeug.contrib.profiler import ProfilerMiddleware

        app.config['PROFILE'] = True
        app.wsgi_app = ProfilerMiddleware(app.wsgi_app,
                       restrictions=[30])
        options.debug = True

    
    gnugocmd = options.executable + ' --boardsize 19 --mode gtp'
    to_gnugo, from_gnugo = os.popen2(gnugocmd)
    verbose = options.verbose 
    gtpnr = 1

    app.run(
        debug=options.debug,
        host=options.host,
        port=int(options.port)
    )
