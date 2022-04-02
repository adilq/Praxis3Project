import time

class Packet(object):
    data = None
    creation_time = time.monotonic()
    sent = False
    data_type = None

    def __init__(self, x):
        self.data = x
        self.update_type()


    def update_sent(self):
        self.sent = True

    def update_type(self):
        self.data_type = type(self.data)

    def convert(self):
        # convert bytearray to string
        if self.data is not None:
            data_string = ''.join([chr(b) for b in self.data])
            data_dict = {}
            #turn back into dictionary
            for subString in data_string.split(","):
                subString = subString.strip("{} '").split(":")
                data_dict[subString[0]] = subString[1]

            #format everything in the dictionary properly
            for key in data_dict.keys():
                new_key = key.strip("{} '")
                data_dict[new_key] = float(data_dict.pop(key))

            self.data = data_dict
            self.update_type()
            return data_dict
        else:
            return
