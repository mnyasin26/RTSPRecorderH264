import socket
# import rtsp
import bitstring
import base64
from datetime import datetime
from dev_config import debug_print
from dev_config import opt, desc, setu0, setu1, setu2, setu3, setu4, setu5, setu6, play, clientports, fname, rn


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

