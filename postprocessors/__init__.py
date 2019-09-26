# Author: Izaak Neutelings (May 2019)
import os
modulepath = os.path.dirname(__file__)


def ensureDirectory(dirname):
    """Make directory if it does not exist."""
    if not os.path.exists(dirname):
      os.makedirs(dirname)
      print '>>> made directory "%s"'%(dirname)
      if not os.path.exists(dirname):
        print '>>> failed to make directory "%s"'%(dirname)
    return dirname
    
