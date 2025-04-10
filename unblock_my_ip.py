from scapy.all import IP, TCP, send

my_ip = "127.0.0.1"

pkt = IP(dst=my_ip)/TCP(dport=9999, sport=9999, flags="S")
send(pkt)

print("🧙‍♀️ Sent magic unblock packet.")
