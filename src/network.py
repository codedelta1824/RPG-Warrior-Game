import socket
import threading
import json

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Public cloud broker server (handles matchmaking by matching room codes)
        # Substitute with your dedicated VPS IP or free ngrok/broker address
        self.server = "broker.yourdomain.com" 
        self.port = 5555
        
        self.is_host = False
        self.room_code = None
        self.connected = False

    def connect_to_broker(self):
        """Initial connection to the matchmaking system."""
        try:
            self.client.connect((self.server, self.port))
            return True
        except Exception as e:
            print(f"[Network Error] Cannot connect to matchmaking server: {e}")
            return False

    def host_game(self, room_code):
        """Registers a newly generated room code on the network."""
        if not self.connected:
            if not self.connect_to_broker(): return False
            
        self.is_host = True
        self.room_code = room_code
        try:
            # Tell the network broker we are opening a room
            payload = {"action": "HOST", "room": str(room_code)}
            self.client.send(str.encode(json.dumps(payload)))
            
            # Start background listener to wait for broker to say client has matched
            threading.Thread(target=self._listen_for_match, daemon=True).start()
            return True
        except Exception as e:
            print(f"Hosting error: {e}")
            return False

    def join_game(self, room_code):
        """Submits a room code to match with an active host."""
        if not self.connected:
            if not self.connect_to_broker(): return False
            
        self.is_host = False
        self.room_code = room_code
        try:
            payload = {"action": "JOIN", "room": str(room_code)}
            self.client.send(str.encode(json.dumps(payload)))
            
            # Read broker confirmation response
            reply = self.client.recv(2048).decode()
            data = json.loads(reply)
            if data.get("status") == "CONNECTED":
                self.connected = True
                return True
            return False
        except Exception as e:
            print(f"Join error: {e}")
            return False

    def _listen_for_match(self):
        """Runs on host background to check when player 2 logs in."""
        try:
            reply = self.client.recv(2048).decode()
            data = json.loads(reply)
            if data.get("status") == "CONNECTED":
                self.connected = True
        except:
            pass

    def send(self, data):
        """Sends gameplay positions across the established link."""
        try:
            self.client.send(str.encode(json.dumps(data)))
            reply = self.client.recv(2048).decode()
            return json.loads(reply)
        except:
            return None