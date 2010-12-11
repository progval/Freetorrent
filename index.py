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

import os
import sys
directory = '/'.join(__file__.split('/')[0:-1])
sys.path.append(directory)

for package in ['common', 'torrent', 'forum', 'about', 'root']:
    reload(__import__(package))

from common import errors

def application(environ, start_response):
    status = '200 OK'
    try:
        status, headers, responseBody = dispatcher(environ)
    except Exception as e:
        status, headers, responseBody = errors.error500(environ, e)
    keys = []
    for header, value in headers:
        keys += [header]
    if not 'Content-Type' in keys:
        headers += [('Content-Type', 'text/html')]
    if not 'Content-Length' in keys:
        headers += [('Content-Length', str(len(responseBody)))]
    start_response(status, headers)
    return [responseBody]

def dispatcher(environ):
    path = environ['REDIRECT_URL']
    package = None
    if path.startswith('/forum/'):
        package = 'forum'
    elif path.startswith('/browse/'):
        package = 'torrent'
    elif path.startswith('/about/'):
        package = 'about'
    elif len(path.split('/')) == 2: # At URI root
        package = 'root'
    if package is None:
        status, headers, responseBody = errors.error404(environ)
    else:
        package = __import__(package + '.index')
        status, headers, responseBody = package.index.run(environ)
    return status, headers, responseBody
