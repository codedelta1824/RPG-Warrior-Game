import threading
import json
import time

class EnetUnavailable(Exception):
    pass

class EnetNetwork:
    """A thin wrapper around pyenet (ENet) for low-latency game networking.

    This module attempts to provide a drop-in replacement API similar to
    the existing `Network` class: `host_game(room_code)`, `join_game(room_code, host_ip)`,
    `send(data)`, `disconnect()`.

    Requirements: `pyenet` (install with `pip install pyenet`).
    """
    def __init__(self, port=12345):
        try:
            import enet
        except Exception:
            raise EnetUnavailable("pyenet is not installed")

        self.enet = enet
        self.host = None
        self.peer = None
        self.is_host = False
        self.connected = False
        self.port = port
        self.room_code = None
        self.recv_lock = threading.Lock()
        self.last_received = None
        self.service_thread = None
        self.running = False

    def _service_loop(self):
        while self.running and self.host:
            event = self.host.service(0)
            if event.type == self.enet.EVENT_TYPE_NONE:
                time.sleep(0.001)
                continue
            if event.type == self.enet.EVENT_TYPE_CONNECT:
                print(f"[ENET] Connected: {event.peer.address}")
                self.peer = event.peer
                self.connected = True
            elif event.type == self.enet.EVENT_TYPE_RECEIVE:
                try:
                    text = event.packet.data.tobytes().decode()
                    parsed = json.loads(text)
                    with self.recv_lock:
                        self.last_received = parsed
                except Exception as e:
                    print(f"[ENET] Receive parse error: {e}")
                event.packet.destroy()
            elif event.type == self.enet.EVENT_TYPE_DISCONNECT:
                print("[ENET] Peer disconnected")
                self.connected = False
                self.peer = None

    def host_game(self, room_code):
        try:
            self.room_code = str(room_code)
            self.is_host = True
            self.host = self.enet.Host(self.enet.Address('0.0.0.0', self.port), 32, 2, 0, 0)
            self.running = True
            self.service_thread = threading.Thread(target=self._service_loop, daemon=True)
            self.service_thread.start()
            print(f"[ENET] Hosting on port {self.port}")
            return True
        except Exception as e:
            print(f"[ENET] Host error: {e}")
            return False

    def join_game(self, room_code, host_ip='127.0.0.1'):
        try:
            self.room_code = str(room_code)
            self.is_host = False
            self.host = self.enet.Host(None, 1, 2, 0, 0)
            addr = self.enet.Address(host_ip, self.port)
            peer = self.host.connect(addr, 2)
            # Service loop to process events
            self.running = True
            self.service_thread = threading.Thread(target=self._service_loop, daemon=True)
            self.service_thread.start()

            # Wait short time for connection
            start = time.time()
            while time.time() - start < 3.0:
                if self.connected:
                    return True
                time.sleep(0.05)
            return False
        except Exception as e:
            print(f"[ENET] Join error: {e}")
            return False

    def send(self, data):
        if not self.connected or not self.peer:
            return None
        try:
            txt = json.dumps(data).encode()
            packet = self.enet.Packet(txt, self.enet.PACKET_FLAG_RELIABLE)
            self.peer.send(0, packet)
            with self.recv_lock:
                if self.last_received is not None:
                    pkt = self.last_received
                    self.last_received = None
                    return pkt
            return None
        except Exception as e:
            print(f"[ENET] Send error: {e}")
            self.disconnect()
            return None

    def disconnect(self):
        try:
            self.running = False
            if self.peer:
                try:
                    self.peer.disconnect()
                except Exception:
                    pass
            if self.host:
                try:
                    self.host.flush()
                except Exception:
                    pass
                try:
                    del self.host
                except Exception:
                    pass
        except Exception as e:
            print(f"[ENET] Disconnect error: {e}")
        finally:
            self.host = None
            self.peer = None
            self.connected = False
            self.is_host = False
