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
        self.recv_thread = None
        self.discovery_thread = None
        self.last_received = None
        self.recv_lock = threading.Lock()
        self.discovery_sock = None
        
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
            # Start discovery responder so clients can find host via UDP broadcast
            try:
                if not self.discovery_thread:
                    self.discovery_thread = threading.Thread(target=self._discovery_responder, daemon=True)
                    self.discovery_thread.start()
            except Exception:
                pass
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
                        try:
                            conn.send(json.dumps(response).encode())
                        except Exception:
                            pass

                        # Start non-blocking recv loop for gameplay messages
                        if not self.recv_thread:
                            self.recv_thread = threading.Thread(target=self._recv_loop, daemon=True)
                            self.recv_thread.start()
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
                # Put socket into short-timeout non-blocking mode
                self.client_socket.settimeout(0.5)

                # Start recv thread to asynchronously read opponent updates
                if not self.recv_thread:
                    self.recv_thread = threading.Thread(target=self._recv_loop, daemon=True)
                    self.recv_thread.start()
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
            # Send our data non-blocking
            try:
                self.client_socket.send(json.dumps(data).encode())
            except (BrokenPipeError, ConnectionResetError, OSError) as e:
                print(f"[NETWORK] Send write error: {e}")
                self.disconnect()
                return None

            # Return the most recently received packet (if any)
            with self.recv_lock:
                if self.last_received is not None:
                    packet = self.last_received
                    self.last_received = None
                    return packet
            return None
        except Exception as e:
            print(f"[NETWORK] Send error: {e}")
            self.disconnect()
            return None

    def _recv_loop(self):
        """Background thread that continuously receives JSON packets and stores the latest."""
        try:
            while self.connected and self.client_socket:
                try:
                    data = self.client_socket.recv(4096)
                    if not data:
                        # Connection closed by peer
                        print("[NETWORK] Peer closed connection")
                        self.disconnect()
                        break
                    try:
                        text = data.decode()
                        parsed = json.loads(text)
                        with self.recv_lock:
                            self.last_received = parsed
                    except Exception as e:
                        # ignore malformed packets
                        print(f"[NETWORK] Recv parse error: {e}")
                except socket.timeout:
                    continue
                except (ConnectionResetError, OSError) as e:
                    print(f"[NETWORK] Recv socket error: {e}")
                    self.disconnect()
                    break
        except Exception as e:
            print(f"[NETWORK] Recv loop error: {e}")

    # -------------------- LAN Discovery --------------------
    def _discovery_responder(self):
        """Host-side UDP responder: replies to discovery broadcasts with host info."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(("0.0.0.0", self.port + 1))
            sock.settimeout(1)
            self.discovery_sock = sock
            while self.is_host:
                try:
                    data, addr = sock.recvfrom(1024)
                    try:
                        msg = json.loads(data.decode())
                    except Exception:
                        continue
                    if msg.get("discover") == self.room_code:
                        resp = {"host_ip": self.get_local_ip(), "port": self.port}
                        sock.sendto(json.dumps(resp).encode(), addr)
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"[DISCOVERY] Responder error: {e}")
                    break
        except Exception as e:
            print(f"[DISCOVERY] Responder setup failed: {e}")
        finally:
            try:
                if self.discovery_sock:
                    self.discovery_sock.close()
            except Exception:
                pass

    def discover_host(self, room_code, timeout=2.0):
        """Client-side LAN discovery: broadcasts room_code and waits for a host reply.

        Returns (host_ip, port) or None.
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.settimeout(timeout)
            msg = json.dumps({"discover": str(room_code)}).encode()
            # Broadcast to the LAN
            sock.sendto(msg, ("<broadcast>", self.port + 1))
            start = time.time()
            while time.time() - start < timeout:
                try:
                    data, addr = sock.recvfrom(1024)
                    try:
                        resp = json.loads(data.decode())
                    except Exception:
                        continue
                    if resp.get("host_ip") and resp.get("port"):
                        return resp.get("host_ip"), resp.get("port")
                except socket.timeout:
                    continue
            return None
        except Exception as e:
            print(f"[DISCOVERY] Client error: {e}")
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
