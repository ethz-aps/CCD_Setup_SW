#######################################
# Author Email: dorfer@aps.ee.ethz.ch
#######################################

from configobj import ConfigObj
from utils import demo
from time import sleep

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
        sleep(0.1)
        print('moving to x=', pos)

    def move_y(self, pos):
        sleep(0.1)
        print('moving to x=', pos)

    def get_x_pos(self):
        return 1

    def get_y_pos(self):
        return 2


    def center_stage(self):
        #find limits and center stage return [xmin, xval, xmax, ymin, yval, ymax]
        return [-20, 0, 20, -20, 0, 20]

if __name__ == '__main__':
    config = ConfigObj('config.ini')['PositionControl']

