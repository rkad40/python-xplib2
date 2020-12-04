from Crypto.Cipher import AES
from Crypto.Hash import SHA256
import json, base64, fs
from datetime import datetime
from regx import Regx

class Session():

    def __init__(self, secret_token=None, session_dir=None, expires_after=None, debug=False):
        """
            Create Session.
            ## Arguments
            - secret_token: secret key for seeding encryption (required)
            - session_dir: directory where session files are stored (required)
            - expires_after: how many minutes will the current session be active (optional - no time limit if None or 0)
            - debug: enables/disables debug mode (optional, default=False)
            ## Details
            Instantiate session object.  
        """
        me = self
        me.debug = debug
        # Validate input parameters.
        if secret_token is None: raise Exception("Session requires parameter \"secret_token\" to be defined")
        if session_dir is None: raise Exception("Session requires parameter \"session_dir\" to be defined")
        # Make sure secret_token is exactly 16 characters in length.
        while len(secret_token) < 16: secret_token += '$'
        if len(secret_token) > 16: secret_token = secret_token[0:16]
        me.secret_token = secret_token
        me.secret_token_bytes = me.secret_token.encode()
        # Create init_vector.
        me.init_vector = 'pt3%Pu^510*r-qM7'
        me.init_vector_bytes = me.init_vector.encode()
        # Initialize other instance variables.
        me.session_key = ''
        me.file_key = ''
        me.session_file = None
        me.data = None
        me.header = None
        me.has_expired = False
        me.expires_after = expires_after
        # Format session_dir variable and create it if necesary.  
        if not fs.is_abs_path(session_dir): session_dir = fs.get_abs_path(session_dir)
        me.session_dir = session_dir
        if not fs.dir_exists(me.session_dir): fs.create_dir(me.session_dir)

    def init(self, session_key=None, reset=False):
        """
            Get session data.
            ## Arguments
            - session_key: if specified, use the designated session key; otherwise create and 
              assign a new key
            ## Details
            From session key (me.session_key), derive sesion file name (me.file_key).  If the file
            exist, read it and populate data (me.header and me.data).  If the me.debug is True,
            write a session-start.json file with the non-encrypted session data.
        """
        me = self
        # Get epoch time stampe e.g. 1580703316.75019042
        now = datetime.timestamp(datetime.now())
        # Create me.session_key if necessary.
        if session_key is not None: 
            me.session_key = str(session_key)
        else:
            ts = str(now)
            # if me.debug: ts = 1580705585.6899998
            if me.debug: print(ts)
            # Convert epoch to string and append me.secret_token. 
            ts = str(ts) + me.secret_token
            if me.debug: print(ts)
            session_key_data = str(ts).encode()
            sha256_obj = SHA256.new(data=session_key_data)
            # Generate me.session_key as utf-8 encoded string.
            me.session_key = base64.b16encode(sha256_obj.digest()).decode()[10:42]
        if me.debug: print(me.session_key)
        # Create me.file_key.
        file_key_data = str(me.session_key) + me.secret_token
        sha256_obj = SHA256.new(data=file_key_data.encode())
        me.file_key = base64.b16encode(sha256_obj.digest()).decode()[10:42]
        if me.debug: print(me.file_key)
        # Read the session data if the session file exists.
        me.session_file = fs.join_names(me.session_dir, me.file_key)
        if fs.file_exists(me.session_file):
            b16e = fs.read_file(me.session_file, to_string=True)
            data = me.__decrypt_data(b16e)
            print(data)
            me.header = data['Header'] if 'Header' in data else {}
            me.data = data['Session'] if 'Session' in data else {}
        else:
            me.header = {}
            me.data = {}
        # Update the header info.
        me.header['AccessCount'] = 1 if 'AccessCount' not in me.header else me.header['AccessCount'] + 1
        me.header['LastRead'] = int(now)
        me.header['ValidSession'] = True
        me.header['HasExpiration'] = False
        if me.expires_after:
            me.header['HasExpiration'] = True
            if reset:
                me.header['ExpiresAfter'] = int(now + (60 * me.expires_after))
            if 'ExpiresAfter' in me.header:
                if now > me.header['ExpiresAfter']: 
                    me.has_expired = True
                    me.header['ValidSession'] = False
                else:
                    me.header['ExpiresAfter'] = int(now + (60 * me.expires_after))
            else:
                me.header['ExpiresAfter'] = int(now + (60 * me.expires_after))
        # If debug, write a debug 'session-start.json' file.
        if me.debug:
            data = {'Header': me.header, 'Session': me.data}
            json_text = json.dumps(data, indent=2)
            file_name = fs.join_names(me.session_dir, 'session-start.json')
            fs.write_file(file_name, json_text)

    def save(self):
        me = self
        # Get epoch time stampe e.g. 1580703316.75019042
        now = datetime.timestamp(datetime.now())
        # Update header data.
        me.header['LastSave'] = int(now)
        # Freeze data
        data = {'Header': me.header, 'Session': me.data}
        json_text = json.dumps(data, indent=2)
        if me.debug:
            file_name = fs.join_names(me.session_dir, 'session-stop.json')
            fs.write_file(file_name, json_text)
        # Encrypt json_text and render in utf-8 base 16. 
        b16e = me.__encrypt_data(data)
        # Write the session data.
        me.session_file = fs.join_names(me.session_dir, me.file_key)
        fs.write_file(me.session_file, b16e)

    def has_data(self):
        me = self
        if len(me.data) > 0: return(True)
        return(False)

    def __encrypt_data(self, data):
        me = self
        debug = False
        if debug: print(data)
        json_text = json.dumps(data)
        if debug: print(json_text)
        while len(json_text) % 16 != 0: json_text += " "
        if debug: print(json_text)
        json_text = json_text.encode()
        # Encrypt json_text to b16e (using secret_token and init_vector).
        aes = AES.new(me.secret_token_bytes, AES.MODE_CBC, me.init_vector_bytes)
        enc = aes.encrypt(json_text)
        if debug: print(enc)
        b16e = base64.b16encode(enc).decode()
        if debug: print(b16e)
        return(b16e)

    def __decrypt_data(self, b16e):
        me = self
        debug = False
        # Decrypt b16e. Render as post_data dict.
        enc = base64.b16decode(b16e)
        if debug: print(enc)
        aes = AES.new(me.secret_token_bytes, AES.MODE_CBC, me.init_vector_bytes)
        dec = aes.decrypt(enc)
        if debug: print(dec)
        data = json.loads(dec)
        if debug: print(data)
        return(data)



