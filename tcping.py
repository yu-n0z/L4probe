
import socket


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
            sp = int(input("Source Port?[1-65536]:"))
            
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
            dp=int(input("Destination Port?[1-65536]:"))
            if  1 <=  dp <= 65536:
                D_port = dp
                InFlg+=1

        if InFlg == 5:
            break
except KeyboardInterrupt:
    print('\n終了')
    sys.exit()

print(f"{Src_ip}\n{S_port}\n{Dest_ip}\n{D_port}")


