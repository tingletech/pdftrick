#!/usr/bin/env python
# -*- coding: utf8 -*-


from __future__ import division
import sys
import argparse
import subprocess
import os
import re
from pprint import pprint as pp


def main(argv=None):
    """
    """

    parser = argparse.ArgumentParser(description="pdf density")
    parser.add_argument('pdf', nargs="+", help="PDF",
                        type=extant_file)

    if argv is None:
        argv = parser.parse_args()

    for path in argv.pdf:
        stat_pdf(path)


# target platform had 2.6
# http://stackoverflow.com/questions/17539985/check-output-error-in-python
def check_output(*popenargs, **kwargs):
    process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
    output, unused_err = process.communicate()
    retcode = process.poll()
    if retcode:
        cmd = kwargs.get("args")
        if cmd is None:
            cmd = popenargs[0]
        error = subprocess.CalledProcessError(retcode, cmd)
        error.output = output
        raise error
    return output


def stat_pdf(path):
    try:
        subprocess.check_output
    except:
        subprocess.check_output = check_output
    output = subprocess.check_output(['pdfinfo', path])
    pages = int(re.search('Pages:\s*(\d*)', output).group(1))
    byts = float(re.search('File size:\s*(\d*)\sbytes', output).group(1))
    mb = 1<<20
    megs = byts / mb
    out = path
    out = out + '\t%.2f MB' % round(megs,2)
    out = out + '\t{0} pages'.format(pages)
    out = out + '\t%.2f pages per MB' % round(pages/megs, 2)
    out = out + '\t%.2f MB per page' % round(megs/pages, 2)
    print out


def extant_file(x):
    """`Type` for argparse - checks that file exists but does not open. 
    [stackoverflow](http://stackoverflow.com/a/11541495/1763984)
    """
    if not os.path.exists(x):
        raise argparse.ArgumentError("{0} does not exist".format(x))
    return x


# main() idiom for importing into REPL for debugging
if __name__ == "__main__":
    sys.exit(main())

"""
Copyright © 2014, Regents of the University of California
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

- Redistributions of source code must retain the above copyright notice,
  this list of conditions and the following disclaimer.
- Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.
- Neither the name of the University of California nor the names of its
  contributors may be used to endorse or promote products derived from this
  software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
"""
