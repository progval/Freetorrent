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
import hashlib
from common.lib import parsers
from common import db
from common import html
from common import exceptions

testName = re.compile('^[a-zA-Z0-9_-]{2,36}$')
testEmail = re.compile('^[a-zA-Z0-9_.-]+@[a-zA-Z0-9_.-]{2,}\.[a-z]{2,}$')

def run(environ):
    status = '200 OK'
    headers = []
    responseBody = html.getHead(title=u'Créer un compte')
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
                    <td><label for="passwd1">Mot de passe :</label></td>
                    <td>
                        <input type="password" id="passwd1" name="passwd1" />
                    </td>
                </tr>
                <tr>
                    <td><label for="passwd2">
                        Mot de passe (confirmation) :
                    </label></td>
                    <td>
                        <input type="password" id="passwd2" name="passwd2" />
                    </td>
                </tr>
                <tr>
                    <td><label for="email">Adresse de courriel :</label></td>
                    <td><input type="text" id="email" name="email" /></td>
                </tr>
                <tr>
                    <td colspan="2">
                        <input type="submit" value="S'inscrire" />
                    </td>
                </tr>
            </table>
        </form>"""
    elif path == 'submit.htm':
        data = parsers.http_query(environ, 'POST')
        assert all((key in data) for key in
                   ('name', 'passwd1', 'passwd2', 'email'))
        cursor = db.conn.cursor()
        cursor.execute("SELECT name FROM users WHERE name=%s",
                       (data['name'],))
        row = cursor.fetchone()
        anyError = False
        if row is not None:
            responseBody += u"""<p>Il y a déjà un utilisateur ayant ce nom.
                               Veuillez en choisir un autre.</p>"""
            anyError = True
        if data['passwd1'] != data['passwd2']:
            responseBody += u"""<p>Le mot de passe et sa confirmation ne sont
                               pas identiques.</p>"""
            anyError = True
        if not testName.match(data['name']):
            responseBody += u"""<p>Le nom d'utilisateur est incorrect.
                               Taille : de 2 à 36, et ne peux contenir que
                               des caractères alphanumériques, des
                               underscores et des tirets.</p>"""
            anyError = True
        if not testEmail.match(data['email']):
            responseBody += u"""<p>L'adresse de courriel est invalide.</p>"""
            anyError = True

        if not anyError:
            ##DB#users
            cursor.execute("""INSERT INTO users VALUES
                            (NULL,%s,%s,%s,'','','')""", (
                            data['name'],
                            hashlib.sha1(data['passwd1']).hexdigest(),
                            data['email']))
            db.conn.commit()
            responseBody += u"""Votre compte a été créé."""
    else:
        raise exceptions.Error404()

    responseBody += html.getFoot()
    return status, headers, responseBody
