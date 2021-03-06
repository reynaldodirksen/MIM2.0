"""
Created on Wed Aug 19 2019

@author: Reynaldo Dirksen
"""


from serial import Serial 


class USBProgrammer:
    def __init__(self, port):            
        self.device = Serial()
        self.device.baudrate = 38400
        self.device.port = port
        self.device.parity = 'E'
        self.device.timeout = 0.1
        self.device.open()

        reply = self.send_command('smA')

        reply = self.send_command('vho1')

        if reply == '':
            reply = None

    @staticmethod
    def _calc_crc(value, size):
        """ Calculate CRC\n
            Conversion of C code on page 30 of HAL1820 programming guide (Micronas)
            :param value: int
            :param size: int
        """
        crc = 0
        for i in range(size - 1, -1, -1):
            bit_in = (value >> i) & 0x01
            bit_out = (crc >> 3) & 0x01
            bit_comp = (bit_out ^ bit_in) & 0x01
            crc = (crc << 1) + bit_comp
            crc = crc ^ (bit_comp << 1)

        return (crc & 0x0F)

    def send_command(self, cmd):
        """ Send a command to the USB programmer and return the reply.
            Handles conversion to/from UTF-8 and strips the CRLF from the reply.

            :param cmd command to send without CR or LF
        """
        self.device.flush()
        bytestring = cmd.encode('UTF-8') + b'\n'
        self.device.write(bytestring)

        bytestring = self.device.read_until(b'\n')
        # TODO: What if we get a timeout, is the bytestring empty or is an exception raised?
        reply = bytestring.decode('UTF-8')
        if reply[-2:] == '\r\n':
            reply = reply[:-2]

        return reply

    def read_firmware_version(self):
        reply = self.send_command('?v')

        return reply[2:]

    def read_voltage_out(self):
#        reply = self.send_command('xxr0A')
#        reply = self.send_command('xxw0300002')
#        reply = self.send_command('xxw10EB531')
#        reply = self.send_command('ftana1')
#        reply = self.send_command('ftsad0')
#        reply = self.send_command('ftvd10')
#
#        total = 0
#
#        samples = config.samples
#        for i in range(samples):
#            reply = self.send_command('ftana2')
#            total = total + int(reply[3:7], 16)
#        voltage = (((total / samples) * config.vsup)/1000)
#
#        reply = self.send_command('ftana1')
#        reply = self.send_command('ftvdl1')
#        reply = self.send_command('ftsad1')
        mdata = self.read_magnetic()
        if mdata == -100:
            voltage = 0
        else:
            voltage = 2.5+mdata*(5/1024)

        
        return round(voltage, 3)

    def read_voltage_out_times(self,samples):
        v = 0
        for i in range(samples):
            mdata = self.read_magnetic()
            if mdata == '':
                samples -=1
            else:
                v += 2.5+int(mdata)*(5/1024)
        voltage = v/samples
        return round(voltage, 3)

    def setup_continuous_voltage_read(self):
        reply = self.send_command('xxr0A')
        reply = self.send_command('xxw0300020')
        reply = self.send_command('xxw10EB531')
        reply = self.send_command('ftana1')
        reply = self.send_command('ftsad0')
        reply = self.send_command('ftvd10')

    def stop_continuous_voltage_read(self):
        reply = self.send_command('ftana1')
        reply = self.send_command('ftvdl1')
        reply = self.send_command('ftsad1')

    def read_continuous_voltage(self):
        total = 0

        samples = 5
        for i in range(samples):
            reply = self.send_command('ftana2')
            total = total + int(reply[3:7], 16)

        return round((((total / samples) * config.vsup)/1000), 3)

#    def read_voltage_sup(self):     #read vout in delphi
#        reply = self.send_command('xxr0A')
#        reply = self.send_command('xxw0300020')
#        reply = self.send_command('xxw10EB531')
#        reply = self.send_command('s')
#        reply = self.send_command('ftsad0')
#        reply = self.send_command('ftvd10')
#
#        total = 0
#
#        samples = config.samples
#        for i in range(samples):
#            reply = self.send_command('ftana1')
#            total = total + int(reply[3:7], 16)
#
#        voltage = ((total / samples) * 4.895) / 1000
#
#        reply = self.send_command('ftana1')
#        reply = self.send_command('ftvdl1')
#        reply = self.send_command('ftsad1')
#
#        return voltage

    def read_magnetic(self):
        reply = self.send_command('xxr02')
        if len(str(reply)) == 0:
            value = -100
        else:
            value = int(reply[2:6], 16) & 0X1FFF
        #crc = int(reply[7]) & 0x0F

        #valid = self._calc_crc(value, 14) == crc
        
        if value > 511:
            value = value - 1024

        #return valid, value
        return value

    def read_id(self):
        reply = self.send_command('xxr0B')

        sensor_id = reply[2:6]

        reply = self.send_command('xxr0C')

        sensor_id = sensor_id + ' ' + reply[2:6]
        if sensor_id == ' ':
            sensor_id = "0000 0000"
        return sensor_id
    
    def read_version(self):
        reply = self.send_command('xxr00')

        return reply[2:6]

    def read_setup(self):
        setup = dict()

        # Read version register to determine which HAL chip we have (1820 or 1860)
        reply = self.send_command('xxr00')[2:6]
        if reply == '':
            setup['mrange'] = 0
            setup['tc'] = 0
            setup['tcsq'] = 0
            setup['sensitivity'] = 0
            setup['offset'] = 0
            setup['version'] = 0
            setup['alignment'] = False
            setup['locked'] = False
            return setup
            
        
        if ((reply == '1F3A') or (reply == '2F3A')):
            setup['version'] = '1860'
        elif (reply == '074A'):
            setup['version'] = '1880'
        else:
            setup['version'] = '1820'
        # Read in customer setup registers
        reply = self.send_command('xxr07')
        register07 = int(reply[2:6], 16)
        reply = self.send_command('xxr08')
        register08 = int( reply[2:6], 16)
        reply = self.send_command('xxr09')
        register09 = int( reply[2:6], 16)
        # Parse customer setup registers and fill setup dict
        
        setup['tcsq'] = (register09 >> 8) & 0x1F  #fixed tcsq
        if setup['tcsq'] > 16:
            setup['tcsq'] = setup['tcsq'] - 32
        setup['tc'] = (register09 >>3) & 0x1F
        setup['mrange'] = register09 & 0x07
        setup['alignment'] = (register09 & 0x2000) > 0
        setup['locked'] = (register09 & 0x8000) > 0

        setup['sensitivity'] = (register08 >> 8) & 0xFF
        if setup['sensitivity'] > 127:
            setup['sensitivity'] = setup['sensitivity'] - 256
        setup['offset'] = register08 & 0xFF
        if setup['offset'] > 127:
            setup['offset'] = setup['offset'] - 256
        return setup

    def write_setup(self, setup):
        """

        :param setup:
        :return:
        """
        sens = setup['sensitivity'] #two's complement
        if sens > 127:
            sens = 127
        elif sens < -127:
            sens = -127
        if sens < 64 and sens >=0:
            sens = 64
        elif sens > -64 and sens < 0:
            sens = -64
        if sens < 0:
            sens = sens + 256
        
        offset = setup['offset'] #two's complement
        if offset > 127:
            offset = 127
        elif offset < -127:
            offset = -127
        if offset < 0:
            offset = offset + 256

        tcsq = int(setup['tcsq'])
        if tcsq < 0:
            tcsq = tcsq + 32 #signed binary
            
        # set latch bit
        reply = self.send_command('xxw0300020')
        # LC(1), DCLAMP(1), OALN(1), QTCOEF(5)
        # LTCOEF(5), MRANGE(3)
        value = ((tcsq & 0x01F) << 8) | ((setup['tc'] & 0x1F) << 3) | (setup['mrange'] & 0x07)
        if setup['alignment']:
            value = value | 0x2000
        if setup['locked']:
            value = value | 0x8000

        # Note: CRC has to be calculated over the WHOLE packet(the one send from the programming module
        #       to the hal1820 chip and not just over the data payload itself(like when reading).
        # Format: cccaaaaapdxxxxxxxxxxxxxxxx
        #         ccc = command(using reverse engineering found the write command to be 7) edit: ??RLD: the command it 6 here though?
        #         aaaaa = address to write
        #         p = parity bit
        #         d = dummy, always 0
        #         xx..xx = 16 bits value to write
        crc = self._calc_crc(((0x300 | 0x024 | 0x002) << 16) | value, 26)
        data = '{:05X}'.format((value << 4) + (crc & 0x0F))
        reply = self.send_command('xxw09' + data)

        value = ((sens & 0x0FF) << 8) + (offset & 0x0FF)
        crc = self._calc_crc(((0x300 | 0x020 | 0x00) << 16) | value, 26)
        data = '{:05X}'.format((value << 4) + (crc & 0x0F))
        reply = self.send_command('xxw08' + data)
        reply = self.send_command('xxw08' + data)
        
        value = 0x0300
        crc = self._calc_crc(((0x300 | 0x01C | 0x000) << 16) | value, 26)
        data = '{:05X}'.format((value << 4) + (crc & 0x0F))
        reply = self.send_command('xxw07' + data)
                             
        
       
        # Prepare to store
        reply = self.send_command('ftvdl1')
        reply = self.send_command('xxw0300020')
        reply = self.send_command('xxw1F459D8')
        reply = self.send_command('xxw1EECA1E')
        reply = self.send_command('xxw1DF5440')
       

        # Activate voltage pump for clear
        for i in range(11):
            reply = self.send_command('xxw0300169')
           

        reply = self.send_command('xxr01')
        

        # Activate voltage pump for store
        for i in range(11):
            reply = self.send_command('xxw03001E2')
            
            
        # Check diagnostics
        reply = self.send_command('xxr01')
        reply = self.send_command('xxw0300015')
        reply = self.send_command('vho0')
        reply = self.send_command('vho1')
        reply = self.send_command('ftvdl1')
        reply = self.send_command('xxr01')
        reply = self.send_command('xxr03')
       


    def isConnected(self):
        sensor_id = self.read_id()
        if (sensor_id == "0000 0000" or sensor_id == ''):
           return False
        else:
            return True
        
    def readNVRAM(self):
        reg = [0 for i in range(12)]
        for i in range(12):
            cmd = 'xxr0' + str(i)
            reg[i] = self.send_command(cmd)
        print(reg) 
        
    def returnBinaryNVRAM(self):
        reg = [0 for i in range(13)]
        binval = ''
        for i in range(13):
            cmd = 'xxr0%s'  % (str(i))
            if i == 10: 
                cmd = 'xxr0A'
            if i == 11: 
                cmd = 'xxr0B'   
            if i == 12: 
                cmd = 'xxr0C'  
            reg[i] = (self.send_command(cmd))
        for i in range(13):
            binval += (reg[i][2:7])
        binval = bin(int(binval, 16))[2:]
        return binval
        
    def returnRegister(self, reg):
        if reg < 10:
            reply = self.send_command('xxr02') 
        return reply[2:6]
if __name__ == '__main__':
    x = USBProgrammer('/dev/ttyUSB0')
    setup = x.read_setup()
    print(setup)
#    while(1):
#        (x.read_voltage_out())
    # print(x.read_magnetic())
#    print(x.read_firmware_version())
#    print(x.read_setup())
#    print(x.read_voltage_out())
#    print(x.read_version())
#    print(x.read_id())
#    setup = x.read_setup()
#    print(setup)
#    setup['mrange'] = 2
#    setup['tc'] = 10
#    setup['tcsq'] = -8
#    setup['alignment'] = True
#    setup['locked'] = False
#    setup['sensitivity'] = -30
 #    setup['offset'] = 0
#    x.write_setup(setup) 
#    print(x.read_setup())
#    setup['locked'] = False
#    setup['sensitivity'] = -64
#    setup['offset'] = -12
#    x.isConnected()
#    x.write_setup(setup)
    while(1):
         print(x.read_setup())
    print(x.read_voltage_out())
    print(x.isConnected())
    x.device.close()
    # print(str(x.read_magnetic()))
 