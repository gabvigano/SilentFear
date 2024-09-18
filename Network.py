import socket
import pickle
from _thread import start_new_thread


class Host:
    def __init__(self, host_type, server_ip, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if host_type == 'server':
            self.client_number = 0
            self.sock.bind((server_ip, port))
            self.images_to_send = None
            self.to_send = {}
            self.to_get = {}
            start_new_thread(self.wait_connection, ())
        else:
            try:
                self.sock.connect((server_ip, port))
                self.client_number = pickle.loads(self.sock.recv(8))  # low bytes number because the data is just a number
                print(f'\nCLIENT [__init__]: connection successful (client number: {self.client_number})')
            except socket.error:
                print('\nCLIENT [__init__]: connection failed')

    def wait_connection(self):
        connection_number = 0
        self.sock.listen()
        print('\nSERVER [wait_connection]: waiting for connection')

        while True:
            connection_number += 1

            connection, address = self.sock.accept()

            print(f'SERVER [wait_connection]: connected to: {address[0]}')

            start_new_thread(self.threaded_client, (connection, connection_number))

    @staticmethod
    def receive_data(connection, buffer=1024, max_buffer=16384):
        data = b''
        while len(data) < max_buffer:
            part = connection.recv(buffer)
            if not part:
                break  # transfer ended
            data += part
            if len(part) < buffer:
                break  # small transfer
        return data

    def threaded_client(self, connection, connection_number):  # noqa
        connection.sendall(pickle.dumps(connection_number))

        while True:
            try:
                data = self.receive_data(connection)

                if not data:
                    print('SERVER [threaded_client]: disconnected')
                    self.to_get = {}
                    break
                else:
                    self.to_get = pickle.loads(data)

                if self.images_to_send:
                    connection.sendall(self.images_to_send)
                    self.images_to_send = None
                else:
                    connection.sendall(self.to_send)

            except Exception as e:
                print(f'SERVER [threaded_client]: {e}')
                self.to_get = {}
                break

        print('SERVER [threaded_client]: connection lost')
        connection.close()

    def server_send(self, data, images=False):
        if images:
            self.images_to_send = pickle.dumps({self.client_number: data})
            return None
        else:
            self.to_send = pickle.dumps({self.client_number: data})
            return self.to_get

    def client_send(self, data):
        self.sock.send(pickle.dumps({self.client_number: data}))

        try:
            data = pickle.loads(self.receive_data(self.sock))
        except Exception as e:
            print(f'CLIENT [client_send]: {e}')

        return data
