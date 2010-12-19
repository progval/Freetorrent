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

from common import db
from common import render
from common import exceptions

fullListBodyTemplate = u"""
<table class="torrentslist" class="full">
    <tr>
        <th>Actions</th>
        <th>Nom & description</th>
        <th>Licence</th>
        <th>Catégorie</th>
    </tr>
    %s
</table>"""
fullListRowTemplate = u"""
<tr>
    <td class="actions">
        <a href="/torrents/%(name_in_url)s-%(id)s/%(name_in_url)s.torrent">
            <img src="/static/download_icon.png" alt="télécharger" />
        </a>
    </td>
    <td class="name_and_desc">
        <a href="/torrents/%(name_in_url)s-%(id)s/">%(name)s</a><br />
        %(description)s
    </td>
    <td class="license">
        %(license)s
    </td>
    <td class="category">
        %(category)s
    </td>
</tr>"""
detailsTemplate = u"""
<div class="torrent_details">
    <h1>%(name)s</h1>
    <h2>Actions</h2>
    <a href="/torrents/%(name_in_url)s-%(id)s/%(name_in_url)s.torrent">
        <img src="/static/download_icon.png" alt="télécharger" />
        Télécharger ce torrent.
    </a>
    <h2>Informations générales</h2>
    <p class="global_data">
        <div class="description">%(description)s</div>
        Licence : %(license)s
        Catégorie : %(category)s
    </p>
</div>"""

def fullList(conditions):
    torrents= db.conn.cursor()
    torrents.execute("""
            SELECT t_id, torrents.name, torrents.description, license,
                categories.name
            FROM torrents
            INNER JOIN categories USING (c_id) """ + conditions)
    rows = ''
    for torrent in torrents:
        rows += fullListRowTemplate % {
                'name_in_url': render.getUrlPrettyName(torrent[1]),
                'id': torrent[0],
                'name': torrent[1],
                'description': render.torrentDescription(torrent[2]),
                'license': torrent[3],
                'category': torrent[4]}
    return fullListBodyTemplate % rows

def details(t_id):
    torrent = db.conn.cursor()
    torrent.execute("""
            SELECT t_id, torrents.name, torrents.description,
                license, categories.name
            INNER JOIN categories USING (c_id)
            WHERE t_id=%s""", (t_id,))
    if torrent.rowcount == 0:
        raise exceptions.Error404()
    assert torrent.rowcount == 1
    torrent = torrent.fetchone()
    return detailsTemplate % {
            'name_in_url': render.getUrlPrettyName(torrent[1]),
            'id': torrent[0],
            'name': torrent[1],
            'description': render.torrentDescription(torrent[2]),
            'license': torrent[3],
            'category': torrent[4]}
