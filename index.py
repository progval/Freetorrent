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
os.chdir(directory)

from common import errors
from common.lib.pesto import cookie as cookielib
from common import user

DEBUG = True

def application(environ, start_response):
    if DEBUG:
        from cStringIO import StringIO
        sys.stdout = StringIO()
        sys.stderr = StringIO()
    status = '200 OK'
    if environ.has_key('HTTP_COOKIE'):
        cookies = cookielib.parse_cookie_header(environ['HTTP_COOKIE'])
    else:
        cookies = []
    environ.update({'cookies': {}})
    for cookie in cookies:
        environ['cookies'].update({cookie.name: cookie})
    environ.update({'user': user.getUserFromCookies(environ['cookies'])})
    try:
        status, headers, responseBody = dispatcher(environ)
    except Exception as e:
        status, headers, responseBody = errors.error500(environ, e)
    if DEBUG:
        sys.stdout.seek(0)
        sys.stderr.seek(0)
        responseBody += sys.stdout.read() + sys.stderr.read()
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
    module = None
    status = None
    if path.startswith('/forum/'):
        module = 'forum.index'
    elif path.startswith('/torrents/'):
        module = 'torrents.browse'
    elif path.startswith('/upload/'):
        module = 'torrents.upload'
    elif path.startswith('/about/'):
        module = 'about.index'
    elif path.startswith('/disconnect/'):
        module = 'user.disconnect'
    elif path.startswith('/connect/'):
        module = 'user.connect'
    elif path.startswith('/register/'):
        module = 'user.register'
    elif path.startswith('/user/'):
        module = 'user.index'
    elif path == '/':
        module = 'root.index'
    if module is None:
        status, headers, responseBody = errors.error404(environ)
    else:
        module = __import__(module)
        status, headers, responseBody = module.index.run(environ)
    return status, headers, responseBody
