import socket
import sys
import time
import datetime
from typing import Protocol

Software_version = '\
        \n\t\t=================================================================\n\
            \t| software version 1.01\t\t\t\t\t\t|\n\
            \t| This software is a trial version.\t\t\t\t|\n\
            \t| The trial period is until 2022/06/30.\t\t\t\t|\n\
            \t=================================================================\n'
                                                                                    
#           \t| if the trial period expires, please purchase a license.\t|\n\

command_help = '\n\ncommand list\n\
    ping\t\t...Continuous Packet Transmission\n\
    CON\t\t\t...Connection Info\n\
    CHANGE <port>\t...Change Server Port\n\
    CLOSE\t\t...Close the session while leaving the listening port\n\
    BYE\t\t\t...Quit Application\n'


print(Software_version)

# ipアドレスを取得
PCIP = socket.gethostbyname(socket.gethostname())
# print(Srcip) # 192.168.○○○.○○○
InFlg = 0

#### オプションの設定
try:
    while True:
        
        #プロトコルを選択
        if InFlg == 0:
            Proto =input("Protocol? [1:TCP or 2:UDP]:")
            if Proto == '1' or Proto == '2':
                InFlg += 1

        #サーバーモードかクライアントモードを選択
        if InFlg == 1:
            mode =input("mode? [1:Server or 2:Clients]:")
            if mode == '1' or mode == '2':
                InFlg += 1

        #ソースIPを指定、表示されたIPのままでOKならEnter
        if InFlg == 2:
            Sip=input(f"Source IP [{PCIP}]? or typing")
            if Sip == "":
                Src_ip = PCIP
                InFlg += 1
            else:
                Src_ip = Sip
                InFlg += 1
        
        #送信元ポートを指定
        if InFlg == 3:
            x = input("Source Port?[1-65536]:")
            if x != "":
                sp = int(x)
                if  1 <= sp <= 65536:
                    S_port = str(sp)
                    InFlg += 1
        
        #宛先IPを入力する
        if InFlg == 4 and mode == "2":
            dip =input("Destination IP?")
            if dip != "":
                Dest_ip = dip
                InFlg += 1
        elif InFlg == 4 and mode == "1":
            Dest_ip = ""
            D_port = ""
            break

        #宛先ポートを指定
        if InFlg == 5 and mode == "2":
            x=input("Destination Port?[1-65536]:")
            if x != "":
                dp=int(x)
                if  1 <=  dp <= 65536:
                    D_port = str(dp)
                    InFlg+=1

        if InFlg == 6:
            break
except KeyboardInterrupt:
    print('\n終了')
    sys.exit()


#=====================================TCPの処理==============================

#TCP/Clientモードの処理
if mode == "2" and Proto == "1":
    init_msg = "クライアントのコネクション情報\nSource_IP:" + Src_ip +  "\nSource_Port:" + S_port + "\nDest_IP:" + Dest_ip + "\nDest_port:" + D_port

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((Src_ip,int(S_port)))  # IPとポート番号を指定します
    s.connect((Dest_ip,int(D_port)))
    s.send(bytes(init_msg,'utf-8'))
    response = s.recv(1024)
    #print("[*]Received a response : {}".format(response))
    print(response.decode('utf-8'))
    
    try:
        while True:
            x =input(">>")

            #byeを入力した場合は終了する
            if x == "BYE":
                s.send(bytes(x,'utf-8'))
                s.close()
                time.sleep(1)
                break

            #CHANGEポートの処理
            elif x[:6] == "CHANGE":
                CHANGE_MSG = x.split()
                if len(CHANGE_MSG) == 2 and CHANGE_MSG[1].isdecimal() and 1 <= int(CHANGE_MSG[1]) <= 65536:
                    s.send(bytes(x,'utf-8'))
                    response = s.recv(1024)
                    print(">>",response.decode('utf-8'))
                    s.close()
                    break
                else:
                    print("!!ポート番号エラー")

            #pingを入力した場合はpingモードに移行1
            elif x == "ping":
                print("\n\nCTRL + C for escaping\n")
                try:
                    while True:
                        #送信メッセージにタイムスタンプを付与する
                        now = datetime.datetime.now(datetime.timezone.utc)
                        Send_MSG = "TCP recieved " + str(now.time())
                        s.send(bytes(Send_MSG,'utf-8'))

                        response = s.recv(1024)
                        now2 = datetime.datetime.now(datetime.timezone.utc)
                        delta = now2 - now
                        print(response.decode('utf-8'),delta.seconds , "." ,str(delta.microseconds//1000).zfill(3),"秒")
                        time.sleep(1)
                except KeyboardInterrupt:
                    pass
            
            #CONを入力した場合はコネクション情報を取得する
            elif x == "CON":
                s.send(bytes(x,'utf-8'))
                time.sleep(1)
                response = s.recv(1024)
                Send_MSG = "【ローカルコネクション情報】\nサーバーIPアドレス:\t" + str(Dest_ip) + "\nサーバー待ち受けport:\t" + str(D_port) + \
                "\nクライアントIPアドレス:\t" + str(Src_ip) + "\nクライアント送信元port:\t" + str(S_port) + \
                "\n\n======================================\n\n" +  response.decode('utf-8')
                print(Send_MSG)

            elif x == "CLOSE":
                s.send(bytes(x,'utf-8'))
                response = s.recv(1024)
                s.close()
                time.sleep(1)
                break

            #?を入力した場合はcommand help を表示
            elif x == "?":
                print(command_help)

            #それ以外はメッセージモードとして処理
            elif x != "":
                s.send(bytes(x,'utf-8'))
                response = s.recv(1024)
                print(">>",response.decode('utf-8'))
            
            Send_MSG =""
            response = ""

    except KeyboardInterrupt:
        s.send(bytes("BYE",'utf-8'))
        s.close()
        time.sleep(1)

#===========================================================================

#TCPサーバーモードの処理
if mode == "1" and Proto == "1":
    init_msg = "Source_IP:" + Src_ip + "\nSource_port:" + S_port
    ServerFlg = 0
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((Src_ip,int(S_port)))  # IPとポート番号を指定します
    s.listen(1)
    print("waiting for TCP connection...")
    clientsocket, address = s.accept()
    print(f"Connection from {address} has been established!")
    clientsocket.send(bytes("ack", 'utf-8'))
    
    client_data = clientsocket.recv(1024)
    print(client_data.decode('utf-8'))
    
    try:
        while True:
            client_data = clientsocket.recv(1024)
            print(client_data.decode('utf-8'))
            decode_data = client_data.decode('utf-8')

            #bye メッセージがきたら終了
            if decode_data == "BYE":
                print("ClientからByeが入力されました")
                ServerFlg = "1"
                time.sleep(1)
                break
            
            #CHANGEポートの処理
            elif decode_data[:6] == "CHANGE":
                change_port = decode_data.split()

                #引数があり、引数が数値文字列であり、1-65536の間であること
                if len(change_port) == 2 and change_port[1].isdecimal() and 1 <= int(change_port[1]) <= 65536:
                
                    #既存セッションの終了処理
                    Reply_MSG = "change server port to " + str(change_port[1])
                    clientsocket.send(bytes(Reply_MSG,'utf-8'))
                    #クライアント側からのcloseを待つ
                    time.sleep(1)

                    #新規待ち受けポートを作成
                    s = ""
                    S_port = str(change_port[1])
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    s.bind((Src_ip,int(S_port)))
                    s.listen(1)
                    print("waiting for connection",S_port)
                    clientsocket, address = s.accept()
                    clientsocket.send(bytes("ack", 'utf-8'))
                    client_data = clientsocket.recv(1024)
                    print(client_data.decode('utf-8'))
                    decode_data = ""

                else:
                    print(f">>",decode_data)
                    clientsocket.send(bytes(Reply_MSG,'utf-8'))
                
            #TCP recieved メッセージがきたらReplyを返す
            elif decode_data[:3] == "TCP":
                #now = datetime.datetime.now()
                Reply_MSG = "TCP Reply "
                clientsocket.send(bytes(Reply_MSG,'utf-8'))
            
            #CON メッセージがきた場合はサーバーのLocal情報を返す
            elif decode_data[:3] == "CON":
                Send_MSG = "【リモートコネクション情報】\nサーバーIPアドレス:\t" + str(Src_ip) + "\nサーバー待ち受けport:\t" + str(S_port) + \
                    "\nクライアントIPアドレス:\t" + str(address[0]) + "\nクライアント送信元port:\t" + str(address[1])
                clientsocket.send(bytes(Send_MSG,'utf-8'))

            #CLOSE メッセージが来た場合の処理
            elif decode_data == "CLOSE":
                print(">>connection close from clients")
                Reply_MSG = "MSG Recieved"
                clientsocket.send(bytes(Reply_MSG,'utf-8'))

                time.sleep(1)
                print("waiting for connection",S_port)
                clientsocket , address = s.accept()
                clientsocket.send(bytes("ack", 'utf-8'))
                client_data = clientsocket.recv(1024)
                print(client_data.decode('utf-8'))

            #その他のメッセージが来た場合は表示させる
            elif decode_data != "":
                #print(f">>",decode_data)
                Reply_MSG = "MSG Recieved"
                clientsocket.send(bytes(Reply_MSG,'utf-8'))
                decode_data = ""

            Send_MSG = ""
            Reply_MSG = ""

            if ServerFlg == "1":
                break
    except KeyboardInterrupt:
        s.close()
        sys.exit()



#=====================================UDPの処理==============================

#UDP/Clientモードの処理
if mode == "2" and Proto == "2":
    init_msg = "クライアントのコネクション情報\nSource_IP:" + Src_ip +  "\nSource_Port:" + S_port + "\nDest_IP:" + Dest_ip + "\nDest_port:" + D_port
    UDP_Dest = (Dest_ip,int(D_port))
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((Src_ip,int(S_port)))  # IPとポート番号を指定します
    s.sendto(bytes(init_msg,'utf-8'),UDP_Dest)
    response,UDP_Server = s.recvfrom(1024)
    #print("[*]Received a response : {}".format(response))
    print(response.decode('utf-8'))
    
    try:
        while True:
            x =input(">>")

            #byeを入力した場合は終了する
            if x == "BYE":
                s.sendto(bytes(x,'utf-8'),UDP_Dest)
                s.close()
                time.sleep(1)
                break

            #CHANGEポートの処理
            elif x[:6] == "CHANGE":
                CHANGE_MSG = x.split()
                if len(CHANGE_MSG) == 2 and CHANGE_MSG[1].isdecimal() and 1 <= int(CHANGE_MSG[1]) <= 65536:
                    s.sendto(bytes(x,'utf-8'),UDP_Dest)
                    response,UDP_Server = s.recvfrom(1024)
                    print(">>",response.decode('utf-8'))
                    s.close()
                    break
                else:
                    print("!!ポート番号エラー")

            #pingを入力した場合はpingモードに移行1
            elif x == "ping":
                print("\n\nCTRL + C for escaping\n")
                try:
                    while True:
                        #送信メッセージにタイムスタンプを付与する
                        now = datetime.datetime.now(datetime.timezone.utc)
                        Send_MSG = "TCP recieved " + str(now.time())
                        s.sendto(bytes(Send_MSG,'utf-8'),UDP_Dest)

                        response,UDP_Server = s.recvfrom(1024)
                        now2 = datetime.datetime.now(datetime.timezone.utc)
                        delta = now2 - now
                        print(response.decode('utf-8'),delta.seconds , "." ,str(delta.microseconds//1000).zfill(3),"秒")
                        time.sleep(1)
                except KeyboardInterrupt:
                    pass
            
            #CONを入力した場合はコネクション情報を取得する
            elif x == "CON":
                s.sendto(bytes(x,'utf-8'),UDP_Dest)
                time.sleep(1)
                response,UDP_Server = s.recvfrom(1024)
                Send_MSG = "【ローカルコネクション情報】\nサーバーIPアドレス:\t" + str(Dest_ip) + "\nサーバー待ち受けport:\t" + str(D_port) + \
                "\nクライアントIPアドレス:\t" + str(Src_ip) + "\nクライアント送信元port:\t" + str(S_port) + \
                "\n\n======================================\n\n" +  response.decode('utf-8')
                print(Send_MSG)

            elif x == "CLOSE":
                s.sendto(bytes(x,'utf-8'),UDP_Dest)
                response,UDP_Server = s.recvfrom(1024)
                s.close()
                time.sleep(1)
                break

            #?を入力した場合はcommand help を表示
            elif x == "?":
                print(command_help)

            #それ以外はメッセージモードとして処理
            elif x != "":
                s.sendto(bytes(x,'utf-8'),UDP_Dest)
                response,UDP_Server = s.recvfrom(1024)
                print(">>",response.decode('utf-8'))
            
            Send_MSG =""
            response = ""

    except KeyboardInterrupt:
        s.sendto(bytes("BYE",'utf-8'),UDP_Dest)
        s.close()
        time.sleep(1)

#===========================================================================

#UDPサーバーモードの処理
if mode == "1" and Proto == "2":
    init_msg = "Source_IP:" + Src_ip + "\nSource_port:" + S_port
    ServerFlg = 0
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((Src_ip,int(S_port)))  # IPとポート番号を指定します
    print("waiting for UDP connection...")
    client_data,UDP_Dest = s.recvfrom(1024)
    
    print(f"Connection from {UDP_Dest[0],UDP_Dest[1]} has been established!")
    print(client_data.decode('utf-8'))
    s.sendto(bytes("ack", 'utf-8'),UDP_Dest)
    
    
    try:
        while True:
            client_data,UDP_Dest = s.recvfrom(1024)
            print(client_data.decode('utf-8'))
            decode_data = client_data.decode('utf-8')

            #bye メッセージがきたら終了
            if decode_data == "BYE":
                print("ClientからByeが入力されました")
                ServerFlg = "1"
                time.sleep(1)
                break
            
            #CHANGEポートの処理
            elif decode_data[:6] == "CHANGE":
                change_port = decode_data.split()

                #引数があり、引数が数値文字列であり、1-65536の間であること
                if len(change_port) == 2 and change_port[1].isdecimal() and 1 <= int(change_port[1]) <= 65536:
                
                    #既存セッションの終了処理
                    Reply_MSG = "change server port to " + str(change_port[1])
                    s.sendto(bytes(Reply_MSG,'utf-8'),UDP_Dest)
                    #クライアント側からのcloseを待つ
                    time.sleep(1)

                    #新規待ち受けポートを作成
                    s = ""
                    S_port = str(change_port[1])
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    s.bind((Src_ip,int(S_port)))
                    print("waiting for connection",S_port)
                    client_data,UDP_Dest = s.recvfrom(1024)
                    print(client_data.decode('utf-8'))
                    s.sendto(bytes("ack", 'utf-8'),UDP_Dest)
                    decode_data = ""

                else:
                    print(f">>",decode_data)
                    s.sendto(bytes(Reply_MSG,'utf-8'),UDP_Dest)
                
            #TCP recieved メッセージがきたらReplyを返す
            elif decode_data[:3] == "UDP":
                #now = datetime.datetime.now()
                Reply_MSG = "UDP Reply "
                s.sendto(bytes(Reply_MSG,'utf-8'),UDP_Dest)
            
            #CON メッセージがきた場合はサーバーのLocal情報を返す
            elif decode_data[:3] == "CON":
                Send_MSG = "【リモートコネクション情報】\nサーバーIPアドレス:\t" + str(Src_ip) + "\nサーバー待ち受けport:\t" + str(S_port) + \
                    "\nクライアントIPアドレス:\t" + str(UDP_Dest[0]) + "\nクライアント送信元port:\t" + str(UDP_Dest[1])
                s.sendto(bytes(Send_MSG,'utf-8'),UDP_Dest)

            #CLOSE メッセージが来た場合の処理
            elif decode_data == "CLOSE":
                print(">>connection close from clients")
                Reply_MSG = "MSG Recieved"
                s.sendto(bytes(Reply_MSG,'utf-8'),UDP_Dest)

                time.sleep(1)
                print("waiting for connection",S_port)
                client_data,UDP_Dest = s.recvfrom(1024)
                print(client_data.decode('utf-8'))
                s.sendto(bytes("ack", 'utf-8'),UDP_Dest)

            #その他のメッセージが来た場合は表示させる
            elif decode_data != "":
                #print(f">>",decode_data)
                Reply_MSG = "MSG Recieved"
                s.sendto(bytes(Reply_MSG,'utf-8'),UDP_Dest)
                decode_data = ""

            Send_MSG = ""
            Reply_MSG = ""

            if ServerFlg == "1":
                break
    except KeyboardInterrupt:
        s.close()
        sys.exit()