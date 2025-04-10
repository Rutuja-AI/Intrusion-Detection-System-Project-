from scapy.all import IP, TCP, send

ip = "127.0.0.1"  # same as where you got blocked

pkt = IP(dst=ip) / TCP(sport=9999, dport=9999, flags="S")
send(pkt, verbose=0)

print("🧙‍♂️ Magic unblock packet sent!")
