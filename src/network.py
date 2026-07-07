import socket
import threading
import json
import time

class Network:
    def __init__(self):
        self.server_socket = None
        self.client_socket = None
        self.is_host = False
        self.room_code = None
        self.connected = False
        self.listen_thread = None
        self.host_address = None
        
        # Local LAN configuration
        self.port = 12345
        self.receive_buffer = ""

    def get_local_ip(self):
        """Get the local IP address of the machine."""
        try:
            # Connect to a remote address to get local IP
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.connect(("8.8.8.8", 80))
            local_ip = sock.getsockname()[0]
            sock.close()
            return local_ip
        except Exception:
            return "127.0.0.1"

    def host_game(self, room_code):
        """Sets up the host server to accept client connections."""
        try:
            self.is_host = True
            self.room_code = str(room_code)
            
            # Create server socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(("0.0.0.0", self.port))
            self.server_socket.listen(1)
            self.server_socket.settimeout(1)  # Non-blocking with timeout
            
            self.host_address = f"{self.get_local_ip()}:{self.port}"
            print(f"[HOST] Server started on {self.host_address}")
            print(f"[HOST] Room code: {self.room_code}")
            
            # Start listening thread for client connection
            self.listen_thread = threading.Thread(target=self._host_listen_loop, daemon=True)
            self.listen_thread.start()
            return True
        except Exception as e:
            print(f"[HOST ERROR] Failed to host game: {e}")
            return False

    def _host_listen_loop(self):
        """Background thread for host to accept client connection."""
        try:
            while not self.connected and self.server_socket:
                try:
                    conn, addr = self.server_socket.accept()
                    print(f"[HOST] Client connecting from {addr}")
                    
                    # Receive join request from client
                    data = conn.recv(1024).decode()
                    client_data = json.loads(data)
                    
                    if client_data.get("room") == self.room_code:
                        print(f"[HOST] Room code match! Client accepted.")
                        self.client_socket = conn
                        self.connected = True
                        
                        # Send confirmation
                        response = {"status": "CONNECTED", "role": "HOST"}
                        conn.send(json.dumps(response).encode())
                        break
                    else:
                        # Room code mismatch
                        response = {"status": "INVALID_CODE"}
                        conn.send(json.dumps(response).encode())
                        conn.close()
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"[HOST] Listen error: {e}")
                    break
        except Exception as e:
            print(f"[HOST] Listen thread error: {e}")

    def join_game(self, room_code, host_ip="127.0.0.1"):
        """Connect to host using room code (default localhost for LAN testing)."""
        try:
            self.is_host = False
            self.room_code = str(room_code)
            
            print(f"[CLIENT] Attempting to connect to {host_ip}:{self.port}")
            
            # Try to connect to host
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.settimeout(5)
            self.client_socket.connect((host_ip, self.port))
            
            print(f"[CLIENT] Connected to host! Sending room code...")
            
            # Send join request with room code
            join_data = {"room": self.room_code}
            self.client_socket.send(json.dumps(join_data).encode())
            
            # Wait for response
            response = self.client_socket.recv(1024).decode()
            response_data = json.loads(response)
            
            if response_data.get("status") == "CONNECTED":
                print(f"[CLIENT] Successfully joined! Room code accepted.")
                self.connected = True
                self.client_socket.settimeout(1)  # Set non-blocking timeout
                return True
            else:
                print(f"[CLIENT] Join failed: {response_data.get('status')}")
                self.client_socket.close()
                return False
                
        except socket.timeout:
            print(f"[CLIENT] Connection timeout - Host may not be available on {host_ip}")
            return False
        except Exception as e:
            print(f"[CLIENT] Join error: {e}")
            return False

    def send(self, data):
        """Sends gameplay data and receives opponent data."""
        if not self.connected or not self.client_socket:
            return None
        
        try:
            # Send our data
            self.client_socket.send(json.dumps(data).encode())
            
            # Receive opponent data
            try:
                response = self.client_socket.recv(2048).decode()
                if response:
                    return json.loads(response)
            except socket.timeout:
                # Timeout is OK - just return None to skip this frame
                return None
        except Exception as e:
            print(f"[NETWORK] Send error: {e}")
            return None

    def disconnect(self):
        """Clean up network resources."""
        try:
            if self.client_socket:
                self.client_socket.close()
            if self.server_socket:
                self.server_socket.close()
            self.connected = False
        except Exception as e:
            print(f"[NETWORK] Disconnect error: {e}")