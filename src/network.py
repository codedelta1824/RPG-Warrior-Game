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
        self.connecting = False
        self.listen_thread = None
        self.host_address = None
        self.connection_lock = threading.Lock()
        
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
        with self.connection_lock:
            if self.is_host and self.connected:
                print("[HOST] Already hosting and connected.")
                return False
            if self.connecting:
                print("[HOST] Host setup already in progress.")
                return False
            self.connecting = True

        try:
            if self.server_socket:
                try:
                    self.server_socket.close()
                except Exception:
                    pass
                self.server_socket = None

            self.is_host = True
            self.room_code = str(room_code)
            self.connected = False
            self.client_socket = None

            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(("0.0.0.0", self.port))
            self.server_socket.listen(1)
            self.server_socket.settimeout(0.5)

            self.host_address = f"{self.get_local_ip()}:{self.port}"
            print(f"[HOST] Server started on {self.host_address}")
            print(f"[HOST] Room code: {self.room_code}")

            self.listen_thread = threading.Thread(target=self._host_listen_loop, daemon=True)
            self.listen_thread.start()
            return True
        except Exception as e:
            print(f"[HOST ERROR] Failed to host game: {e}")
            self.disconnect()
            return False
        finally:
            self.connecting = False

    def _host_listen_loop(self):
        """Background thread for host to accept client connection."""
        try:
            while not self.connected and self.server_socket:
                try:
                    conn, addr = self.server_socket.accept()
                    print(f"[HOST] Client connecting from {addr}")
                    conn.settimeout(1)
                    conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

                    try:
                        data = conn.recv(1024).decode()
                        client_data = json.loads(data)
                    except Exception as handshake_error:
                        print(f"[HOST] Handshake error: {handshake_error}")
                        conn.close()
                        continue

                    if client_data.get("room") == self.room_code:
                        print(f"[HOST] Room code match! Client accepted.")
                        self.client_socket = conn
                        self.connected = True

                        response = {"status": "CONNECTED", "role": "HOST"}
                        conn.send(json.dumps(response).encode())
                        break
                    else:
                        response = {"status": "INVALID_CODE"}
                        try:
                            conn.send(json.dumps(response).encode())
                        except Exception:
                            pass
                        conn.close()
                except socket.timeout:
                    continue
                except OSError as e:
                    print(f"[HOST] Listen socket error: {e}")
                    break
                except Exception as e:
                    print(f"[HOST] Listen error: {e}")
                    break
        except Exception as e:
            print(f"[HOST] Listen thread error: {e}")

    def join_game(self, room_code, host_ip="127.0.0.1"):
        """Connect to host using room code (default localhost for LAN testing)."""
        with self.connection_lock:
            if self.connected:
                print("[CLIENT] Already connected.")
                return False
            if self.connecting:
                print("[CLIENT] Connection already in progress.")
                return False
            self.connecting = True

        try:
            self.is_host = False
            self.room_code = str(room_code)

            print(f"[CLIENT] Attempting to connect to {host_ip}:{self.port}")

            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            self.client_socket.settimeout(2)
            self.client_socket.connect((host_ip, self.port))

            print(f"[CLIENT] Connected to host! Sending room code...")
            join_data = {"room": self.room_code}
            self.client_socket.send(json.dumps(join_data).encode())

            response = self.client_socket.recv(1024).decode()
            response_data = json.loads(response)

            if response_data.get("status") == "CONNECTED":
                print(f"[CLIENT] Successfully joined! Room code accepted.")
                self.connected = True
                self.client_socket.settimeout(1)
                return True
            else:
                print(f"[CLIENT] Join failed: {response_data.get('status')}")
                self.client_socket.close()
                self.client_socket = None
                return False
        except socket.timeout:
            print(f"[CLIENT] Connection timeout - Host may not be available on {host_ip}")
            if self.client_socket:
                self.client_socket.close()
                self.client_socket = None
            return False
        except Exception as e:
            print(f"[CLIENT] Join error: {e}")
            if self.client_socket:
                self.client_socket.close()
                self.client_socket = None
            return False
        finally:
            self.connecting = False

    def send(self, data):
        """Sends gameplay data and receives opponent data."""
        if not self.connected or not self.client_socket:
            return None

        try:
            self.client_socket.send(json.dumps(data).encode())

            try:
                response = self.client_socket.recv(2048).decode()
                if response:
                    return json.loads(response)
            except socket.timeout:
                return None
        except Exception as e:
            print(f"[NETWORK] Send error: {e}")
            self.disconnect()
            return None

    def disconnect(self):
        """Clean up network resources."""
        try:
            if self.client_socket:
                self.client_socket.close()
            if self.server_socket:
                self.server_socket.close()
        except Exception as e:
            print(f"[NETWORK] Disconnect error: {e}")
        finally:
            self.client_socket = None
            self.server_socket = None
            self.connected = False
            self.connecting = False
            self.is_host = False
            self.room_code = None
            self.host_address = None
