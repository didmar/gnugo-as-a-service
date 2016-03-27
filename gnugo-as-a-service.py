from flask import Flask
import os

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
    msg = x[1]
    while len(line) > 1:
        line = from_gnugo.readline()
        msg += line
    if verbose:
        print 'msg: '+msg
    gtpnr = gtpnr + 1
    return isok, msg

app = Flask(__name__)

@app.route('/<path:command>')
def hello_world(command):
    isok, msg = gtp(' '.join(command.split('/')))
    return msg, 200 if isok else 400

if __name__ == '__main__':
    app.run()
