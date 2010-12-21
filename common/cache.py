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

import time
import sqlite3
from common import db

CACHE_LIFETIME = 60*60*4

conn = sqlite3.connect(':memory:')

cursor = conn.cursor()
cursor.execute("""
        CREATE TABLE users (
            u_id INTEGER,
            last_calc INTEGER,
            messages INTEGER,
            upload FLOAT,
            download FLOAT
        );""")
cursor.execute("""SELECT * FROM users WHERE u_id=0""")
userColumns = [item[0] for item in cursor.description]
cursor.close()

def generateUserCache(u_id):
    cursor = db.conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM messages WHERE u_id=%s", (u_id,))
    messages = cursor.fetchone()[0]
    upload = 0 #FIXME
    download = 0 #FIXME
    cacheCursor = conn.cursor()
    cacheCursor.execute("DELETE FROM users WHERE u_id=?", (u_id,))
    row = (u_id, time.time(), messages, upload, download)
    cacheCursor.execute("INSERT INTO users VALUES (?,?,?,?,?)", row)
    return row

def getUserCache(u_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE u_id=?", (u_id,))
    row = cursor.fetchone()
    if row is None:
        row = generateUserCache(u_id)
    else:
        if int(row[1]) < time.time() - CACHE_LIFETIME:
            row = generateUserCache(u_id)
    output = {}
    for column, value in zip(userColumns, list(row)):
        output.update({column: value})
    return output
