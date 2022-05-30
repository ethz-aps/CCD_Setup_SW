#######################################
# Author Email: dorfer@aps.ee.ethz.ch
#######################################

import pyvisa as visa
from time import sleep, time
from configobj import ConfigObj


from utils import demo, random_number

class KeithleyK2470():
    def __init__(self, conf):
        self._conf = conf['HighVoltageControl']
        self.demo_mode = conf['DemoRun'].as_bool('demo')

        self.open_connection()

    @demo
    def open_connection(self):
        rm = visa.ResourceManager('@py')
        self._inst = rm.open_resource(self._conf['address'], timeout=self._conf.as_int('timeout_ms'))
        #self.write('ABORt')
        #self.write('*RST')
        sleep(2)
        print("Connected to: ", self.query("*idn?").rstrip())

    @demo
    def write(self, command):
        self._inst.write(command)
        err = self.get_full_error_queue(verbose=False)
        for e in err:
            if e.split(',')[0] != '0':
                print(f"Errors while writing {command} to instrument")
                print(e)

    @demo
    def query(self, command):
        try:
            return self._inst.query(command).strip()
        except visa.Error as err:
            msg = f"query '{command}'"
            print(f"\n\nVisaError: {err}\n  When trying {msg}  (full traceback below).")
            print(f"  Have you checked that the timeout (currently "
                  f"{self.timeout:,d} ms) is sufficently long?")
            try:
                self.get_full_error_queue(verbose=True)
                print("")
            except Exception as excep:
                print("Could not retrieve errors!")
                print(excep)
                print("")
            raise
    
    @demo
    def get_full_error_queue(self, verbose=False):
        """All the latest errors from the oscilloscope, upto 30 errors
        (and store to the attribute ``errors``)"""
        errors = []
        for i in range(100):
            err = self._inst.query(":SYSTem:ERRor?").strip()
            if err[:2] == "+0":  # No error
                # Stop querying
                break
            else:
                # Store the error
                errors.append(err)
        if verbose:
            if not errors:
                print("Error queue empty")
            else:
                print("Latest errors:")
                for i, err in enumerate(errors):
                    print(f"{i:>2}: {err}")
        return errors

    @demo
    def close(self):
        self._inst.close()


    def configure(self):
        self.write('system:posetup rst') #reset the instrument
        #self.write('trace:delete "currpts"')

        self.write(f':SENSe:CURRent:NPLCycles {self._conf.as_float("nplcycles")}') #1 power line cycle =20ms in EU
        self.write(':SENSe:CURRent:AZERo:STATe ON') #check if maybe it needs to be disabled for all functions
        self.write(':SOURce:VOLTage:READ:BACK OFF') #no voltage readback from source unit --> voltage might be off the real value
        #self.write(':SENS:CURR:RANG 100E-9') #automatically removes the autorange setup of the instrument

        #set limitation on the current for the voltage source
        self.write(f'SOURCe:VOLTage:ILIMit {self._conf.as_float("current_compliance")}')

        #do an autozero for the current measurement
        self.write(':SENS:AZERo:ONCE') #do an autozero before the measurement


    def setBias(self, voltage):
        self.write(':SOUR:VOLT %f' % voltage)
        #sleep(1)
        #self.write(':SENS:AZERo:ONCE') #do an autozero before the measurement


    def toggleOutput(self, on=False):
        if on:
            self.write(':OUTPUT ON') 
        else:
            self.write(':OUTPUT OFF') 


    def getCurrent(self):
        data = self._inst.query_ascii_values('READ?')
        return data

    def getDummyCurrent(self):
        voltage = 1
        curr = random_number()
        return (voltage, curr)



if __name__ == '__main__':
    config = ConfigObj('config.ini')['HighVoltageControl']
    k = KeithleyK2470(config)
    k.write("abort")
    sleep(1)
    k.write("*rst")
    sleep(1)
    k.configure()
