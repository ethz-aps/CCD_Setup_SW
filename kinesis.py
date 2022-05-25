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

    def moveX(self, pos):
        if self._conf.as_bool('lock_state'):
            return
        print('moving in x')

    def moveY(self, pos):
        if self._conf.as_bool('lock_state'):
            return
        print('moving in y')


    def set_lock_state(self, lock_state):
        if lock_state == True:
            self._conf['lock_state'] = True
        else:
            self._conf['lock_state'] = False



if __name__ == '__main__':
    config = ConfigObj('config.ini')['PositionControl']

