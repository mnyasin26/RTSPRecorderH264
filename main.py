import base64
from commandRTSP import RTSPClient
from packetParserRTP import parseRtpPacket
from h264Recorder import H264Recorder
from paho.mqtt import client as mqtt
import time
import random


broker = '52.221.249.234'
port = 1883
client_id = f'publish-{random.randint(0, 1000)}'

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt.Client(client_id)
    # client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("$SYS/#")

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

def main():

    mqttClient =  connect_mqtt()
    # mqttClient.on_connect = on_connect
    # mqttClient.on_message = on_message
    # mqttClient.connect("52.221.249.234", 1883)


    # if mqttClient.is_connected():
    #     print("Connected to MQTT Broker")
    # else:
    #     print("Failed to connect to MQTT Broker")
    #     return
    mqttClient.loop_start()
    

    Rtsp = RTSPClient('localhost', 554)
    Rec = H264Recorder("output.h264")


    Rtsp.connect()
    print(Rtsp.options())
    res, sps, pps = Rtsp.describe()
    print(res)
    print(sps)
    print(pps)

    Rec.setSPS(base64.b64decode(sps))
    Rec.setPPS(base64.b64decode(pps))
    Rec.start()

    print(Rtsp.setup())
    print(Rtsp.play())

    Rtsp.setPakcetNum(5000)

    counter = 0
    counterPacket = 0
    totalBytes = 0
    rtp_packet = ''
    while rtp_packet != None:
        # mqttClient.loop()
        rtp_packet = Rtsp.listen()
        if rtp_packet is None:
            break
        nal_unit = parseRtpPacket(rtp_packet)
        counterPacket += 1
        # print("Packet: " + str(counterPacket))
        if nal_unit is not None:
            # print(nal_unit.hex())
            Rec.feed(nal_unit)
            counter += 1
            totalBytes += len(nal_unit)

            mqttClient.publish("h264", nal_unit.hex())
            
            print("RTP Packet Num: " + str(counterPacket), end=' ')
            print("Nal unit Num: " + str(counter), end=' ')
            print("Total Bytes: " + str(totalBytes), end=' ')
            print("Nal unit Size: " + str(len(nal_unit)))
        else:
            pass
            # print("Nal unit is None")
    Rec.stop()
    print(Rtsp.teardown())
    mqttClient.loop_stop()

if __name__ == '__main__':
    main()

