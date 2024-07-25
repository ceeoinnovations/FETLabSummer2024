from pyscript import window
import asyncio
import andrea_terminal 

code ='''
import os
def cksm(file):
    s = os.stat(file)[6]
    f = open(file,'rb')
    msg = f.read()
    f.close()
    v = 21
    for c in msg.decode():
        v ^= ord(c)
    return s,v
'''

class Ampy(andrea_terminal.Terminal):
    def __init__(self, buffer_size = 256, status = None, baudrate = 115200, update_progress_callback = None):
        super().__init__(baudrate)
        self.buffer_size = buffer_size
        self.status = status
        self.update_progress_callback = update_progress_callback
        self.update(0)
        self.path = None

    def update(self, value):
        if self.status: self.status.value = value
        # update the progress bar percent
        if self.update_progress_callback: self.update_progress_callback(value)



    # def update_progress(self, value):
    #     if self.update_progress_callback:
    #         self.update_progress_callback(value)

    async def go_raw(self):
        await self.eval('\r\x01',True)
        await self.eval('\x04',True)
        print('rebooted')

    async def close_raw(self):
        await self.eval('\r\x02',True) # ctrl-B: enter friendly REPL
        
    async def send_code(self, filename, data):
        await self.eval("f = open('%s', 'wb')"%(filename),True)
        size = len(data)
        for i in range(0, size, self.buffer_size):
            chunk_size = min(self.buffer_size, size - i)
            chunk = repr(data[i : i + chunk_size])
            reply = await self.eval("f.write(%s)"%(chunk),True) 
            await asyncio.sleep(0.01)
            await self.eval('\x04',True)
            print(reply)
            self.update(10 + 90*(i+1)/size)
        await self.eval("f.close()",True)
        await self.eval('\x04',True)
        
    def checksum(self, msg):
        v = 21
        for c in msg.decode():
            v ^= ord(c)
        return v

    async def download(self, filename, data, check = True):
        file_size = len(data.encode()) 
        cs = self.checksum(data.encode())
        
        await self.eval('\r\x03',True)
        await asyncio.sleep(0.1)
        await self.eval(f'# switching to raw mode and downloading {filename}\r\n')
        self.eval('\x03',True)
        await asyncio.sleep(0.1)
        await self.go_raw()
        self.update(10)
        await self.send_code(filename, data) 
        reply = await self.eval('\x04',True)
        print(reply)
        await self.eval(code,True)
        await self.eval('\x04',True)
        await self.close_raw()
        self.update(100)

        if check:
            await self.eval('\r\n# checking filesize and checksum\r\n')
            reply = await self.eval(f"({file_size},{cs}) == cksm('{filename}')\r\n")
            await asyncio.sleep(0.5)
            print(reply)
            try:
                success = self.buffer.split('\n')[1]
            except:
                return False
            return success
        return True

  