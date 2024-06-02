DEBUG = False

host = 'localhost'
port = 554

adr="rtsp://localhost:554/live" # username, passwd, etc.
clientports=[60784,60785] # the client ports we are going to use for receiving video
fname="stream.h264" # filename for dumping the stream
rn=15000 # receive this many packets

opt="OPTIONS "+adr+" RTSP/1.0\r\nCSeq: 2\r\nUser-Agent: python\r\n\r\n"
desc="DESCRIBE "+adr+" RTSP/1.0\r\nCSeq: 3\r\nUser-Agent: python\r\nAccept: application/sdp\r\n\r\n"
setu0 = "SETUP "+adr+"/track0 RTSP/1.0\r\nCSeq: 4\r\nUser-Agent: python\r\nTransport: RTP/AVP;unicast;client_port="+str(clientports[0])+"-"+str(clientports[1])+"\r\n\r\n"
setu1 = "SETUP "+adr+"/track1 RTSP/1.0\r\nCSeq: 5\r\nUser-Agent: python\r\nTransport: RTP/AVP;unicast;client_port="+str(clientports[0])+"-"+str(clientports[1])+"\r\n\r\n"
setu2 = "SETUP "+adr+"/track2 RTSP/1.0\r\nCSeq: 6\r\nUser-Agent: python\r\nTransport: RTP/AVP;unicast;client_port="+str(clientports[0])+"-"+str(clientports[1])+"\r\n\r\n"
setu3 = "SETUP "+adr+"/track3 RTSP/1.0\r\nCSeq: 7\r\nUser-Agent: python\r\nTransport: RTP/AVP;unicast;client_port="+str(clientports[0])+"-"+str(clientports[1])+"\r\n\r\n"
setu4 = "SETUP "+adr+"/track4 RTSP/1.0\r\nCSeq: 8\r\nUser-Agent: python\r\nTransport: RTP/AVP;unicast;client_port="+str(clientports[0])+"-"+str(clientports[1])+"\r\n\r\n"
setu5 = "SETUP "+adr+"/track5 RTSP/1.0\r\nCSeq: 9\r\nUser-Agent: python\r\nTransport: RTP/AVP;unicast;client_port="+str(clientports[0])+"-"+str(clientports[1])+"\r\n\r\n"
setu6 = "SETUP "+adr+"/track6 RTSP/1.0\r\nCSeq: 10\r\nUser-Agent: python\r\nTransport: RTP/AVP;unicast;client_port="+str(clientports[0])+"-"+str(clientports[1])+"\r\n\r\n"
play = "PLAY "+adr+" RTSP/1.0\r\nCSeq: 11\r\nUser-Agent: python\r\nSession: FLAG_1\r\nRange: npt=0.000-\r\n\r\n"

def debug_print(msg):
    if DEBUG:
        print(msg)