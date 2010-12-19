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

import re
from common import db
from common import html
from common import render as commonRender
from common import exceptions
from torrents import render

detailsMatch = re.compile('^%s-(?P<t_id>[a-f0-9]+)/$' %
                          commonRender.urlAvailableChars)

def run(environ):
    status = '200 OK'
    headers = []
    path = environ['module_path']
    if path == '':
        responseBody = html.getHead(title='Catalogue des torrents')
        responseBody += render.fullList("""
                ORDER BY submit_time DESC
                LIMIT 0, 10""")
        responseBody += html.getFoot()
        return status, headers, responseBody
    parsed = detailsMatch.match(path)
    if parsed is not None:
        t_id = parsed.group('t_id')
        torrent = db.conn.cursor()
        torrent.execute("SELECT name FROM torrents WHERE t_id=%s", (t_id,))
        if torrent.rowcount == 0:
            raise exceptions.Error404()
        assert torrent.rowcount == 1
        torrent = torrent.fetchone()
        responseBody = html.getHead(title='%s (torrent)' % torrent[0])
        responseBody += render.details(t_id)
        reponseBody += html.getFoot()
        return status, headers, responseBody

    raise exceptions.Error404()
