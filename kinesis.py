#######################################
# Author Email: dorfer@aps.ee.ethz.ch
#######################################

from configobj import ConfigObj
from utils import demo

class Kinesis():
    def __init__(self, conf):
        self._conf = conf['PositionControl']
        self.demo_mode = conf['DemoRun'].as_bool('demo')
        self.open_connection()

    @demo
    def open_connection(self):
        addr = self._conf['address']

    def move_x(self, pos):
        if self._conf.as_bool('lock_state'):
            return
        print('moving in x')

    def move_y(self, pos):
        if self._conf.as_bool('lock_state'):
            return
        print('moving in y')


    def set_lock_state(self, lock_state):
        if lock_state == True:
            self._conf['lock_state'] = True
        else:
            self._conf['lock_state'] = False

    def get_lock_state(self):
        return self._conf.as_bool('lock_state')

    def get_x_pos(self):
        return 1

    def get_y_pos(self):
        return 2


    def center_stage(self):
        return 1

if __name__ == '__main__':
    config = ConfigObj('config.ini')['PositionControl']

