'''
Created on 15/04/2010

@author: fccoelho
'''
import sys
try:
    import pyinotify
except:
    raise TypeError('Filemonitor cannot cannot be used on %s platform'%sys.platform)

class Monitor(object):
    '''
    Monitors a file for changes and triggers a visualization action
    '''
    ValidEvents ={'create':pyinotify.IN_CREATE,
                  'delete':pyinotify.IN_DELETE,
                  'close_write':pyinotify.IN_CLOSE_WRITE,
                  "close_nowrite":pyinotify.IN_CLOSE_NOWRITE,
                  'access':pyinotify.IN_ACCESS,
                  'attrib':pyinotify.IN_ATTRIB,
                  'modify':pyinotify.IN_MODIFY}
    def __init__(self,filepath,events,visaction):
        '''
        Sets up monitoring of a file 
        
        :Parameters:
            - `filepath`: full path of the file to monitor
            - `event`: events to monitor: list of strings
            - `visaction`: Callable which will perform the action which takes filepath as argument
        '''
        self.filepath = filepath
        self.events = events
        self.visaction = visaction
        # Setting up the watch manager
        self.wm = pyinotify.WatchManager()
        mask = self._get_mask(events)
        handler = _HandleEvents()
        handler.set_action(self.visaction)
        notifier = pyinotify.ThreadedNotifier(self.wm, handler)
        notifier.start()
        wdd = self.wm.add_watch(self.filepath, mask, rec=True)
        self.wm.rm_watch(wdd.values())
        
    def _get_mask(self, events):
        '''
        returns the mask for the notifier
        '''
        try:
            codes = [self.ValidEvents[e] for e in events]
        except KeyError:
            raise KeyError('%s is not a valid event'%e)
        if len(codes) > 1:
            mask = codes[0]
            for c in codes[1:]:
                mask = mask | c
        else:
            mask = codes[0]
        return mask
                
        
        
class _HandleEvents(pyinotify.ProcessEvent):
    
    def set_action(self,action):
        self.action = action
        
    def process_IN_CREATE(self, event):
        print "Creating:", event.pathname

    def process_IN_DELETE(self, event):
        print "Removing:", event.pathname
        
    def process_IN_ACCESS(self,event):
        print "Accessing:", event.pathname
        
    def process_IN_ATTRIB(self,event):
        print "Changing metadata:", event.pathname
        
    def process_IN_MODIFY(self,event):
        print "Modifying:", event.pathname
        
    def process_IN_CLOSE_WRITE(self,event):
        print "Closing writable file:", event.pathname
        
    def process_IN_CLOSE_NOWRITE(self,event):
        print "Closing read-only file:", event.pathname