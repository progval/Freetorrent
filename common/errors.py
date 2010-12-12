# -*- coding: utf8 -*-

# Copyright (c) 2010, Valentin Lorentz
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the University of California, Berkeley nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE REGENTS AND CONTRIBUTORS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import sys
import traceback
from common import html
from cStringIO import StringIO

def error404(environ):
    status = '404 Not Found'
    headers = []
    responseBody = '<h1>Not Found</h1>'
    head, foot = '', ''
    try:
        head, foot = (html.getHead(title='Erreur 404'), html.getFoot())
    except:
        pass
    return  status, headers, head + responseBody + foot

def error500(environ, e):
    status = '500 Internal Server Error'
    headers = []
    responseBody = '<h1>Internal Error</h1>'
    responseBody += '<h2>%s</h2>' % e.__class__.__name__
    exceptionTraceback = StringIO()
    traceback.print_exc(file=exceptionTraceback)
    exceptionTraceback.seek(0)
    responseBody += '<pre>%s</pre>' % exceptionTraceback.read()
    head, foot = '', ''
    try:
        head, foot = html.getHead(title='Erreur 500'), html.getFoot()
    except:
        pass
    return  status, headers, head + responseBody + foot
