import socket

server = '127.0.0.1' # localhost - loopback
port = 12345

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.bind((server, port))
    sock.listen()
    conn, addr = sock.accept()          # Informação do cliente que conectou
    with conn:                          # Trabalhando com a conexão do cliente
        print(f'Cliente conectou com o endereço: {addr}')
        while True:                     # Loop infinito
            data = conn.recv(1024)      # Leia 1024 bytes
            if not data:                # Se não leu nada
                break                   # Sai do while
            conn.sendall(data)          # Se leu alguma coisa -> devolve pro cliente