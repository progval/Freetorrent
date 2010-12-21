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
import time
from common import db
from common import html
from common import user
from common import render
from common import exceptions
from common.lib import parsers

forumMatch = re.compile('^%s-(?P<f_id>[0-9]+)/$' % render.urlAvailableChars)
topicMatch = re.compile('^%s-(?P<f_id>[0-9]+)/%s-(?P<t_id>[0-9]+)/$' % \
                        (render.urlAvailableChars, render.urlAvailableChars))
newTopicMatch = re.compile('^%s-(?P<f_id>[0-9]+)/new/.*$' %
                           render.urlAvailableChars)
newMessageMatch=re.compile('^%s-(?P<f_id>[0-9]+)/%s-(?P<t_id>[0-9]+)/reply/.*$'\
                        % (render.urlAvailableChars, render.urlAvailableChars))

forumsListTemplate = u"""
<table class="forumslist">
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
lastForumMessageTemplate = u"""<a href="%(url)s#msg%(msg_id)s">
    %(topic_name)s par %(user_name)s
</a>"""

topicsListTemplate = u"""
<h2>%s</h2>
<form action="new/" method="get">
    <p><input type="submit" value="Nouveau sujet" /></p>
</form>
<table class="topicslist">
    <tr>
        <th>Nouveaux messages</th>
        <th>Nom</th>
        <th>Messages</th>
        <th>Dernier message</th>
    </tr>
    %s
</table>"""
topicRowTemplate = u"""<tr>
    <td class="%(newmsg_prefix)snewmsg">%(newmsg)s</td>
    <td class="name"><a href="%(url)s">%(topic_name)s</a></td>
    <td class="count">%(posts)s</td>
    <td class="lastmessage">%(lastmessage)s</td>
</tr>"""
lastTopicMessageTemplate = u"""<a href="%(url)s#msg%(msg_id)s">
    par %(user_name)s
</a>"""

topicBodyTemplate = u"""
<h2>%s</h2>
<form action="reply/" method="get">
    <p><input type="submit" value="Répondre" /></p>
</form>
<table class="topic">
    <tr>
        <th>Auteur</th>
        <th>Message</th>
    </tr>
    %s
</table>"""
messageRowTemplate = u"""
<tr>
    <td class="author">
        <a href="%(user_url)s">%(user_name)s</a><br />
        %(avatar)s
    </td>
    <td class="message">
        <a name="msg%(id)s"></a>
        %(message_content)s
    </td>
</tr>"""

textarea = u"""
<label for="content">Message</label><br />
<textarea name="content" id="content"></textarea>"""
newTopicTemplate = u"""
<form action="submit.htm" method="post">
    <label for="title">Titre :</label>
    <input type="title" name="title" id="title" />
    <br />
    %s
    <br />
    <input type="submit" value="Créer le sujet" />
</form>""" % textarea
newMessageTemplate = u"""
<form action="submit.htm" method="post">
    %s
    <br />
    <input type="submit" value="Répondre" />
</form>""" % textarea

notAllowedTemplate = u"""
<p>
    Désolé, mais vous n'avez pas l'autorisation d'effectuer cette action.
    <br />
    Si vous n'êtes pas connecté(e), essayez de vous connecter, ou de vous
    enregistrer si vous n'avez pas encore de compte.
</p>"""

failedSubmitionTemplate = u"""
L'envoi du message a échoué, pour une raison inconnue. Vous pouvez
récupérer son contenu, pour essayer de l'envoyer à nouveau :
<pre class="recover_message">
%(content)s
</pre>"""

def addForumPrefix(function):
    def decorate(*args, **kwargs):
        return '/forum' + function(*args, **kwargs)
    return decorate

@addForumPrefix
def getTopicUrl(t_id):
    cursor = db.conn.cursor()
    cursor.execute("""SELECT forums.name, topics.title, forums.f_id, t_id
            FROM topics, forums
            WHERE topics.f_id=forums.f_id and t_id=%s""", (t_id,))
    assert cursor.rowcount <= 1
    if cursor.rowcount == 0:
        return '/forums/'
    else:
        row = cursor.fetchone()
        return '/%s-%i/%s-%i/' % (render.getUrlPrettyName(row[0]),
                                 row[2],
                                 render.getUrlPrettyName(row[1]),
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
        return '/%s-%i/' % (render.getUrlPrettyName(row[0]),
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
                    ORDER BY messages.last_update DESC
                    LIMIT 0,1;""", (forum[0],))
            lastMessage = lastMessage.fetchone()
            if lastMessage is None:
                lastMessage = 'aucun'
            else:
                lastMessage = lastForumMessageTemplate % \
                        {'url': getTopicUrl(lastMessage[1]),
                        'msg_id': lastMessage[0],
                        'topic_name': lastMessage[2],
                        'user_name': lastMessage[3]}
            if user.currentUser.id != 0:
                topics = db.conn.cursor()
                topics.execute("SELECT t_id FROM topics WHERE f_id=%s", (forum[0],))
                notRead = 0
                for topic in topics:
                    lastRead = db.conn.cursor()
                    lastRead.execute("""
                            SELECT time FROM last_read
                            WHERE u_id=%s AND t_id=%s""",
                            (user.currentUser.id, topic[0]))
                    if lastRead.rowcount == 0:
                        lastRead = 0
                    else:
                        lastRead = lastRead.fetchone()[0]
                    counter = db.conn.cursor()
                    counter.execute("""
                            SELECT COUNT(*) FROM messages
                            WHERE t_id=%s AND UNIX_TIMESTAMP(last_update)>%s""",
                            (topic[0], lastRead))
                    row = counter.fetchone()
                    notRead += row[0]
            else:
                notRead = 0
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
        return status, headers, responseBody
    parsed = forumMatch.match(path)
    if parsed is not None:
        f_id = parsed.group('f_id')
        forum = db.conn.cursor()
        forum.execute("SELECT name FROM forums WHERE f_id = %s", f_id)
        if forum.rowcount < 1:
            raise exceptions.Error404()
        forum = forum.fetchone()
        responseBody = html.getHead(title=u"%s (forum)" % forum[0])
        topicRows = u''
        topics = db.conn.cursor()
        topics.execute("SELECT t_id, title FROM topics WHERE f_id=1")
        for topic in topics:
            lastMessage = db.conn.cursor()
            lastMessage.execute("""SELECT messages.m_id, users.name
                    FROM messages, users
                    WHERE t_id=%s
                        AND users.u_id=messages.u_id
                    ORDER BY messages.last_update DESC
                    LIMIT 0,1;""", (topic[0],))
            lastMessage = lastMessage.fetchone()
            if lastMessage is None:
                lastMessage = 'aucun'
            else:
                lastMessage = lastTopicMessageTemplate % \
                        {'url': getTopicUrl(topic[0]),
                        'msg_id': lastMessage[0],
                        'user_name': lastMessage[1]}
            if user.currentUser.id != 0:
                lastRead = db.conn.cursor()
                lastRead.execute("""
                        SELECT time FROM last_read
                        WHERE t_id=%s AND last_read.u_id=%s""",
                                 (topic[0], user.currentUser.id))
                row = lastRead.fetchone()
                if row is None:
                    lastRead = 0
                else:
                    lastRead = row[0]
                notRead = db.conn.cursor()
                notRead.execute("""
                        SELECT COUNT(*) FROM messages
                        WHERE UNIX_TIMESTAMP(last_update)>%s AND t_id=%s""",
                        (lastRead,topic[0]))
                notRead = notRead.fetchone()[0]
            else:
                notRead = 0
            if notRead == 0:
                prefix = 'no'
            else:
                prefix = ''
            topicRow = topicRowTemplate % \
                    {'newmsg_prefix': prefix,
                    'newmsg': notRead,
                    'url': getTopicUrl(topic[0]),
                    'topic_name': topic[1],
                    'posts': getTopicPostsCount(topic[0]),
                    'lastmessage': lastMessage}
            topicRows += topicRow
        responseBody += topicsListTemplate % (forum[0], topicRows)
        responseBody += html.getFoot()
        return status, headers, responseBody
    parsed = topicMatch.match(path)
    if parsed is not None:
        f_id = parsed.group('f_id')
        t_id = parsed.group('t_id')
        topic = db.conn.cursor()
        topic.execute("SELECT title FROM topics WHERE t_id=%s", (t_id,))
        if topic.rowcount == 0:
            raise exceptions.Error404()
        topic = topic.fetchone()
        updateLastRead = db.conn.cursor()
        args = (t_id, user.currentUser.id)
        updateLastRead.execute("""
                DELETE FROM last_read
                WHERE t_id=%s AND u_id=%s""", args)
        updateLastRead.execute("INSERT INTO last_read VALUES(%s, %s, %s)",
                               args + (time.time(),))
        messages = db.conn.cursor()
        messages.execute("""
                SELECT m_id, content, created_on, users.u_id, users.name, avatar
                FROM messages
                INNER JOIN users USING (u_id)
                WHERE t_id=%s""", (t_id,))
        responseBody = html.getHead(title=u"%s (sujet)" % topic[0])
        messageRows = u''
        for message in messages:
            def getAvatarHtml(avatarUrl):
                if avatarUrl != '':
                    return '<img src="%s" alt="avatar" />' % avatarUrl
                else:
                    return ''
            messageRow = messageRowTemplate % \
                    {'user_url': '/users/%s/' % message[4],
                    'user_name': message[4],
                    'avatar': getAvatarHtml(message[5]),
                    'message_content': render.forum(message[1]),
                    'id': message[0]}
            messageRows += messageRow
        responseBody += topicBodyTemplate % (topic[0], messageRows)
        responseBody += html.getFoot()
        return status, headers, responseBody
    parsed = newTopicMatch.match(path)
    if parsed is not None:
        f_id = parsed.group('f_id')
        responseBody = html.getHead(title='Nouveau sujet')
        if user.currentUser.id == 0:
            responseBody += notAllowedTemplate
        elif path.endswith('submit.htm'):
            data = parsers.http_query(environ, 'POST')
            assert all((key in data) for key in ('title', 'content'))
            cursor = db.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM forums WHERE f_id=%s", (f_id,))
            try:
                assert cursor.fetchone()[0] == 1
                cursor.execute("INSERT INTO topics VALUES('', %s, %s)",
                               (f_id, data['title']))
                cursor.execute("""
                        INSERT INTO messages
                        VALUES('', %s, %s, %s, CURRENT_TIMESTAMP, '')""",
                        (cursor.lastrowid,user.currentUser.id,data['content']))
                responseBody += u"<p>Le sujet a été créé avec succès.</p>"
                status = '302 Found'
                headers.append(('Location', '../'))
            except Exception, e:
                print repr(e)
                responseBody += failedSubmitionTemplate % \
                        {'content': data['content']}
        else:
            responseBody += newTopicTemplate
        responseBody += html.getFoot()
        return status, headers, responseBody
    parsed = newMessageMatch.match(path)
    if parsed is not None:
        t_id = parsed.group('t_id')
        responseBody = html.getHead(title=u'Réponse au sujet')
        if user.currentUser.id == 0:
            responseBody += notAllowedTemplate
        elif path.endswith('submit.htm'):
            data = parsers.http_query(environ, 'POST')
            assert all((key in data) for key in ('content'))
            cursor = db.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM topics WHERE t_id=%s", (f_id,))
            try:
                assert cursor.fetchone()[0] == 1
                cursor.execute("""
                        INSERT INTO messages
                        VALUES('', %s, %s, %s, CURRENT_TIMESTAMP, '')""",
                        (t_id, user.currentUser.id, data['content']))
                responseBody += u"<p>La réponse a été envoyée avec succès.</p>"
                status = '302 Found'
                headers.append(('Location', '../'))
            except Exception, e:
                print repr(e)
                responseBody += failedSubmitionTemplate % \
                        {'content': data['content']}
        else:
            responseBody += newMessageTemplate
        responseBody += html.getFoot()
        return status, headers, responseBody
    raise exceptions.Error404()
