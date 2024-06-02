import socket

class RTSPClient:
    host = None
    port = None
    username = None
    password = None
    socket_rtsp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_rtp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    clientports = [60784, 60785]
    sessionId = None
    received_packets = 100
    packetCount = 0

    def __init__(self, host, port, username='', password=''):
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    def connect(self):
        self.socket_rtsp.settimeout(2)
        self.socket_rtsp.connect((self.host, self.port))

    def options(self):
        opt = "OPTIONS rtsp://" + self.host + ":" + str(self.port) + "/live RTSP/1.0\r\nCSeq: 2\r\nUser-Agent: python\r\n\r\n"
        self.socket_rtsp.send(opt.encode())
        print(opt)
        return self.socket_rtsp.recv(4096)
    
    def describe(self):
        desc = "DESCRIBE rtsp://" + self.host + ":" + str(self.port) + "/live RTSP/1.0\r\nCSeq: 3\r\nUser-Agent: python\r\nAccept: application/sdp\r\n\r\n"
        self.socket_rtsp.send(desc.encode())
        response = self.socket_rtsp.recv(4096)
        sps = response.decode().split("sprop-parameter-sets=")[1].split(",")[0]
        pps = response.decode().split("sprop-parameter-sets=")[1].split(",")[1]
        return response, sps, pps
    
    def setup(self):
        setu0 = "SETUP rtsp://" + self.host + ":" + str(self.port) + "/live/track0 RTSP/1.0\r\nCSeq: 4\r\nUser-Agent: python\r\nTransport: RTP/AVP;unicast;client_port="+str(self.clientports[0])+"-"+str(self.clientports[1])+"\r\n\r\n"
        self.socket_rtsp.send(setu0.encode())
        response = self.socket_rtsp.recv(4096)
        sessionId = response.decode().split("Session: ")[1].split("\r\n")[0]
        self.sessionId = sessionId
        return response, sessionId    

    def play(self):
        self.socket_rtp.bind(("", self.clientports[0]))
        self.socket_rtp.settimeout(5)
        play = "PLAY rtsp://" + self.host + ":" + str(self.port) + "/live RTSP/1.0\r\nCSeq: 11\r\nUser-Agent: python\r\nSession: " + self.sessionId + "\r\nRange: npt=0.000-\r\n\r\n"
        self.socket_rtsp.send(play.encode())
        return self.socket_rtsp.recv(4096)
    
    def teardown(self):
        teardown = "TEARDOWN rtsp://" + self.host + ":" + str(self.port) + "/live RTSP/1.0\r\nCSeq: 12\r\nUser-Agent: python\r\nSession: " + self.sessionId + "\r\n\r\n"
        self.socket_rtsp.send(teardown.encode())
        response = self.socket_rtsp.recv(4096)
        self.socket_rtsp.close()
        self.socket_rtp.close()
        return response
    
    
    def listen(self):
        if self.packetCount < self.received_packets:
            data = self.socket_rtp.recv(4096)
            self.packetCount += 1
            return data
        else:
            return None
        
    def setPakcetNum(self, num):
        self.received_packets = num