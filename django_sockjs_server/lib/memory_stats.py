
class MemoryStats(object):
    _proc_status = '/proc/self/status'

    _scale = {'kB': 1024.0, 'mB': 1024.0*1024.0,
              'KB': 1024.0, 'MB': 1024.0*1024.0}

    def _VmB(self, VmKey):
        '''Private.
        '''
        # get pseudo file  /proc/<pid>/status
        try:
            t = open(self._proc_status)
            v = t.read()
            t.close()
        except:
            return 0.0  # non-Linux?
            # get VmKey line e.g. 'VmRSS:  9999  kB\n ...'
        i = v.index(VmKey)
        v = v[i:].split(None, 3)  # whitespace
        if len(v) < 3:
            return 0.0  # invalid format?
            # convert Vm value to bytes
        return float(v[1]) * self._scale[v[2]]


    def memory(self, since=0.0):
        '''Return memory usage in bytes.
        '''
        return self._VmB('VmSize:') - since

    def resident(self, since=0.0):
        '''Return resident memory usage in bytes.
        '''
        return self._VmB('VmRSS:') - since

    def stacksize(self, since=0.0):
        '''Return stack size in bytes.
        '''
        return self._VmB('VmStk:') - since
