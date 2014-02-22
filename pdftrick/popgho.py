#!/usr/bin/env python
# -*- coding: utf8 -*-
from __future__ import division
import sys
import argparse
import tempfile
import subprocess
import os
import shutil
from StringIO import StringIO
from pprint import pprint as pp


# http://stackoverflow.com/a/11541495/1763984
def extant_file(x):
    """'Type' for argparse - checks that file exists but does not open. """
    if not os.path.exists(x):
        raise argparse.ArgumentError("{0} does not exist".format(x))
    return x

def main(argv=None):

    parser = argparse.ArgumentParser(description="one weird PDF trick")
    parser.add_argument('before', nargs=1, help="PDF (before)", type=extant_file)
    parser.add_argument('after', nargs="?", help="PDF (after)")
    # TODO argument: compression ratio cutoff
    # TODO argument: logging
    if argv is None:
        argv = parser.parse_args()

    if not which('pdftops'):   # use poppler to create a .ps
        raise error("need pdftops from poppler")
    if not which('ps2pdf'):    # and use ghostscript to create a .pdf
        raise error("need ps2pdf from ghostscript")

    postscript = tempfile.mkstemp(suffix='.ps', prefix='popgho')[1]
    o_pdf = argv.before[0]
    n_pdf = "".join([o_pdf,'.new.pdf'])

    # swallow all stderr and stdout
    with open(os.devnull, "w") as f:
        subprocess.check_call(['pdftops', o_pdf, postscript],
                              stdout=f, stderr=f)
        subprocess.check_call(['ps2pdf', postscript, n_pdf],
                              stdout=f, stderr=f)

    o_size = os.path.getsize(o_pdf)
    n_size = os.path.getsize(n_pdf)
    compression_ratio = o_size/n_size

    if (argv.after):
        shutil.move(n_pdf, argv.after)
        print "compression: {1}; created: {0}".format(argv.after, compression_ratio)
    elif (compression_ratio > 1.2):
        shutil.move(n_pdf, o_pdf)
        print "compression: {1}; overwrite: {0}".format(o_pdf, compression_ratio)
    else:
        os.remove(postscript)
        print "compression: {0}; not worth it, deleted new file".format(compression_ratio)

# http://stackoverflow.com/a/377028/1763984
def which(program):
    import os
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None

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
