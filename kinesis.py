#######################################
# Author Email: dorfer@aps.ee.ethz.ch
#######################################

from configobj import ConfigObj
from utils import demo

class Kinesis():
    def __init__(self, conf):
        self.conf = conf
        self.demo_mode = conf['DemoRun'].as_bool('demo')
        self.open_connection()

        self.lock_state = False

    @demo
    def open_connection(self):
        addr = self.conf['PositionControl']['address']

    def move_x(self, pos):
        if self.lock_state:
            return
        print('moving in x')

    def move_y(self, pos):
        if self.lock_state:
            return
        print('moving in y')


    def get_x_pos(self):
        return 1

    def get_y_pos(self):
        return 2


    def center_stage(self):
        return 1

if __name__ == '__main__':
    config = ConfigObj('config.ini')['PositionControl']

