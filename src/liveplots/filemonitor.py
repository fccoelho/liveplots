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
    def __init__(self,filepath,events,visaction,**kwargs):
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
        self.mask = self._get_mask(events)
        self.handler = _HandleEvents()
        if 'debug' in kwargs:
            self.handler.debug = kwargs['debug']
        self.handler.set_action(self.visaction)
        self.notifier = pyinotify.ThreadedNotifier(self.wm, self.handler)
        self.notifier.start()
        wdd = self.wm.add_watch(self.filepath, self.mask, rec=True)
        #self.wm.rm_watch(wdd.values())
        
    def _get_mask(self, events):
        '''
        Returns the mask for the notifier
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
    
    def stop(self):
        self.notifier.stop()
                
        
        
class _HandleEvents(pyinotify.ProcessEvent):
    debug = 0
    def set_action(self,action):
        self.action = action
        
    def process_IN_CREATE(self, event):
        if self.debug:
            print "Creating:", event.pathname
        self.action(event.pathname)

    def process_IN_DELETE(self, event):
        if self.debug:
            print "Removing:", event.pathname
        self.action(event.pathname)
        
    def process_IN_ACCESS(self,event):
        if self.debug:
            print "Accessing:", event.pathname
        self.action(event.pathname)
        
    def process_IN_ATTRIB(self,event):
        if self.debug:
            print "Changing metadata:", event.pathname
        self.action(event.pathname)
        
    def process_IN_MODIFY(self,event):
        if self.debug:
            print "Modifying:", event.pathname
        self.action(event.pathname)
        
    def process_IN_CLOSE_WRITE(self,event):
        if self.debug:
            print "Closing writable file:", event.pathname
        self.action(event.pathname)
        
    def process_IN_CLOSE_NOWRITE(self,event):
        if self.debug:
            print "Closing read-only file:", event.pathname
        self.action(event.pathname)