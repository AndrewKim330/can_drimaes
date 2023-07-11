import can


class CANMessageSend(object):
    def __init__(self, bus):
        self.bus = bus

    def send_message(self, sig_id, send_data):
        print("aaa")
        message = can.Message(arbitration_id=sig_id, data=send_data)
        self.bus.send(message)
