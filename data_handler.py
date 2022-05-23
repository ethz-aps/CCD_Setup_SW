import os
import h5py
import datetime
from pathlib import Path


class DataHandler(object):
     
    def __init__(self, conf):
        self.conf = conf
        self.hdf = None
        self.data = None
        self.runnumber = self.readRunNumber()+1


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

    def createFile(self):    
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
        self.data.attrs['dut_name'] = 1
        self.data.attrs['number_of_events'] = 1
        self.data.attrs['excitation_source'] = 1
        self.data.attrs['amp_serial_number'] = 1
        self.data.attrs['veto_scint_voltage'] = 1
        self.data.attrs['trg_scint_voltage'] = 1

        self.data.attrs['bias_voltage'] = 1
        self.data.attrs['compliance'] = 1
        self.data.attrs['abort_on_compliance'] = 1

        self.data.attrs['time_axis'] = 1

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
    
