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
from common import db
from common.lib.pesto import cookie

testName = re.compile('^[a-zA-Z0-9_-]{2,36}$')
testPasswdhash = re.compile('^[a-f0-9]*$')

def getUserFromCookies(cookies):
    global currentUser
    if not cookies.has_key('name') or not cookies.has_key('passwdhash'):
        user = User()
    else:
        user = User(cookies['name'].value, cookies['passwdhash'].value)
    currentUser = user
    return user

users = {}
def User(name='anonyme', passwdhash=''):
    global users
    #DEBUG
    return _User(name, passwdhash)
    if not users.has_key(name):
        users.update({name: _User(name, passwdhash)})
    return users[name]
class _User:
    def __init__(self, name, passwdhash):
        global currentUser
        self.__class__.__name__ = 'User'
        cursor = db.conn.cursor()
        assert testName.match(name)
        assert testPasswdhash.match(passwdhash)
        if passwdhash != '':
            ##DB#users
            cursor.execute("""SELECT name, passwdhash FROM users
                           WHERE name=%s AND passwdhash=%s;""",
                           (name, passwdhash))
        else:
            cursor.execute("""SELECT name, passwdhash FROM users
                           WHERE name=%s;""", (name,))

        row = cursor.fetchone()
        if row is None:
            self.name = 'anonyme'
            self.passwdhash = ''
        else:
            self.name, self.passwdhash = row
