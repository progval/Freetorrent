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

from common import html

body = u"""
<h1>À propos de Freetorrent</h1>
<h2>Ce que Freetorrent est</h2>
<p>Freetorrent est un projet et une communauté basés sur le logiciel et les
contenus libres, et qui les promouvoient. Les contenus ainsi partagés sont
sous licence libre.</p>

<h2>Ce que Freetorrent n'est pas</h2>
<p>Freetorrent n'est pas un site d'utilisation illégale du protocole
BitTorrent, puisque les contenus partagés <strong>doivent</strong> être sous
licence libre.</p>

<h2>Freetorrent est libre</h2>
<p>Les technologies utilisées par Freetorrent sont libres. Freetorrent
utilise des bases de données MySQL et SQLite et le langage de programmation
Python, le tout hébergé sur un serveur Debian GNU/Linux.
Le code de Freetorrent est sous licence libre BSD trois clauses.</p>
"""

def run(environ):
    global body
    status = '200 OK'
    headers = []
    responseBody = html.getHead(title=u'À propos')
    responseBody += body
    responseBody += html.getFoot()
    return status, headers, responseBody
