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

import hashlib
from common import db
from common import html
from common import user
from common import exceptions
from common.lib import parsers
from common.lib.pesto import cookie

def run(environ):
    status = '200 OK'
    headers = []
    responseBody = html.getHead(title='Se connecter')
    path = environ['module_path']
    if path == '':
        responseBody += u"""
        <form action="submit.htm" method="POST">
            <table>
                <tr>
                    <td><label for="name">Nom :</label></td>
                    <td><input type="text" id="name" name="name" /></td>
                </tr>
                <tr>
                    <td><label for="passwd">Mot de passe :</label></td>
                    <td>
                        <input type="password" id="passwd" name="passwd" />
                    </td>
                </tr>
                <tr>
                    <td colspan="2">
                        <input type="submit" value="Se connecter" />
                    </td>
                </tr>
            </table>
        </form>"""
    elif path == 'submit.htm':
        data = parsers.http_query(environ, 'POST')
        assert all((key in data) for key in ('name', 'passwd'))
        currentUser = user.User(data['name'],
                                hashlib.sha1(data['passwd']).hexdigest())
        def getCookie(name, value):
            return cookie.Cookie(name=name,
                                 value=value,
                                 expires=2592000,
                                 path='/')
        nameCookie = getCookie('name', currentUser.name)
        passwdCookie = getCookie('passwdhash', currentUser.passwdhash)
        headers.append(('Set-Cookie', str(nameCookie)))
        headers.append(('Set-Cookie', str(passwdCookie)))
        headers.append(('Location', '/'))
        status = '302 Found'
        responseBody += 'Bienvenue %s !' % str(nameCookie.value)
    else:
        raise exceptions.Error404()
    responseBody += html.getFoot()
    return status, headers, responseBody
