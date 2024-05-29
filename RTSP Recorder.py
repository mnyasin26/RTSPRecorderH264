import socket
import rtsp
import bitstring
import base64
from datetime import datetime

DEBUG = True


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


def generate_sps_pps(width, height):
    # Parameter set values (example values, you may need to adjust them)
    profile_idc = 100  # Baseline profile
    level_idc = 40     # Level 4.0
    seq_parameter_set_id = 0

    # SPS (Sequence Parameter Set) data
    sps = bytearray([
        0x67,             # NAL unit type 7, SPS
        0x64, 0x00, 0x1E, # profile_idc = 100, constraint_set flags, level_idc = 40
        0xAC,             # seq_parameter_set_id = 0, log2_max_frame_num_minus4 = 0x2C (44)
        0x05, 0x40, 0x1E, # pic_order_cnt_type = 0, max_num_ref_frames = 5, gaps_in_frame_num_value_allowed_flag = 0
        0xFF, 0xFF, 0x03, 0xC0, # frame_crop_left_offset = 0, frame_crop_right_offset = 0, frame_crop_top_offset = 0, frame_crop_bottom_offset = 0
        0x00, 0x04,       # vui_parameters_present_flag = 1, bitstream_restriction_flag = 0
        0x00, 0x00, 0x00, 0x00, # num_units_in_tick = 0
        0x00, 0x00, 0x00, 0x00, # time_scale = 0
        0x00, 0x00, 0x00, 0x00, # fixed_frame_rate_flag = 0
        ])

    # PPS (Picture Parameter Set) data
    pps = bytearray([
        0x68,             # NAL unit type 8, PPS
        0x01,             # pic_parameter_set_id = 0
        ])

    return sps, pps


def debug_print(msg):
    if DEBUG:
        print(msg)


def decode_rtp_packet(packet):
    # Extract the relevant information from the RTP packet
    bt = bitstring.BitArray(bytes=packet)
    typ = bt[1:8].uint  # Type field of the RTP packet
    payload = packet[12:]  # RTP payload

    # Decode the RTP payload based on the type
    if typ == 32 or typ == 33 or typ == 34:
        # SPS, PPS, or VPS packet
        return payload
    elif typ == 49:
        # FU-A packet
        startF = bt[8]  # Start bit
        endF = bt[9]  # End bit
        if startF:
            # First fragment in a movie frame
            return payload[2:]  # Skip the first two bytes
        elif endF:
            # Last fragment in a movie frame
            return b''  # Empty payload
        else:
            return payload[2:]  # Skip the first two bytes
    else:
        return payload

# def digestpacket(st):
#     substr = ''
#     #print("start",hex(st[0]),hex(st[1]))
#     while st[0] != 0x24 or st[1] != 0x00:
#         #print(chr(st[0]),end='')
#         st = st[1:]
#         if len(st)==0:
#             print("package Err")    
#             return b'',st,1
#     msg_len =  int.from_bytes(st[2:4], "big")
#     #print("msg_len",msg_len)
    
#     if msg_len <= len(st)-4:
#         substr = st[msg_len+4:]
#         st = st[4:msg_len+4]
#         #print('msg len,left len=',len(st),len(substr))
#     else:
#         #print("continue read...")
#         return b'',st,1
#     #print( ' ------------------------------------')
#     #startbytes=[b'\x00',b'\x00',b'\x00',b'\x01'] # this is the sequence of four bytes that identifies a NAL packet.. must be in front of every NAL packet.
#     startbytes = bytes([0x00,0x00,0x00,0x01])
#     #print((st[0:8]).hex())
#     bt=bitstring.BitArray(bytes=st) # turn the whole string-of-bytes packet into a string of bits.  Very unefficient, but hey, this is only for demoing.
#     version=bt[0:2].uint # version
#     p=bt[3] # P
#     x=bt[4] # X
#     cc=bt[4:8].uint # CC
#     m=bt[9] # M
#     pt=bt[9:16].uint # PT
#     sn=bt[16:32].uint # sequence number
#     timestamp=bt[32:64].uint # timestamp
#     dt_obj = datetime.fromtimestamp(timestamp)
#     #c=bt[64:96].uint # ***c identifier
#     # The header format can be found from:
#     # https://en.wikipedia.org/wiki/Real-time_Transport_Protocol

#     lc=12 # so, we have red twelve bytes
#     bc=12*8 # .. and that many bits
    
#     cids=[]
#     for i in range(cc):
#         cids.append(bt[bc:bc+32].uint)
#         bc+=32; lc+=4;
#     #print("csrc identifiers:",cids)

#     if (x):
#         # this section haven't been tested.. might fail
#         hid=bt[bc:bc+16].uint
#         bc+=16; lc+=2;

#         hlen=bt[bc:bc+16].uint
#         bc+=16; lc+=2;

#         #print "ext. header id, header len",hid,hlen
#         hst=bt[bc:bc+32*hlen]
#         bc+=32*hlen; lc+=4*hlen;
    
#     #fb=bt[bc] # i.e. "F"
#     #nri=bt[bc+1:bc+3].uint # "NRI"
#     nlu0=bt[bc:bc+3] # "3 NAL UNIT BITS" (i.e. [F | NRI])
#     #typ=bt[bc+3:bc+8].uint # "Type"
#     typ=bt[bc+1:bc+7].uint # "Type", New Type
#     #print "F, NRI, Type :", fb, nri, typ
#     #print "first three bits together :",bt[bc:bc+3]
#     print("sequence number =",sn,'   Frame  Type   ',typ)
#     #if (typ==7 or typ==8):
#     if (typ==32 or typ==33 or typ==34): # 33 means SPS_NUT, 34 menas PPS_NUT
#         # this means we have either an SPS or a PPS packet
#         # they have the meta-info about resolution, etc.
#         # more reading for example here:
#         # http://www.cardinalpeak.com/blog/the-h-264-sequence-parameter-set/
#         if (typ == 32):
#             print (">>>>> VPS_NUT packet", "first byte",hex(st[lc]))
#         elif (typ==33):
#             print (">>>>> SPS_NUT packet", "first byte",hex(st[lc]))
#         else:
#             print (">>>>> PPS_NUT packet", "first byte",hex(st[lc]))
#         ret_str = startbytes+st[lc:]
#         print("segment length:",len(ret_str))
#         return ret_str,substr,0
#     # .. notice here that we include the NAL starting sequence "startbytes" and the "First byte"
#     #print("RTP payload len:",len(st[lc:]))
    
#     bc+=16; lc+=2; # H265 the first two byte is the FU identifier by wireshark-analyzing
#     # The "Type" here is most likely 28, i.e. "FU-A" FU-A is 49
    
#     if typ == 49:
#         startF = bt[bc] # start bit
#         endF = bt[bc+1] # end bit
#         #print("start,end=",start,end)
#         if (startF): # OK, this is a first fragment in a movie frame
#             print(">>>>> first fragment found")
#             # nlu=nlu0+nlu1 # Create "[3 NAL UNIT BITS | 5 NAL UNIT BITS]" this is used in H264
#             head=startbytes+bytes([0x26,0x01])
#             lc+=1 # We skip the "Second byte"
#         elif (endF):
#             print(">>>>> end fragment found")
#             head=b''
#             lc+=1 # We skip the "Second byte"
#         else:
#             head=b''
#             lc+=1 # We skip the "Second byte"
#         return head+st[lc:],substr,0
#     else:
#         lc-=2
#         return startbytes+st[lc:],substr,0
reconstructed_nal_unit = bytearray()

def parse_rtp_packet(packet):
    global reconstructed_nal_unit
    # Define RTP header length
    RTP_HEADER_LENGTH = 12
    
    # Extract RTP header and payload
    rtp_header = packet[:RTP_HEADER_LENGTH]
    payload = packet[RTP_HEADER_LENGTH:]

    # Print RTP header
    debug_print("RTP Header: " + str(rtp_header.hex()))

    # Identify NAL unit type
    nal_header = payload[0]
    nal_unit_type = nal_header & 0x1F
    debug_print(f"NAL Unit Type: {nal_unit_type}")
    # debug_print(bitstring.BitArray(bytes=bytearray([nal_header])).bin)
    # debug_print(bitstring.BitArray(bytes=bytearray(b'\x1F')).bin)
    # debug_print(bitstring.BitArray(bytes=bytearray([nal_unit_type])).bin)



    if nal_unit_type >= 1 and nal_unit_type <= 23:
        # Single NAL unit packet
        debug_print("Single NAL Unit Packet")
        if nal_unit_type == 12:
            # pass
            debug_print("Filler data")
            # reconstructed_nal_unit = bytearray()
            # return None

        nal_unit = payload[1:]
    elif nal_unit_type == 28 or nal_unit_type == 29:
        # Fragmented NAL units (FU-A or FU-B)
        debug_print("Fragmented NAL Unit")
        fu_header = payload[1]
        start_bit = fu_header & 0x80
        end_bit = fu_header & 0x40
        nal_unit_type = fu_header & 0x1F

        if nal_unit_type == 12:
            # pass
            debug_print("Filler data")
            # reconstructed_nal_unit = bytearray()
            # return None
        elif nal_unit_type == 1:
            debug_print("Coded slice of a non-IDR picture")
        elif nal_unit_type == 5:
            debug_print("Coded slice of an IDR picture")
        elif nal_unit_type == 30:
            debug_print("undefined")
            exit()
        elif nal_unit_type == 31:
            debug_print("undefined")
            exit()
        else:
            debug_print("Not identified yet")

        if start_bit:
            debug_print("**Start of fragmented NAL unit")
            reconstructed_nal_unit.append((nal_header & 0xE0) | nal_unit_type)
            reconstructed_nal_unit.extend(payload[2:])
        else:
            debug_print("*Continuation of fragmented NAL unit")
            reconstructed_nal_unit.extend(payload[2:])
        
        if end_bit:
            debug_print("##End of fragmented NAL unit")
            nal_unit = bytes(reconstructed_nal_unit)
            reconstructed_nal_unit = bytearray()
        else:
            nal_unit = None
    else:
        debug_print("Unsupported NAL Unit Type")
        nal_unit = None

    return nal_unit


def digestpacket(st):
    """ This routine takes a UDP packet, i.e. a string of bytes and ..
    (a) strips off the RTP header
    (b) adds NAL "stamps" to the packets, so that they are recognized as NAL's
    (c) Concantenates frames
    (d) Returns a packet that can be written to disk as such and that is recognized by stock media players as h264 stream
    """
    stb = b""
    head = b""
    bt = b""
    startbytes=b"\x00\x00\x00\x01" # this is the sequence of four bytes that identifies a NAL packet.. must be in front of every NAL packet.
    stb = bitstring.BitArray(bytes=startbytes)
    bt = bitstring.BitArray(bytes=st) # turn the whole string-of-bytes packet into a string of bits.  Very unefficient, but hey, this is only for demoing.
    
    lc=12 # bytecounter
    bc=12*8 # bitcounter

    version=bt[0:2].uint # version
    p=bt[3] # P
    x=bt[4] # X
    cc=bt[4:8].uint # CC
    m=bt[9] # M
    pt=bt[9:16].uint # PT
    sn=bt[16:32].uint # sequence number
    timestamp=bt[32:64].uint # timestamp
    ssrc=bt[64:96].uint # ssrc identifier
    # The header format can be found from:
    # https://en.wikipedia.org/wiki/Real-time_Transport_Protocol

    lc=12 # so, we have red twelve ----ytes
    bc=12*8 # .. and that many -----bits

    # print ("version, p, x, cc, m, pt",version,p,x,cc,m,pt)
    # print ("sequence number, timestamp",sn,timestamp)
    # print ("sync. source identifier",ssrc)


    # OK, now we enter the NAL packet, as described here:
    # 
    # https://tools.ietf.org/html/rfc6184#section-1.3
    #
    # Some quotes from that document:
    #
    """
    5.3. NAL Unit Header Usage
    The structure and semantics of the NAL unit header were introduced in
    Section 1.3.  For convenience, the format of the NAL unit header is
    reprinted below:
        +---------------+
        |0|1|2|3|4|5|6|7|
        +-+-+-+-+-+-+-+-+
        |F|NRI|  Type   |
        +---------------+
    This section specifies the semantics of F and NRI according to this
    specification.
    """
    """
    Table 3.  Summary of allowed NAL unit types for each packetization
                    mode (yes = allowed, no = disallowed, ig = ignore)
        Payload Packet    Single NAL    Non-Interleaved    Interleaved
        Type    Type      Unit Mode           Mode             Mode
        -------------------------------------------------------------
        0      reserved      ig               ig               ig
        1-23   NAL unit     yes              yes               no
        24     STAP-A        no              yes               no
        25     STAP-B        no               no              yes
        26     MTAP16        no               no              yes
        27     MTAP24        no               no              yes
        28     FU-A          no              yes              yes
        29     FU-B          no               no              yes
        30-31  reserved      ig               ig               ig
    """
    # This was also very usefull:
    # http://stackoverflow.com/questions/7665217/how-to-process-raw-udp-packets-so-that-they-can-be-decoded-by-a-decoder-filter-i
    # A quote from that:
    """
    First byte:  [ 3 NAL UNIT BITS | 5 FRAGMENT TYPE BITS] 
    Second byte: [ START BIT | RESERVED BIT | END BIT | 5 NAL UNIT BITS] 
    Other bytes: [... VIDEO FRAGMENT DATA...]
    """

    fb=bt[bc] # i.e. "F"
    nri=bt[bc+1:bc+3].uint # "NRI"
    nlu0=bt[bc:bc+3] # "3 NAL UNIT BITS" (i.e. [F | NRI])
    typ=bt[bc+3:bc+8].uint # "Type"
    print('F: %d, NRI: %d, Type: %d'% (fb, nri, typ))
    print ("first three bits together :",bt[bc:bc+3])

    if(typ == 1):  
        print ("Single NAL unit")
        
        return stb + bt[bc:]
    
    if(typ == 24):
        print ("STAP-A packet")
        
        

    if(typ == 28):
        print ("FU-A packet")
        bc+=8; lc+=1; # let's go to "Second byte"
        # ********* WE ARE AT THE "Second byte" ************
        # The "Type" here is most likely 28, i.e. "FU-A"
        start=bt[bc+0] # start bit
        end=bt[bc+1] # end bit
        nlu1=bt[bc+3:bc+8] # 5 nal unit bits
        print("5 nal unit bits: ", nlu1.uint)
        if nlu1.uint == 12:
            print ("Filler data found")
            return b''

        if (start): # OK, this is a first fragment in a movie frame
            print (">>> first fragment found")
            nlu=nlu0+nlu1 # Create "[3 NAL UNIT BITS | 5 NAL UNIT BITS]"
            head=stb+nlu # .. add the NAL starting sequence
            print(head)        
            lc+=1 # We skip the "Second byte"
        elif (start==False and end==False): # intermediate fragment in a sequence, just dump "VIDEO FRAGMENT DATA"
            head=b""
            print ("<<<< intermediate fragment found")
            lc+=1 # We skip the "Second byte"
        elif (end==True): # last fragment in a sequence, just dump "VIDEO FRAGMENT DATA"
            head=b""
            print ("<<<< last fragment found")
            lc+=1 # We skip the "Second byte"
        return head + bt[lc:]
    
    else:
        print ("unknown frame type for this piece of s***")
        return b""


    # if (typ==7 or typ==8):
    #     # this means we have either an SPS or a PPS packet
    #     # they have the meta-info about resolution, etc.
    #     # more reading for example here:
    #     # http://www.cardinalpeak.com/blog/the-h-264-sequence-parameter-set/
    #     if (typ==7):
    #         print (">>>>> SPS packet")
    #     else:
    #         print (">>>>> PPS packet")
    #     return head + bt[lc:]
        # .. notice here that we include the NAL starting sequence "startbytes" and the "First byte"

    

    

    # print ("sequence number =",sn,'   Frame  Type   ',typ)
    # print ("H264 Header:",bytes(head).hex())
    # print ("H264 Payload:", bytes(bt[lc:]).hex())

    
    # if (typ==28 or typ==1 or typ==12): # This code only handles "Type" = 28, i.e. "FU-A"
    #     # return "test"
    # else:
    #     print ("unknown frame type for this piece of s***")
    #     return "test"

        # raise(Exception,"unknown frame type for this piece of s***")

def check_port():
    host = 'localhost'
    port = 554
    global play

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        s.settimeout(2)
        s.connect(("localhost", 554))

        # SENDING OPTIONS
        s.send(opt.encode())
        print ("Request sent")
        print (opt)
        response = s.recv(4096)
        print("response: ")
        print(response.decode())

        # SENDING DESCRIBE
        s.send(desc.encode())
        print ("Request sent")
        print (desc)
        response = s.recv(4096)
        print("response: ")
        print(response.decode())
        # bitStringstr = bitstring.BitArray(bytes=response).bin
        # print(bitStringstr)

        # v=0
        # o=- 91716953419 1 IN IP4 127.0.0.1
        # t=0 0
        # a=control:*
        # m=video 0 RTP/AVP 96
        # a=rtpmap:96 H264/90000
        # a=fmtp:96 packetization-mode=1;profile-level-id=640032;sprop-parameter-sets=Z2QAMqzZQHgCXsBagICAoAAAfSAAF3AR4wYywA==,aO+8sA==

        # Parsing and get the value of sprop-parameter-sets
        sps = response.decode().split("sprop-parameter-sets=")[1].split(",")[0]
        print(sps)
        pps = response.decode().split("sprop-parameter-sets=")[1].split(",")[1]
        print(pps)

        # Convert the base64 string to hexa
        sps = base64.b64decode(sps)
        pps = base64.b64decode(pps)

        # print(bitstring.BitArray(bytes=sps).bin)
        # print(pps.hex())
        

    
        

        # SEND SETUP 0
        s.send(setu0.encode())
        print ("Request sent")
        print (setu0)
        response = s.recv(4096)
        print("response: ")
        print(response.decode())
        sessionId = response.decode().split("Session: ")[1].split("\r\n")[0]
        print(sessionId)

        # SEND SETUP 1
        # s.send(setu1.encode())
        # print ("Request sent")
        # print (setu1)
        # response = s.recv(4096)
        # print("response: ")
        # print(response.decode())
        # sessionId = response.decode().split("Session: ")[1].split("\r\n")[0]
        # print(sessionId)

        # SEND SETUP 2
        # s.send(setu2.encode())
        # print ("Request sent")
        # print (setu2)
        # response = s.recv(4096)
        # print("response: ")
        # print(response.decode())
        # sessionId = response.decode().split("Session: ")[1].split("\r\n")[0]
        # print(sessionId)

        
        # SEND SETUP 3
        # s.send(setu3.encode())
        # print ("Request sent")
        # print (setu3)
        # response = s.recv(4096)
        # print("response: ")
        # print(response.decode())
        # sessionId = response.decode().split("Session: ")[1].split("\r\n")[0]
        # print(sessionId)


        # SEND SETUP 4
        # s.send(setu4.encode())
        # print ("Request sent")
        # print (setu4)
        # response = s.recv(4096)
        # print("response: ")
        # print(response.decode())
        # sessionId = response.decode().split("Session: ")[1].split("\r\n")[0]
        # print(sessionId)


        # SEND SETUP 5
        # s.send(setu5.encode())
        # print ("Request sent")
        # print (setu5)
        # response = s.recv(4096)
        # print("response: ")
        # print(response.decode())
        # sessionId = response.decode().split("Session: ")[1].split("\r\n")[0]
        # print(sessionId)




        # SEND SETUP 6
        # s.send(setu6.encode())
        # print ("Request sent")
        # print (setu6)
        # response = s.recv(4096)
        # print("response: ")
        # print(response.decode())

        sessionId = response.decode().split("Session: ")[1].split("\r\n")[0]
        print("Session ID: ")
        print(sessionId)

        play = play.replace("FLAG_1", sessionId)

        s1=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s1.bind(("", clientports[0])) # we open a port that is visible to the whole internet (the empty string "" takes care of that)
        s1.settimeout(5) # if the socket is dead for 5 s., its thrown into trash
        print("Socket created")
        print("Socket bind complete")
        print("Socket now listening")


        # SEND PLAY
        s.send(play.encode())
        print ("Request sent")
        print (play)
        response = s.recv(4096)
        print("response: ")
        print(response.decode())

        f=open(fname,'wb')
        # Generate SPS and PPS for 1920x1080 resolution
        # sps, pps = generate_sps_pps(1920, 1080)
        headerH264 = b'\x00\x00\x00\x01'
        # headerH264= bytearray(headerH264)
        # print(headerH264)


        # Print SPS and PPS byte arrays as hexadecimal
        # print("SPS:", ''.join('{:02x} '.format(byte) for byte in sps))
        # print("PPS:", ''.join('{:02x} '.format(byte) for byte in pps))
        f.write(headerH264)
        f.write(sps)
        f.write(headerH264)
        f.write(pps)
        for i in range(rn):
            debug_print("========================"+str(i+1)+"============================")
            recst=s1.recv(10800)
            # debug_print(' '.join(recst.hex()[i:i+2] for i in range(0, len(recst.hex()), 2)))
            # debug_print(decode_rtp_packet(recst))
            # recst=s1.recv(4096)
            debug_print ("read"+str(len(recst))+"bytes")
            nal_unit = parse_rtp_packet(recst)
            
            if nal_unit is not None:
                # debug_print("Nal unit: " + nal_unit.hex())
                f.write(headerH264)
                f.write(nal_unit)
                
            else:
                debug_print("Nal unit is None")

            # st=digestpacket(recst)
            # print ("dumping",len(bytes(st)),"bytes")
            # print(' '.join(bytes(st).hex()[i:i+2] for i in range(0, len(bytes(st).hex()), 2)))
            # print(bytes(st).hex())
            # f.write(bytes(st))

            
        #     # st=digestpacket(recst)
        #     # print ("dumping",len(st),"bytes")
        #     # f.write(st)
        # try:
        #     resid,conti = ''.encode(),0
        #     for i in range(rn):
        #         print("========================",i+1,rn,"============================")
        #         recst = resid + s1.recv(4096)
        #         if len(recst) == 0:
        #             break
        #         conti = 0
        #         print ("read",len(recst),"bytes")
        #         while len(recst) != 0 and conti == 0:
        #             st,recst,conti=digestpacket(recst)
        #             resid = ''.encode()
        #             if conti == 1:
        #                 resid = recst
        #             if len(st)!=0:
        #                 print ("dumping",len(st),"bytes")
        #                 f.write(str(st))
        # except Exception as e: 
        #     print(e)
        f.close()


        # Close the socket
        
        
        


        s.close()
        s1.close()

        # testByteArr = b'\x00\x00\x00\x01'
        # test1 = bitstring.BitArray(bytes=testByteArr)
        # print(test1)
        # print(test1 + test1)
    except socket.error as e:
        print(f"Error: {e}")

# Call the function to check the port
check_port()

