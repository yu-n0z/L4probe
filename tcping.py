from os import truncate
import socket
import sys

# ipアドレスを取得
PCIP = socket.gethostbyname(socket.gethostname())
# print(Srcip) # 192.168.○○○.○○○
InFlg = 0
1
#### オプションの設定
try:
    while True:
        if InFlg == 0:
            mode =input("mode? [1:Server or 2:Clients]:")
            if mode == '1' or mode == '2':
                InFlg += 1

        if InFlg == 1:
            Sip=input(f"Source IP [{PCIP}]? or type:")
            if Sip == "":
                Src_ip = PCIP
                InFlg += 1
            else:
                Src_ip = Sip
                InFlg += 1
        
        if InFlg == 2:
            x = input("Source Port?[1-65536]:")
            if x != "":
                sp = int(x)
                if  1 <= sp <= 65536:
                    S_port = str(sp)
                    InFlg += 1
        
        if InFlg == 3 and mode == "2":
            dip =input("Destination IP?")
            if dip != "":
                Dest_ip = dip
                InFlg += 1
        elif InFlg == 3 and mode == "1":
            Dest_ip = ""
            D_port = ""
            break

        if InFlg == 4 and mode == "2":
            x=input("Destination Port?[1-65536]:")
            if x != "":
                dp=int(x)
                if  1 <=  dp <= 65536:
                    D_port = str(dp)
                    InFlg+=1

        if InFlg == 5:
            break
except KeyboardInterrupt:
    print('\n終了')
    sys.exit()

# print(f"送信元IP{Src_ip}\n送信元ポート{S_port}\n宛先IP{Dest_ip}\n宛先ポート{D_port}")
if mode == "2":
    init_msg = "Sourte_IP:" + Src_ip +  "\nSource_Port:" + S_port + "\nDest_IP:" + Dest_ip + "\nDest_port:" + D_port

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((Src_ip,int(S_port)))  # IPとポート番号を指定します
    s.connect((Dest_ip,int(D_port)))
    s.send(bytes(init_msg,'utf-8'))
    response = s.recv(1024)
    #print("[*]Received a response : {}".format(response))
    print(response)
    
    if response == bytes("ack",'utf-8'):
        while True:
        
            x =input("press any key:")
            if x != "" and x != "bye":
                s.send(bytes(x,'utf-8'))
            elif x == "bye":
                s.send(bytes(x,'utf-8'))
                break

if mode == "1":
    ServerFlg = 0
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((Src_ip,int(S_port)))  # IPとポート番号を指定します
    s.listen(1)

    while True:
        clientsocket, address = s.accept()
        print(f"Connection from {address} has been established!")
        clientsocket.send(bytes("ack", 'utf-8'))

        client_data = clientsocket.recv(1024)
        print(client_data.decode('utf-8'))
        
        while True:
            client_data = clientsocket.recv(1024)
            print(f">>",client_data.decode('utf-8'))

            if client_data.decode('utf-8') == "bye":
                clientsocket.close()
                ServerFlg = "1"
                break
        if ServerFlg == "1":
            break

