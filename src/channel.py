def join ( self, channel, key = None ):
       
        topic = ''
        names = []
        if key != None:
            self.rsend ( 'JOIN ' + channel + ' ' + key )
        else:
            self.rsend ( 'JOIN ' + channel )
        data = self.recv()
        while self.find ( data, '366' ) == False:
                ncode = data.split() [1]

                if self.find ( data, '332' ):
                        topic = data.split ( None, 4 ) [4] [1:]
                elif self.find ( data, '333' ):
                        # implement topic, setter and time set collection
                        pass
                elif self.find ( data, '353' ):
                        names = data.split() [5:]
                        names [0] = names [0] [1:]
                elif self.find ( data, 'JOIN' ):
                        pass
                elif ncode in self.err_replies.keys(): return ncode
                else: self.buffer.append ( data )
                data = self.recv()

        return [ topic, names ]
def part ( self, channel, reason = None ):

        if reason == None:
                self.rsend ( 'PART ' + channel )
        else:
                self.rsend ( 'PART ' + channel + ' :' + reason )
        while 1:
                data = self.recv()
                ncode = data.split() [1]

                if ncode in self.err_replies.keys():
                        return ncode
                elif self.find ( data, 'PART' ):
                        pass
                else: self.buffer.append ( data )
                break
        return True
def cmode ( self, channel, modes = '' ):

        if modes == '':
                self.rsend ( 'MODE ' + channel )
                return self.recv().split() [4]
        else:   self.rsend ( 'MODE ' + channel + ' ' + modes )
        
        while 1:
                data = self.recv()
                ncode = data.split() [1]

                if ncode in self.err_replies.keys():
                        if ncode in self.err_replies.keys():
                                return ncode
                        elif self.find ( data, 'MODE' ):
                                pass
                        else: self.buffer.append ( data )
                        break
        return True
def banlist ( self, channel ):
        self.rsend ( 'MODE ' + channel + ' +b' )
        bans = []
        data = self.recv()
        while self.find ( data, '368' ) == False:
                ncode = data.split() [1]

                if ncode in self.err_replies.keys():
                        return ncode
                elif self.find ( data, '367' ):
                        bans.append ( data.split() [4] )
                else: self.buffer.append ( data )
                data = self.recv()
        return bans
def exceptlist ( self, channel ):
        self.rsend ( 'MODE ' + channel + ' +e' )
        excepts = []
        data = self.recv()
        while self.find ( data, '349' ) == False:
                ncode = data.split() [1]

                if ncode in self.err_replies.keys():
                        return ncode
                elif self.find ( data, '348' ):
                        excepts.append ( data.split() [4] )
                else: self.buffer.append ( data )
                data = self.recv()
        return excepts
def invitelist ( self, channel ):
        self.rsend ( 'MODE ' + channel + ' +i' )
        invites = []
        data = self.recv()
        while self.find ( data, '347' ) == False:
                ncode = data.split() [1]

                if ncode in self.err_replies.keys():
                        return ncode
                elif self.find ( data, '346' ):
                        invites.append ( data.split() [4] )
                else: self.buffer.append ( data )
                data = self.recv()
        return invites
def topic ( self, channel, rtopic = None ):

        if rtopic != None:
            self.rsend ( 'TOPIC ' + channel + ' :' + rtopic )
        else:
            self.rsend ( 'TOPIC ' + channel )
        topic = None
        while topic == None:
                data = self.recv()
                ncode = data.split() [1]
                if ncode in self.err_replies.keys():
                        return ncode
                elif self.find ( data, '332' ):
                        topic = data.split ( None, 4 ) [4] [1:]
                        self.recv()
                elif self.find ( data, 'PART' ):
                        pass
                elif self.find ( data, '333' ):
                        # implement topic, setter and time set collection
                        pass
                elif data.find ( '331' ) != -1: topic = ''
                else: self.buffer.append ( data )
        return topic
def names ( self, channel ):
        self.rsend ( 'NAMES ' + channel )
        names = []
        data = self.recv()
        while self.find ( data, '366' ) == False:
                ncode = data.split() [1]

                if self.find ( data, '353' ) == True:
                        names = data.split() [5:]
                        names [0] = names [0] [1:]
                elif ncode in self.err_replies.keys():
                        return ncode
                else: self.buffer.append ( data )
                data = self.recv()
        return names
def slist ( self ):
  
        self.rsend ( 'LIST' )
        list_info = { }
        data = self.recv()
        while self.find ( data, '323' ) == True:
                ncode = data.split() [1]

                if self.find ( data, '322' ) == True:
                        raw_lst = data.split ( None, 5 )
                        list_info [ raw_lst [3] ] = [ raw_lst [4], raw_lst [5] [1:] ]
                elif self.find ( data, '321' ) == False:
                        pass
                elif ncode in self.err_replies.keys():
                        return ncode
                else: self.buffer.append ( data )
                data = self.recv()
        return list_info
def invite ( self, channel, nick ):
        self.rsend ( 'INVITE ' + nick + ' ' + channel )

        while 1:
                data = self.recv()
                ncode = data.split() [1]

                if ncode in self.err_replies.keys():
                        if ncode in self.err_replies.keys():
                                return ncode
                        elif self.find ( data, '341' ):
                                pass
                        elif self.find ( data, '301' ):
                                return 'AWAY'
                        elif self.find ( data, 'INVITE' ):
                                pass
                        else: self.buffer.append ( data )
                        break
        return True
def kick ( self, channel, nick, reason = '' ):
        self.rsend ( 'KICK ' + channel + ' ' + nick + ' :' + reason )
        while 1:
                data = self.recv()
                ncode = data.split() [1]

                if ncode in self.err_replies.keys():
                        return ncode
                elif self.find ( data, 'KICK' ):
                        pass
                else: self.buffer.append ( data )
                break
        return True