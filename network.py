# network.py
import socket
import pickle
import sys
import errno # Import errno

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = None # Server IP for client, local IP for server
        self.port = 5555 # Default port
        self.addr = None
        self.id = None # Player ID assigned by server (e.g., 1 or -1)
        self.conn = None # Connection object for the server
        self.buffer_size = 2048 * 2 # Increased buffer size

    def _send(self, target_socket, data):
        """Sends pickled data with a fixed-size header for length."""
        try:
            pickled_data = pickle.dumps(data)
            # Prepend header indicating the length of the message
            header = f"{len(pickled_data):<10}"
            target_socket.sendall(header.encode() + pickled_data)
            return True
        except socket.error as e:
            print(f"Send Error: {e}")
            return False
        except (pickle.PicklingError, OverflowError) as e:
            print(f"Pickling Error: {e}")
            return False
            
    def _receive(self, target_socket):
        """Receives data using the fixed-size header.""" 
        try:
            # Receive the header first
            header_data = b""
            while len(header_data) < 10:
                chunk = target_socket.recv(10 - len(header_data))
                if not chunk:
                    print("Connection closed while receiving header.")
                    return None
                header_data += chunk
                
            msg_len = int(header_data.decode().strip())
            
            # Receive the actual message data
            data = b""
            while len(data) < msg_len:
                chunk = target_socket.recv(min(self.buffer_size, msg_len - len(data)))
                if not chunk:
                    print("Connection closed while receiving data.")
                    return None
                data += chunk
                
            return pickle.loads(data)
        except socket.timeout:
             # print("Socket timeout during receive") # Expected during non-blocking
             return None # No data available right now
        except socket.error as e:
            # Check for WSAEWOULDBLOCK on Windows (expected non-blocking error)
            if sys.platform == 'win32' and e.winerror == errno.WSAEWOULDBLOCK:
                pass # Ignore this specific error, it's expected
            else:
                print(f"Receive Error: {e}") # Print other socket errors
            return None
        except (pickle.UnpicklingError, ValueError, EOFError) as e:
            print(f"Unpickling Error or Corrupt Data: {e}")
            return None
        except Exception as e:
            print(f"Unexpected Receive Error: {e}") # Catch other potential errors
            return None

    # --- Client Methods ---
    def connect(self, server_ip):
        self.host = server_ip
        self.addr = (self.host, self.port)
        try:
            print(f"Connecting to {self.addr}...")
            self.client.connect(self.addr)
            print("Connected. Waiting for player assignment...")
            initial_data = self._receive(self.client)
            if initial_data and 'id' in initial_data:
                self.id = initial_data['id']
                print(f"Assigned Player ID: {self.id}")
                self.client.setblocking(False)
                return self.id
            else:
                print("Failed to receive player ID from server.")
                self.close()
                return None
        except socket.error as e:
            print(f"Connection Error: {e}")
            self.close()
            return None
        except Exception as e:
             print(f"Unexpected connection error: {e}")
             self.close()
             return None

    def send_to_server(self, data):
        if not self.id:
             print("Cannot send, not connected or assigned ID.")
             return False
        return self._send(self.client, data)

    def receive_from_server(self):
        if not self.id:
             return None
        return self._receive(self.client)

    # --- Server Methods ---
    def start_server(self, host='0.0.0.0', port=5555):
        self.port = port
        self.host = host
        self.addr = (self.host, self.port)
        try:
            self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.client.bind(self.addr)
            self.client.listen(1)
            print(f"Server started on {self.host}:{self.port}. Waiting for opponent...")
            self.conn, addr = self.client.accept()
            print(f"Opponent connected from {addr}")
            self.id = 1
            if not self._send(self.conn, {'id': -1}):
                 raise Exception("Failed to send initial ID to client")
            print("Sent player assignment to opponent. Game can start.")
            self.conn.setblocking(False)
            return True 
        except socket.error as e:
            print(f"Server Error: {e}")
            self.close()
            return False
        except Exception as e:
             print(f"Unexpected server start error: {e}")
             self.close()
             return False
             
    def send_to_client(self, data):
        if not self.conn:
            print("Cannot send, no client connected.")
            return False
        return self._send(self.conn, data)

    def receive_from_client(self):
        if not self.conn:
            return None
        return self._receive(self.conn)
        
    # --- Generic Send/Receive (Based on Role) ---
    def send(self, data):
        if self.id == 1:
            return self.send_to_client(data)
        elif self.id == -1:
            return self.send_to_server(data)
        else:
            return False
            
    def receive(self):
         if self.id == 1:
            return self.receive_from_client()
         elif self.id == -1:
            return self.receive_from_server()
         else:
             return None

    # --- Cleanup ---
    def close(self):
        print("Closing network connection...")
        if self.conn:
            try:
                self.conn.close()
            except socket.error as e:
                 print(f"Error closing connection socket: {e}")
            self.conn = None
        try:
            self.client.close()
        except socket.error as e:
             print(f"Error closing main socket: {e}")
        self.id = None
