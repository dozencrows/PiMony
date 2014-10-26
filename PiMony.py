#!/usr/bin/python
'''
PiMony -- Smart remote control prototype

This is the main module for PiMony, a prototype smart remote control program

@author:     Nicholas Tuckett

@copyright:  2014 Nicholas Tuckett. All rights reserved.

@license:    private

@contact:    pimony@magwitch.uk.net
@deffield    updated: Updated
'''

import sys
import os

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

from PyGameInterface import PyGameInterface

__all__ = []
__version__ = 0.1
__date__ = '2014-10-26'
__updated__ = '2014-10-26'

class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg

def main(argv=None): # IGNORE:C0111
    '''Command line options.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = '''%s

  Created by Nicholas Tuckett on %s.
  Copyright 2014 Nicholas Tuckett. All rights reserved.

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc, str(__date__))

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-d", "--debug", dest="debug", help="Specify debug mode: provide remote host name as value")

        # Process arguments
        args = parser.parse_args()
        
        if args.debug:
            sys.path.append(r'/home/pi/pysrc')
            import pydevd
            pydevd.settrace(args.debug)
            
        interface = PyGameInterface()
        interface.use_framebuffer()
        interface.run()
        
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
#    except Exception, e:
#        if DEBUG or TESTRUN:
#            raise(e)
#        indent = len(program_name) * " "
#        sys.stderr.write(program_name + ": " + repr(e) + "\n")
#        sys.stderr.write(indent + "  for help use --help")
#        return 2

if __name__ == "__main__":
    sys.exit(main())
