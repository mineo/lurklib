#    This file is part of Lurklib.
#    Copyright (C) 2010  Jamie Shaw (LK-)
#
#    Lurklib is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Lurklib is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Lurklib.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import with_statement


class _Connection(object):
    def _connect(self, server, port, tls=False):
        """
        Connects the socket to an IRC server.
        Required arguments:
        * server - Server to connect to.
        * port - Port to use.
        Optional arguments:
        * tls=False - Should we use TLS/SSL?
        """
        with self.lock:
            if tls:
                self._socket = self._m_tls.wrap_socket(self._socket)
            self._socket.connect((server, port))

    def _register(self, nick, user, real_name, password=None):
        """
        Register the connection with the IRC server.
        Required arguments:
        * nick - Nick to use. If a tuple/list is specified -
            it will try to use the first,
            and if the first is already used -
             it will try to use the second and so on.
        * user - Username to use.
        * real_name - Real name to use.
        Optional arguments:
        * password=None - IRC server password.
        """
        with self.lock:
            if password:
                self._password(password)

            self.nick(nick)
            self._user(user, real_name)

    def _init(self, server, nick, user, real_name,
              password, port=None, tls=False):
        """
        Connect and register with the IRC server and -
            set server-related information variables.
        Required arguments:
        * server - Server to connect to.
        * nick - Nick to use.
            If a tuple/list is specified it will try to use the first,
            and if the first is already used -
            it will try to use the second and so on.
        * user - Username to use.
        * real_name - Real name to use.
        * password=None - IRC server password.
        Optional arguments:
        * port - Port to use.
        * tls=False - Should we use TLS/SSL?
        """
        with self.lock:
            if tls:
                if not port:
                    port = 6697
                self._connect(server, port, True)
            else:
                if port == None:
                    port = 6667

                self._connect(server, port)
            while self.readable(2):
                data = self.stream()
                if data[0] == 'NOTICE':
                        self.server = data[1][0]
                self.con_msg.append(data)

            self._register(nick, user, real_name, password)
            while self.readable(timeout=4):
                rdata = self.stream()
                if rdata[0] == 'UNKNOWN':
                    data = rdata[1][3].replace(':', '', 1)
                    ncode = data[1]

                    if ncode == '004':
                        info = data.split()
                        self.server = info[0]
                        self.ircd = info[1]
                        self.umodes = info[2]
                        self.cmodes = info[3]
                    elif ncode == '005':
                        version = data.replace
                        (':are supported by this server', '')
                        version = version.split()
                        for info in version:
                            try:
                                info = info.split('=')
                                name = info[0]
                                value = info[1]
                                self.version[name] = value

                                if name == 'CHARSET':
                                    self.encoding = value
                            except IndexError:
                                self.version[info[0]] = True
                    elif ncode == '372':
                        self.motd.append(data)
                    elif ncode == '376':
                        self.con_msg.append(data)
                        break
                    elif ncode == '422':
                        self.con_msg.append(data)
                        break
                else:
                    if rdata[0] == 'NOTICE':
                        self.server = rdata[1][0]

                self.con_msg.append(rdata[1])

            self.motd = tuple(self.motd)
            self.con_msg = tuple(self.con_msg)
            self.connected = True
            self.keep_going = \
                True

    def _password(self, password):
        """
        Authenticates with the IRC server.
        Required arguments:
        * password - Password to send.
        """
        with self.lock:
            self.send('PASS :%s' % password)

            if self.readable():
                data = self._recv()
                ncode = data.split()[1]
                if ncode in self.error_dictionary:
                        self.exception(ncode)
                else:
                    self._index -= 1

    def _nick(self, nick):
        """
        Sets your nick.
        Required arguments:
        * nick - New nick.
        """
        with self.lock:
            self.send('NICK :%s' % nick)

            if self.readable():
                data = self._recv()
                ncode = data.split()[1]
                if ncode in self.error_dictionary:
                        self.exception(ncode)
                elif data.split()[1] == 'NICK' and self.hide_called_events:
                    pass
                else:
                    self._index -= 1

            for channel in self.channels:
                priv_level = self.channels[channel]['USERS'][self.current_nick]
                del self.channels[channel]['USERS'][self.current_nick]
                self.channels[channel]['USERS'][nick] = priv_level
            self.current_nick = nick

    def nick(self, nick):
        """
        Sets your nick.
        Required arguments:
        * nick - New nick or a tuple of possible new nicks.
        """
        nick_set_successfully = False
        try:
            self._nick(nick)
            nick_set_successfully = True
        except TypeError:
            for nick_ in nick:
                try:
                    self._nick(nick_)
                    nick_set_successfully = True
                    break

                except self.NicknameInUse:
                    pass
        if nick_set_successfully == False:
            self.exception('433')

    def _user(self, user, real_name):
        """
        Sends the USER message.
        Required arguments:
        * user - Username to send.
        * real_name - Real name to send.
        """
        with self.lock:
            self.send('USER %s 0 * :%s' % (user, real_name))
            if self.readable():
                data = self._recv()
                ncode = data.split()[1]
                if ncode in self.error_dictionary:
                        self.exception(ncode)
                else:
                    self._index -= 1

    def oper(self, name, password):
        """
        Opers up.
        Required arguments:
        * name - Oper name.
        * password - Oper password.
        """
        with self.lock:
            self.send('OPER %s %s' % (name, password))
            snomasks = ''
            new_umodes = ''
            if self.readable():
                    data = self._recv()
                    ncode = data.split()[1]

                    if ncode in self.error_dictionary:
                            self.exception(ncode)
                    elif self.find(data, 'MODE'):
                            new_umodes = data.split()[-1].replace(':', '', 1)
                    elif ncode == '381':
                            return new_umodes, snomasks
                    elif ncode == '008':
                            snomasks = data.split('(')[1].split(')')[0]
                    else:
                        self._index -= 1

    def umode(self, nick, modes=''):
        """
        Sets/gets user modes.
        Required arguments:
        * nick - Nick to set/get user modes for.
        Optional arguments:
        * modes='' - Sets these user modes on a nick.
        """
        with self.lock:
            if modes == '':
                self.send('MODE %s' % nick)
                modes = ''
                if self.readable():
                    modes = ' '.join(self._recv().split()[3:])
                    modes = modes.replace('+', '').replace(':', '', 1)
                return modes

            else:
                self.send('MODE %s %s' % (nick, modes))

            if self.readable():
                    data = self._recv()
                    ncode = data.split()[1]

                    if ncode in self.error_dictionary:
                            self.exception(ncode)
                    elif ncode == '221':
                            return data.split()[3].replace(':', '', 1)
                    elif self.find(data, 'MODE') and self.hide_called_events:
                            pass
                    else:
                        self._index -= 1

    def service(self):
        """ Not implemented. """
        pass

    def _quit(self, reason=''):
        """
        Sends a QUIT message to the server.
        Optional arguments:
        * reason='' - Reason for quitting.
        """
        with self.lock:
            self.send('QUIT :%s' % reason)

    def quit(self, reason=''):
        """
        Sends a QUIT message, closes the connection and -
            ends Lurklib's mainloop.
        Optional arguments:
        * reason='' - Reason for quitting.
        """
        with self.lock:
            self.keep_going = False
            self._quit(reason)
            self._socket.shutdown(self._m_socket.SHUT_RDWR)
            self._socket.close()

    def __close__(self):
        """ For use with the Python 'with' statement. """
        with self.lock:
            self.quit()

    def __del__(self):
        """ For use with Python's automatic garbage collection and such. """
        with self.lock:
            try:
                self.quit()
            except self._m_socket.error:
                pass

    def squit(self, server, reason=''):
        """
        Quits a server.
        Required arguments:
        * server - Server to quit.
        Optional arguments:
        * reason='' - Reason for the server quitting.
        """
        with self.lock:
            self.send('SQUIT %s :%s' % (server, reason))

            while self.readable():
                    data = self._recv()
                    ncode = data.split()[1]

                    if ncode in self.error_dictionary:
                            self.exception(ncode)

                    elif self.find(data, 'SQUIT') and self.hide_called_events:
                            pass
                    else:
                        self._index -= 1

    def latency(self):
        """ Checks the connection latency. """
        with self.lock:
            self.send('PING %s' % self.server)
            ctime = self._m_time.time()

            data = self._recv().split()[1]
            if data == 'PONG':
                latency = self._m_time.time() - ctime
                return latency
            else:
                self._index -= 1
