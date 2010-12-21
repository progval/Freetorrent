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
import cgi
from common import db
from common import html
from common import cache
from common import exceptions

searchMatch = re.compile('^search-(?P<from>[0-9]+)-(?P<count>[0-9]+).htm(?P<args>.*)$')

usersListTemplate = u"""
<table class="users_list">
    <tr>
        <th>ID</th>
        <th>Nom</th>
        <th>Messages</th>
    </tr>
    %s
</table>"""
usersListRowTemplate = u"""
<tr>
    <td class="id">
        %(id)s
    </td>
    <td class="username">
        <a href="%(name)s/">%(name)s</a>
    </td>
    <td class="messages">
        %(messages)s
    </td>
</tr>
"""

userProfileTemplate = u"""
<table>
    <tr>
        <td>%(name)s</td>
        <td rowspan="3">
            <img src="%(avatar)s" alt="Pas d'avatar défini" />
        </td>
    </tr>
    <tr>
        <td><a href="mailto:%(email)s">%(email)s</a></td>
    </tr>
    <tr>
        <td>A posté %(messages)s messages.</td>
    </tr>
</table>"""

def run(environ):
    status = '200 OK'
    headers = []
    path = environ['module_path']
    if path == '':
        status = '302 Found'
        headers.append(('Location', 'search-0-50.htm'))
        responseBody = html.getHead(title='Redirection')
        responseBody += u"""<p>Si vous voyez cette page, c'est que votre
                navigateur ne supporte pas les redirections. Veuillez cliquer
                sur <a href="list-1-50.htm">ce lien</a> pour voir la liste des
                utilisateurs.</p>"""
        responseBody += html.getFoot()
        return status, headers, responseBody
    parsed = searchMatch.match(path)
    if parsed is not None:
        args = {}
        if parsed.group('args') != '':
            assert parsed.group('args')[0] == '?'
            args = cgi.parse_qsl(parsed.group('args'))
        sqlQuery = "SELECT u_id, name FROM users WHERE u_id!=0 "
        sqlArgs = tuple()
        if args.has_key('orderby'):
            orderby == args['orderby']
            assert orderby in ('u_id', 'name')
            sqlQuery += "ORDER BY %s " % orderby
            if args.has_key('desc'):
                sqlQuery += "DESC "
        sqlQuery += "LIMIT %i, %i" % (int(parsed.group('from')), int(parsed.group('count')))
        users = db.conn.cursor()
        users.execute(sqlQuery, sqlArgs)
        rows = ''
        for user in users:
            cursor = db.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM messages WHERE u_id=%s" % (user[0],))
            messages = cursor.fetchone()[0]
            rows += usersListRowTemplate % {'id': user[0],
                                            'name': user[1],
                                            'messages': messages}
        responseBody = html.getHead(title=u"Recherche d'utilisateurs")
        responseBody += usersListTemplate % rows
        responseBody += html.getFoot()
        return status, headers, responseBody
    else:
        username = path.split('/')[0]
        user = db.conn.cursor()
        user.execute("SELECT u_id, email, avatar FROM users WHERE name=%s",
                     (username,))
        if user.rowcount == 0:
            raise exceptions.Error404()
        assert user.rowcount == 1
        user = user.fetchone()
        responseBody = html.getHead(title=u"%s (membre)" % username)
        cached = cache.getUserCache(user[0])
        responseBody += userProfileTemplate % {'name': username,
                                              'u_id': user[0],
                                              'email': user[1].replace('@', '(4R0B4S3)'),
                                              'avatar': user[2],
                                              'messages': cached['messages']}
        responseBody += html.getFoot()
        return status, headers, responseBody

    raise exceptions.Error404()
