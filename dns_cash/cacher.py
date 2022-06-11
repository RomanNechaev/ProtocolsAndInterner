import glob
import json


class Cacher:
    def __init__(self):
        self.info_files = glob.glob('cash/*.cfg')

    def get_data(self):
        json_info = {}
        for zone in self.info_files:
            with open(zone) as file:
                data = json.load(file)
                origin = data['origin']
                json_info[origin] = data
        return json_info

    @staticmethod
    def save_info_data(data):
        with open(f'cash/{data["origin"]}.cfg', 'w+') as file:
            json.dump(data, file)
