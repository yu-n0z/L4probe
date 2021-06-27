import socket
import sys
import time
import datetime

# ipアドレスを取得
PCIP = socket.gethostbyname(socket.gethostname())
# print(Srcip) # 192.168.○○○.○○○
InFlg = 0
1
#### オプションの設定
try:
    while True:
        #サーバーモードかクライアントモードを洗濯
        if InFlg == 0:
            mode =input("mode? [1:Server or 2:Clients]:")
            if mode == '1' or mode == '2':
                InFlg += 1

        #ソースIPを指定、表示されたIPのままでOKならEnter
        if InFlg == 1:
            Sip=input(f"Source IP [{PCIP}]? or type:")
            if Sip == "":
                Src_ip = PCIP
                InFlg += 1
            else:
                Src_ip = Sip
                InFlg += 1
        
        #送信元ポートを指定
        if InFlg == 2:
            x = input("Source Port?[1-65536]:")
            if x != "":
                sp = int(x)
                if  1 <= sp <= 65536:
                    S_port = str(sp)
                    InFlg += 1
        
        #宛先IPを入力する
        if InFlg == 3 and mode == "2":
            dip =input("Destination IP?")
            if dip != "":
                Dest_ip = dip
                InFlg += 1
        elif InFlg == 3 and mode == "1":
            Dest_ip = ""
            D_port = ""
            break

        #宛先ポートを指定
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

#Clientモードの処理
if mode == "2":
    init_msg = "Source_IP:" + Src_ip +  "\nSource_Port:" + S_port + "\nDest_IP:" + Dest_ip + "\nDest_port:" + D_port

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((Src_ip,int(S_port)))  # IPとポート番号を指定します
    s.connect((Dest_ip,int(D_port)))
    s.send(bytes(init_msg,'utf-8'))
    response = s.recv(1024)
    #print("[*]Received a response : {}".format(response))
    print(response.decode('utf-8'))
    
    if response.decode('utf-8') == "ack":
        try:
            while True:
                x =input(">>")

                #byeを入力した場合は終了する
                if x == "bye":
                    s.send(bytes(x,'utf-8'))
                    break

                #pingを入力した場合はpingモードに移行
                elif x == "ping":
                    try:
                        while True:
                            #送信メッセージにタイムスタンプを付与する
                            now = datetime.datetime.now()
                            Send_MSG = "TCP recieved " + str(now.time())
                            s.send(bytes(Send_MSG,'utf-8'))

                            response = s.recv(1024)
                            print(response.decode('utf-8'))
                            time.sleep(1)
                    except KeyboardInterrupt:
                        pass
                
                #CONを入力した場合はコネクション情報を取得する
                elif x == "CON":
                    s.send(bytes(x,'utf-8'))
                    response = s.recv(1024)
                    Send_MSG = "ローカルコネクション情報\nサーバーIPアドレス:" + str(Dest_ip) + "\nサーバー待ち受けport:" + str(D_port) + \
                    "\nクライアントIPアドレス:" + str(Src_ip) + "\nクライアント送信元port:" + str(S_port) + \
                    "\n\n======================================\n\n" +  response.decode('utf-8')
                    print(Send_MSG)

                #それ以外はメッセージモードとして処理
                elif x != "":
                    s.send(bytes(x,'utf-8'))
                
                Send_MSG =""

        except KeyboardInterrupt:
            s.send(bytes("bye",'utf-8'))

#サーバーモードの処理
if mode == "1":
    init_msg = "Source_IP:" + Src_ip + "\nSource_port:" + S_port
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
            decode_data = client_data.decode('utf-8')

            #bye メッセージがきたら終了
            if decode_data == "bye":
                print("ClientからByeが入力されました")
                clientsocket.close()
                ServerFlg = "1"
                break
            #メッセージモードの処理

            #TCP recieved メッセージがきたらReplyを返す
            elif decode_data[:3] == "TCP":
                print(decode_data)
                now = datetime.datetime.now()
                Reply_MSG = "TCP Reply " + str(now.time())
                clientsocket.send(bytes(Reply_MSG,'utf-8'))
            
            #GET メッセージがきた場合はサーバーのLocal情報を返す
            elif decode_data[:3] == "CON":
                Send_MSG = "リモートコネクション情報\nサーバーIPアドレス:" + str(Src_ip) + "\nサーバー待ち受けport:" + str(S_port) + \
                    "\nクライアントIPアドレス:" + str(address[0]) + "\nクライアント送信元port:" + str(address[1])
                clientsocket.send(bytes(Send_MSG,'utf-8'))
 
            elif decode_data != "":
                print(f">>",decode_data)

            Send_MSG = ""

        if ServerFlg == "1":
            break
