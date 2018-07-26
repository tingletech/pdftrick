#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
[github](https://github.com/tingletech/pdftrick) [pypi](https://pypi.python.org/pypi/pdftrick)

One weird PDF trick
===================

I have some really large PDF files of manuscript materials with
OCR.  10,000 pages worth and I don't have enough room for them.
They are in the 50M to 500M range per file.  And they need to be up
this week for a grant deadline.  So I'm looking around the google
for some way to shrink the pdf files.  I came across this:
[askubuntu](http://askubuntu.com/a/243753)

    pdf2ps input.pdf output.ps
    ps2pdf output.ps output.pdf

Okay, about 8× compression!  Great, convert to postscript and back.
The project manager asks "is the OCR still good?"  I rip the text.
a n d  i t  h as a l l  t h i s  w e i r d spaces in it.

Long and the short of it: I found that if I use `pdftops` from
[Poppler](http://poppler.freedesktop.org) to create the postscript
file but use `ps2pdf` from [Ghostscript](http://www.ghostscript.com)
to create the new PDF file; I still get 8× compression, and the OCR
looks the same as before[^footnote].  I guess poppler is better at writing
postscript, and that ghostscript is better at writting PDF.

This script automates the process of running poppler and then
ghostscript on a PDF to get this magic.

[^footnote]: as I check more files in the batch, I'm finding that
for some this process does introduce extra spaces between letters
as well; however, it seems to be to a lesser degree than doing both
steps with ghostscript.


"""

from __future__ import division
import sys
import argparse
import tempfile
import subprocess
import os
import shutil
import contextlib
import shlex


def main(argv=None):
    """

    First argument is the PDF file you want to shrink.

    Second argument is optional.

    If one argement is given, the large file is replaced with a new
    smaller file if the compression ratio is greater than 1.2.

    If two arguments are given, the second argument is the path
    to put the output file.

    """

    parser = argparse.ArgumentParser(description="one weird PDF trick")
    parser.add_argument(
        'before', nargs=1, help="PDF (before)", type=extant_file)
    parser.add_argument('after', nargs="?", help="PDF (after)")
    parser.add_argument(
        '-t', '--tempdir', help="needs a lot of temp space", required=False)
    parser.add_argument(
        '--pdftops_opts', help="options for pdftops command", required=False)
    parser.add_argument(
        '--ps2pdf_opts', help="options for ps2pdf command", required=False)
    """
        usage: pdftrick [-h] [-t TEMPDIR] before [after]

        one weird PDF trick

        positional arguments:
          before                PDF (before)
          after                 PDF (after)

        optional arguments:
          -h, --help            show this help message and exit
          -t TEMPDIR, --tempdir TEMPDIR
                                needs a lot of temp space
    """
    # * TODO argument: compression ratio cutoff
    # * TODO argument: logging
    if argv is None:
        argv = parser.parse_args()

    if argv.tempdir:
        tempfile.tempdir = argv.tempdir

    # check that we have the tools we are wrapping
    if not which('pdftops'):  # use poppler to create a .ps
        raise Exception("need pdftops from poppler")
    if not which('ps2pdf'):  # and use ghostscript to create a .pdf
        raise Exception("need ps2pdf from ghostscript")

    with make_temp_directory(prefix='popgho') as tempdir:
        main_with_temp(tempdir, argv)


def main_with_temp(tempdir, argv):
    os.environ.update({'TMPDIR': tempdir})  # for ghostscript
    postscript = os.path.join(tempdir, 'poppler.ps')
    o_pdf = argv.before[0]
    n_pdf = os.path.join(tempdir, 'ghost.pdf')
    pdftops_opts = []
    ps2pdf_opts = []
    if argv.ps2pdf_opts is not None:
        ps2pdf_opts = shlex.split(argv.ps2pdf_opts)
    if argv.pdftops_opts is not None:
        pdftops_opts = shlex.split(argv.pdftops_opts)

    # swallow all stderr and stdout [stackoverflow](http://stackoverflow.com/a/12503246/1763984)
    with open(os.devnull, "w") as f:
        subprocess.check_call(
            ['pdftops'] + pdftops_opts + [o_pdf, postscript],
            stdout=f,
            stderr=f)
        subprocess.check_call(
            ['ps2pdf'] + ps2pdf_opts + [postscript, n_pdf],
            stdout=f,
            stderr=f,
            env=os.environ)

    o_size = os.path.getsize(o_pdf)
    n_size = os.path.getsize(n_pdf)
    compression_ratio = o_size / n_size

    if (argv.after):
        shutil.move(n_pdf, argv.after)
        print("compression: {1}; created: {0}".format(argv.after,
                                                      compression_ratio))
    elif (compression_ratio > 1.2):
        shutil.move(n_pdf, o_pdf)
        print("compression: {1}; overwrite: {0}".format(
            o_pdf, compression_ratio))
    else:
        os.remove(n_pdf)
        print("compression: {0}; not worth it, deleted new file"
              .format(compression_ratio))
    os.remove(postscript)


def which(program):
    """like the unix `which` command 
    [stackoverflow](http://stackoverflow.com/a/377028/1763984)
    """

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


def extant_file(x):
    """`Type` for argparse - checks that file exists but does not open. 
    [stackoverflow](http://stackoverflow.com/a/11541495/1763984)
    """
    if not os.path.exists(x):
        raise argparse.ArgumentError("{0} does not exist".format(x))
    return x


@contextlib.contextmanager
def make_temp_directory(prefix):
    """way to clean up a temporary folder
    [stackoverflow](http://stackoverflow.com/a/13379969/1763984)
    """
    temp_dir = tempfile.mkdtemp(prefix=prefix)
    yield temp_dir
    shutil.rmtree(temp_dir)


# main() idiom for importing into REPL for debugging
if __name__ == "__main__":
    sys.exit(main())
"""
Copyright © 2018, Regents of the University of California
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
