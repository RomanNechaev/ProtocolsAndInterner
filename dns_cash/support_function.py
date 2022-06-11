class SupportFunction:
    @staticmethod
    def make_ipv4_from_bytes(data):
        ip = ''
        for byte in data:
            ip += str(byte) + '.'
        return ip.rstrip('.')

    @staticmethod
    def flags_to_bytes(*args):
        string = ''
        for arg in args:
            string += arg
        return int(string, 2).to_bytes(1, byteorder='big')