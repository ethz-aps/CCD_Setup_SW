#######################################
# Author Email: dorfer@aps.ee.ethz.ch
#######################################

import os
import h5py
import datetime
from time import time
from pathlib import Path


class DataHandler(object):
     
    def __init__(self, conf, hvplot):
        self.conf = conf
        self.hdf = None
        self.data = None
        self.runnumber = self.readRunNumber()+1

        self.hvplot = hvplot

        self.times = []
        self.voltages =[]
        self.currents = []

        self.scope_config = None


    def setHVData(self, v, c):
        self.times.append(time())
        self.voltages.append(v)
        self.currents.append(c)
        self.hvplot.updatePlot(self.times, self.voltages, self.currents)


    def readRunNumber(self):        
        dir_path = os.path.dirname(os.path.realpath(__file__))
        Path(f"{dir_path}/data/").mkdir(exist_ok=True)
        try:
            with open('data/runnumber.dat', "r") as f:
                return int(f.readline())
        except FileNotFoundError:
            with open('data/runnumber.dat', "w") as f:
                f.write("1\n")
            return 0


    def increaseRunNumber(self):
        with open('data/runnumber.dat', "r+") as f:
            runnumber = int(f.readline())
            f.seek(0)
            f.write(str(runnumber+1))
            return (runnumber+1)

    def createFile(self, scope_config=None, run_config=None):    
        #reset old one
        self.hdf= None
        self.data=None

        #read and increase run number
        self.runnumber = self.increaseRunNumber()
        print('Run number: ', self.runnumber)
         
        #create new h5py file
        fname = 'data/run' + str(self.runnumber) + ".hdf5"
        self.hdf = h5py.File(fname, "w", libver='latest')
        self.hdf.attrs['timestamp'] = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())

        self.data = self.hdf.create_group("data")
        conf = self.conf['RunSettings']
        self.data.attrs['dut_name'] = conf['last_sample']
        self.data.attrs['number_of_events'] = conf.as_int('events_per_run')
        self.data.attrs['excitation_source'] = conf['excitation_source']
        self.data.attrs['amp_serial_number'] = conf.as_int('amplifier_serial_nr')
        self.data.attrs['veto_scint_voltage'] = conf.as_float('veto_scint_voltage')
        self.data.attrs['trg_scint_voltage'] = conf.as_float('trigger_scint_voltage')

        conf = self.conf['HighVoltageControl']
        self.data.attrs['bias_voltage'] = conf.as_float('bias_voltage')
        self.data.attrs['compliance_nA'] = conf.as_float('current_compliance_nA')
        self.data.attrs['abort_on_compliance'] = conf.as_bool('abort_on_compliance')

        if scope_config:
            self.data.attrs['time_axis'] = scope_config['x_axis']
        else:
            self.data.attrs['time_axis'] = 0

        print('File ', fname, ' open for writing.')
 



    
    def addData(self, timestamp, x, y, wfarr):
        self.data.create_dataset(sp, data=wfarr, compression="gzip")
        self.data[sp].attrs['timestamp'] = timestamp
        self.data[sp].attrs['x'] = x
        self.data[sp].attrs['y'] = y
        self.spcount += 1


    def closeFile(self):
        self.hdf.close()
        print('File for run ', str(self.runnumber), ' closed.')
    
