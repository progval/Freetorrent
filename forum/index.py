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
from common import user
from common import exceptions
from unidecode import unidecode

availableChars = '[a-zA-Z0-9_-]+'
forumMatch = re.compile('^%s-(?P<f_id>[0-9]+)/$' % availableChars)
topicMatch = re.compile('^%s/-(?P<f_id>[0-9]+)%s/-(?P<t_id>[0-9]+)$' % \
                        (availableChars, availableChars))

forumsListTemplate = u"""<table class="forumslist">
    <tr>
        <th>Nouveaux messages</th>
        <th>Nom & description</th>
        <th>Sujets/messages</th>
        <th>Dernier message</th>
    </th>
    %s
</table>"""
forumRowTemplate = u"""<tr>
    <td class="%(newmsg_prefix)snewmsg">%(newmsg)s</td>
    <td class="name">
        <a href="%(url)s">%(forum_name)s</a><br />%(forum_desc)s
    </td>
    <td class="counts">%(topics)s/%(posts)s</td>
    <td class="lastmessage">%(lastmessage)s</td>
</tr>"""
lastMessageTemplate = u"""<a href="%(url)s#msg%(msg_id)s">
    %(topic_name)s par %(user_name)
</a>"""

def addForumPrefix(function):
    def decorate(*args, **kwargs):
        return '/forum' + function(*args, **kwargs)
    return decorate

@addForumPrefix
def getTopicUrl(t_id):
    cursor = db.conn.cursor()
    cursor.execute("""SELECT forums.name, topics.title, f_id, t_id
            FROM topics, forums
            WHERE topics.f_id=forums.f_id and t_id=%s""", (t_id,))
    assert cursor.rowcount <= 1
    if cursor.rowcount == 0:
        return '/forums/'
    else:
        row = cursor.fetchone()
        return '/%s-%i/%s-%i' % (unidecode(row[0]).replace(' ', '_'),
                                 row[2],
                                 unidecode(row[1]).replace(' ', '_'),
                                 row[3])

@addForumPrefix
def getForumUrl(f_id):
    cursor = db.conn.cursor()
    cursor.execute("SELECT forums.name, f_id FROM forums WHERE f_id=%s",
                   (f_id,))
    assert cursor.rowcount <= 1
    if cursor.rowcount == 0:
        return '/forums/'
    else:
        row = cursor.fetchone()
        return '/%s-%i/' % (unidecode(row[0]).replace(' ', '_'),
                            row[1])

def getForumTopicsCount(f_id):
    cursor = db.conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM topics WHERE f_id=%s", (f_id,))
    assert cursor.rowcount == 1
    return cursor.fetchone()[0]

def getForumPostsCount(f_id):
    cursor = db.conn.cursor()
    cursor.execute("""SELECT COUNT(*) FROM messages
            INNER JOIN topics USING (t_id)
            WHERE f_id=%s""", (f_id,))
    assert cursor.rowcount == 1
    return cursor.fetchone()[0]

def getTopicPostsCount(t_id):
    cursor = db.conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM messages WHERE t_id=%s", (t_id,))
    assert cursor.rowcount == 1
    return cursor.fetchone()[0]

def run(environ):
    status = '200 OK'
    headers = []
    path = environ['module_path']
    if path == '':
        forums = db.conn.cursor()
        forums.execute("SELECT f_id, name, description FROM forums;")
        responseBody = html.getHead(title='Liste des forums')
        forumRows = ''
        for forum in forums:
            lastMessage = db.conn.cursor()
            lastMessage.execute("""SELECT messages.m_id, topics.t_id,
                        topics.title, users.name
                    FROM messages, topics, users
                    WHERE f_id=%s
                        AND topics.t_id=messages.t_id
                        AND users.u_id=messages.u_id
                    ORDER BY messages.time
                    LIMIT 0,1;""", (forum[0],))
            lastMessage = lastMessage.fetchone()
            if lastMessage is None:
                lastMessage = 'aucun'
            else:
                lastMessage = lastMessageTemplate % \
                        {'url': getTopicUrl(lastMessage[1]),
                        'msg_id': lastMessage[0],
                        'topic_name': lastMessage[2],
                        'user_name': lastMessage[3]}
            notRead = db.conn.cursor()
            notRead.execute("""SELECT COUNT(*) FROM last_read
                    INNER JOIN topics USING (t_id)
                    INNER JOIN messages USING (t_id)
                    WHERE f_id=%s AND last_read.time<messages.time
                        AND last_read.u_id=%s""",
                             (forum[0], user.currentUser.id))
            notRead = notRead.fetchone()[0]
            if notRead == 0:
                prefix = 'no'
            else:
                prefix = ''
            forumRow = forumRowTemplate % \
                    {'newmsg_prefix': prefix,
                    'newmsg': notRead,
                    'url': getForumUrl(forum[0]),
                    'forum_name': forum[1],
                    'forum_desc': forum[2],
                    'topics': getForumTopicsCount(forum[0]),
                    'posts': getForumPostsCount(forum[0]),
                    'lastmessage': lastMessage}
            forumRows += forumRow
        responseBody += forumsListTemplate % forumRows
        responseBody += html.getFoot()
    else:
        raise exceptions.Error404()
    return status, headers, responseBody
