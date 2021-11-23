import selectors
import socket
import sys
import types

selector = selectors.DefaultSelector() # Cria um seletor

def accept_wrapper(sock):
    conn, addr = sock.accept()
    print('Aceitando conexão de: ', addr)
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb='', outb=b'') # contém dados da conexão e mensagens transmitidas
    events = selectors.EVENT_READ | selectors.EVENT_WRITE # lida com leitura e escrita
    selector.register(conn, events, data=data)

def receive_data(key, mask):
    conn = key.fileobj # obtém o socket com a conexão do cliente
    data = key.data # recebe os dados que o cliente mandou
    if mask & selectors.EVENT_READ: # se for um evento de leitura
        recv_data= conn.recv(1024)
        if recv_data is not None: # se recebe dados ...
            data.outb += recv_data # acrescenta os dados recebidos à variável outb
        else: # se não recebe dados == terminar a conexão
            print('Fechando conexão com: ', data.addr)
            selector.unregister(conn)
            conn.close()
    
    if mask & selectors.EVENT_WRITE: # Se tiver evento de escrita
        if data.outb: # se tiver dados pra escrever
            print('Mandando mensagem ', repr(data.outb), ' para ', data.addr)
            sent = sock.send(data.outb)
            data.outb = data.outb[sent:] # manda os dados aos poucos

if len(sys.argv) != 3: # Se não receber 3 parâmetros na linha do comando (script, ip, porta)
    print('Uso: ', sys.argv[0], '<host> <porta>')
    sys.exit(1)
    
host, port = sys.argv[1], sys.argv[2] # ip e porta da linha de comando
#print('IP: ', sys.argv[1], '\nPorta: ', sys.argv[2])

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Cria um socket IP/TCP
sock.bind((host, port)) # vincula ao IP e Porta
sock.listen() # Escuta na porta e IP designados
print('Ouvindo em: ', (host, port))

sock.setblocking(False) # declara o socket como não bloqueante (aceita múlt conexões)
selector.register(sock, selectors.EVENT_READ, data=None) # registra o socket para o seletor

try:
    while True:
        events = selector.select(timeout=None) # Equivale à linha do accept no echo-server
        for key, mask in events: # [(key, mask) ... ] -> events
            if key.data is None: # Primeira vez que contata-se o cliente
                # executar o código do accept
                accept_wrapper(key.fileobj)
            else: # senão, estamos recebendo dados
                # lida com os dados recebidos
                receive_data(key, mask)

except KeyboardInterrupt:
    print('Recebi ctrl-c. Saindo do programa.')

finally:
    selector.close()