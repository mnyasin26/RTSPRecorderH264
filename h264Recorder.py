

class H264Recorder:

    header = bytearray([0x00, 0x00, 0x00, 0x01])
    sps = None
    pps = None
    file = None
    filename = None

    def __init__(self, filename="output.h264"):
        self.filename = filename

    def setSPS(self, sps):
        self.sps = sps
    
    def setPPS(self, pps):
        self.pps = pps

    def setFilename(self, filename):
        self.filename = filename

    def start(self):
        self.file = open(self.filename, "wb")
        self.file.write(self.header)
        self.file.write(self.sps)
        self.file.write(self.header)
        self.file.write(self.pps)
        self.recording = True

    def feed(self, nal_unit):
        if self.recording:
            self.file.write(self.header)
            self.file.write(nal_unit)

    def stop(self):
        self.file.close()
        self.recording = False
