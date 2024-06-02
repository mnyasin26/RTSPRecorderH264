from dev_config import debug_print

reconstructed_nal_unit = bytearray()
counterPacketNum = 0

def parseRtpPacket(packet):
    
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
            return None

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
            return None
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
            # if nal_unit_type != 5:
                # debug_print("Coded slice of a non-IDR picture")
                # return None
            nal_unit = bytes(reconstructed_nal_unit)

            reconstructed_nal_unit = bytearray()
        else:
            nal_unit = None
    else:
        debug_print("Unsupported NAL Unit Type")
        nal_unit = None

    return nal_unit