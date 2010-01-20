# -*- coding: utf-8 -*-
#############################################################################
# File          : AbstractCheck.py
# Package       : rpmlint
# Author        : Frederic Lepied
# Created on    : Tue Sep 28 00:22:38 1999
# Version       : $Id$
# Purpose       : Abstract class to hold all the derived classes.
#############################################################################

import re
import socket
import urllib2

from Filter import addDetails, printInfo, printWarning
import Config

# Note: do not add any capturing parentheses here
macro_regex = re.compile('%+[{(]?\w+[)}]?')

class _HeadRequest(urllib2.Request):
    def get_method(self):
        return "HEAD"

class AbstractCheck:
    known_checks = {}

    def __init__(self, name):
        if not AbstractCheck.known_checks.get(name):
            AbstractCheck.known_checks[name] = self
        self.name = name
        self.verbose = False
        self.network_enabled = Config.getOption("NetworkEnabled", False)
        self.network_timeout = Config.getOption("NetworkTimeout", 10)

    def check(self, pkg):
        raise NotImplementedError('check must be implemented in subclass')

    def check_url(self, pkg, tag, url):
        """Check that URL points to something that seems to exist."""
        if self.verbose:
            if self.network_enabled:
                printInfo(pkg, 'checking-url', url,
                          '(timeout %s seconds)' % self.network_timeout)
            else:
                printInfo(pkg, 'network-checks-disabled', url)
                return
        # Could use timeout kwarg to urlopen, but that's python >= 2.6 only
        socket.setdefaulttimeout(self.network_timeout)
        res = err = None
        try:
            res = urllib2.urlopen(_HeadRequest(url))
        except Exception, e:
            printWarning(pkg, 'invalid-url', '%s:' % tag, url, e)
        res and res.close()

class AbstractFilesCheck(AbstractCheck):
    def __init__(self, name, file_regexp):
        self.__files_re = re.compile(file_regexp)
        AbstractCheck.__init__(self, name)
    def check(self, pkg):
        if pkg.isSource():
            return
        for filename in pkg.files():
            if self.__files_re.match(filename):
                self.check_file(pkg, filename)


    def check_file(self, pkg, filename):
        """Virtual method called for each file that match the regexp passed
        to the constructor.
        """
        raise NotImplementedError('check must be implemented in subclass')

addDetails(
'invalid-url',
'''The value should be a valid, public HTTP, HTTPS, or FTP URL.''',

'network-checks-disabled',
'''Checks requiring network access have not been enabled in configuration,
see the NetworkEnabled option.''',
)

# AbstractCheck.py ends here

# Local variables:
# indent-tabs-mode: nil
# py-indent-offset: 4
# End:
# ex: ts=4 sw=4 et
