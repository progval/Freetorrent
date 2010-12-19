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
from common import html
from common import exceptions
from common.lib import parsers

form = u"""
<form action="submit.htm" method="post" enctype="multipart/form-data">
    <table>
        <tr>
            <th colspan="2">Informations générales</th>
        </tr>
        <tr>
            <td><label for="name">Nom :</label></td>
            <td><input type="text" id="name" name="name" /></td>
        </tr>
        <tr>
            <td><label for="license">Licence :</label></td>
            <td><input type="text" id="license" name="license" /></td>
        </tr>
        <tr>
            <td><label for="url">URL :</label></td>
            <td><input type="text" id="url" name="url" /></td>
        </tr>
        <tr>
            <td><label for="description">Description :</label></td>
            <td>
                <textarea name="description" id="description"
                          rows="auto" cols="auto"></textarea>
            </td>
        </tr>

        <tr>
            <th colspan="2">Format</th>
        </tr>
        <tr>
            <td><label for="category">Catégorie :</label></td>
            <td>
                <select name="category" id="category">
                    <option value='0' selected="selected">(choisir)</option>
                    %(categories)s
                </select>
            </td>
        </tr>
        <tr>
            <td><label for="audio">Format audio :</label></td>
            <td>
                <select name="audio" id="audio">
                    <option value='0' selected="selected">
                        (choisir)
                    </option>
                    <option value='MP3 Low Quality'>
                        MP3 basse Qualite
                    </option>
                    <option value='MP3 Medium Quality'>
                        MP3 Medium Qualite
                    </option>
                    <option value='MP3 High Quality'>
                        MP3 Haute Qualite
                    </option>
                    <option value='OGG Vorbis'>
                        OGG Vorbis
                    </option>
                    <option value='XM/MOD'>
                        XM/MOD
                    </option>
                    <option value='Free Losless Audio Codec (FLAC)'>
                        Free Losless Audio Codec (FLAC)
                    </option>
                    <option value='Advanced Audio Coding (AAC)'>
                        MPEG-4 Advanced Audio Coding (AAC)
                    </option>
                    <option value='Autre'>
                        Autre
                    </option>
                </select>
            </td>
        </tr>
        <tr>
            <td><label for="video">Format vidéo :</label></td>
            <td>
                <select name="video" id="video">
                    <option value='0' selected="selected">(choisir)</option>
                    <option value='mpeg1'>mpeg1</option>
                    <option value='mpeg2'>mpeg2</option>
                    <option value='mpeg4'>mpeg4</option>

                    <option value='XVid'>XVid</option>
                    <option value='DivX'>DivX</option>
                    <option value='h.264'>h.264</option>
                    <option value='VP3'>VP3</option>
                    <option value='OGG Theora'>OGG Theora</option>
                    <option value='Autre'>Autres</option>
                </select>
            </td>
        </tr>
        <tr>
            <th colspan="2">Fichiers</th>
        </tr>
        <tr>
            <td><label for="file">Fichier .torrent :</label></td>
            <td><input type="file" name="file" id="file" /></td>
        </tr>
        <tr>
            <td><label for="icon">Image :</label></td>
            <td><input type="file" name="icon" id="icon" /></td>
        </tr>


        <tr>
            <td colspan="2">
                <input type="submit" value="Envoyer" />
            </td>
        </tr>
    </table>
</form>"""

def run(environ):
    status = '200 OK'
    headers = []
    path = environ['module_path']
    responseBody = html.getHead(title="Soumission d'un torrent")
    if path == '':
        categoriesHtml = ''
        categories = db.conn.cursor()
        categories.execute("SELECT c_id, name FROM categories")
        for category in categories:
            categoriesHtml += '<option value="%s">%s</option>' % \
                    (category[0], category[1])

        responseBody += form % {'categories': categoriesHtml}
        responseBody += html.getFoot()
    elif path == 'submit.htm':
        data = parsers.http_query(environ, 'POST')
        assert all((key in data) for key in ('name', 'license', 'url',
                                             'description', 'category',
                                             'audio', 'video', 'file',
                                             'icon'))
    else:
        raise exceptions.Error404()

    return status, headers, responseBody
