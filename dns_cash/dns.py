import socket
import datetime
from parse.msg_controller import MSGController
from cfg import GOOGLE_NS, ttl_m
from cacher import Cacher
from support_function import SupportFunction


class DNS:
    def __init__(self):
        self.cacher = Cacher()
        self.INFO_DATA = self.cacher.get_data()

    def make_info_from_response(self, data, domain, qtype):
        question = self.build_question(domain, qtype)
        ANCOUNT = int.from_bytes(data[6:8], 'big')
        answer = data[12 + len(question):]
        records = self.get_records_from_answer(answer, ANCOUNT)
        origin = '.'.join(domain)
        time = str(datetime.datetime.now())
        cash_data = {'origin': origin, 'time': time, 'data': records, 'ttl': ttl_m}
        self.INFO_DATA[origin] = cash_data
        self.cacher.save_info_data(cash_data)
        return cash_data

    @staticmethod
    def get_records_from_answer(answer, count):
        ptr = 0
        records = {}
        for _ in range(count):
            record = {}
            rec_type = int.from_bytes(answer[ptr + 2: ptr + 4], 'big')
            ttl = int.from_bytes(answer[ptr + 6:ptr + 10], 'big')
            rd_length = int.from_bytes(answer[ptr + 10: ptr + 12], 'big')
            rd_data = ''
            if rec_type == 1:
                rd_data = SupportFunction.make_ipv4_from_bytes(answer[ptr + 12:ptr + 12 + rd_length])
            if rec_type == 2:
                rd_data = answer[ptr + 12:ptr + 12 + rd_length].hex()
            ptr += 12 + rd_length
            rec_type = MSGController.make_type_from_number(rec_type)
            record['ttl'] = ttl
            record['value'] = rd_data
            if rec_type in records:
                records[rec_type].append(record)
            else:
                records[rec_type] = [record]
        return records

    def find_data(self, domain, qtype):
        request = self.build_request(domain, qtype)
        temp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            temp_sock.sendto(request, GOOGLE_NS)
            data, _ = temp_sock.recvfrom(512)
        finally:
            temp_sock.close()
        info = self.make_info_from_response(data, domain, qtype)
        return info

    def get_info(self, domain, info_data, qtype):
        info_name = '.'.join(domain)
        info = None
        if info_name in info_data:
            print(f"FROM CASH:")
            info = info_data[info_name]
            if qtype in info['data']:
                time = datetime.datetime.fromisoformat(info['time'])
                ttl = info['ttl']
                current_time = datetime.datetime.now()
                if (current_time - time).seconds > ttl:
                    print(f'Data were out of date. Turn to the senior DNS server')
                    info = self.find_data(domain, qtype)
            else:
                print(f'No data found for the query = {qtype}. Turn to the senior DNS server')
                info = self.find_data(domain, qtype)
        else:
            print(f'There is no data in the cache. Turn to the senior DNS server.')
            info = self.find_data(domain, qtype)

        return info

    def get_records(self, data):
        domain, question_type = MSGController.get_question_domain(data)
        QT = ''
        if question_type == b'\x00\x01':
            QT = 'a'
        if question_type == (12).to_bytes(2, byteorder='big'):
            QT = 'ptr'

        if question_type == (2).to_bytes(2, byteorder='big'):
            QT = 'ns'

        recs = None
        if QT == 'a' or QT == 'ns':
            info = self.get_info(domain, self.INFO_DATA, QT)
            recs = info['data'][QT]

        return recs, QT, domain

    @staticmethod
    def build_question(domain, rec_type):
        question = b''

        for part in domain:
            length = len(part)
            question += bytes([length])

            for char in part:
                question += ord(char).to_bytes(1, byteorder='big')

        if rec_type == 'a':
            question += (1).to_bytes(2, byteorder='big')
        if rec_type == 'ns':
            question += (2).to_bytes(2, byteorder='big')

        question += (1).to_bytes(2, byteorder='big')
        return question

    @staticmethod
    def record_to_bytes(rec_type, ttl, value):
        record = b'\xc0\x0c'

        if rec_type == 'a':
            record += bytes([0]) + bytes([1])
        if rec_type == 'ns':
            record += bytes([0]) + bytes([2])

        record += bytes([0]) + bytes([1])
        record += int(ttl).to_bytes(4, byteorder='big')

        if rec_type == 'a':
            record += bytes([0]) + bytes([4])

            for part in value.split('.'):
                record += bytes([int(part)])
        if rec_type == 'ns':
            byte_value = bytes(bytearray.fromhex(value))
            record += bytes([0]) + bytes([len(byte_value)])
            record += byte_value
        return record

    def build_request(self, domain, qtype):
        ID = b'\xAA\xAA'
        FLAGS = b'\x01\x00'
        QDCOUNT = b'\x00\x01'
        ANCOUNT = (0).to_bytes(2, byteorder='big')
        NSCOUNT = (0).to_bytes(2, byteorder='big')
        ARSCOUNT = (0).to_bytes(2, byteorder='big')
        header = ID + FLAGS + QDCOUNT + ANCOUNT + NSCOUNT + ARSCOUNT
        question = self.build_question(domain, qtype)
        return header + question
