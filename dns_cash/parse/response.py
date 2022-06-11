import parse.header_flags
import dns
from support_function import SupportFunction
from parse.msg_controller import MSGController


class Response:
    global dnss
    dnss = dns.DNS()

    @staticmethod
    def build_response(data):
        ID = data[0:2]
        FLAGS = Response.build_response_flags(data[2:4])
        QDCOUNT = b'\x00\x01'
        records_data = dnss.get_records(data[12:])
        ANCOUNT = len(records_data[0]).to_bytes(2, byteorder='big')
        NSCOUNT = (0).to_bytes(2, byteorder='big')
        ARSCOUNT = (0).to_bytes(2, byteorder='big')
        header = ID + FLAGS + QDCOUNT + ANCOUNT + NSCOUNT + ARSCOUNT
        body = b''
        records, rec_type, domain = records_data
        question = dnss.build_question(domain, rec_type)
        for record in records:
            body += dnss.record_to_bytes(rec_type, record['ttl'], record['value'])
        print(f'Response to the request "{rec_type}" has been sent')
        return header + question + body

    @staticmethod
    def make_response(data):
        request_info = MSGController.parse_incoming_request(data)
        response = b''
        req_type = request_info['question']['QTYPE']
        if req_type == 'a' or req_type == 'ns':
            print(f'Received a request of the type "{req_type}"')
            response = Response.build_response(data)

        return response

    @staticmethod
    def build_response_flags(flags):
        first_byte = flags[:1]
        OPCODE = ''
        for bit in range(1, 5):
            OPCODE += str(ord(first_byte) & (1 << bit))

        first_byte_str = parse.header_flags.QR + OPCODE + parse.header_flags.AA \
                         + parse.header_flags.TC + parse.header_flags.RD
        second_byte_str = parse.header_flags.RA + parse.header_flags.Z + parse.header_flags.RCODE

        return SupportFunction.flags_to_bytes(first_byte_str) + SupportFunction.flags_to_bytes(
            second_byte_str)
