import argparse
import socket
import threading
import queue
import sys
import json
import csv
from datetime import datetime
from typing import List, Dict, Optional

# Fila para threads pegarem portas a escanear
port_queue = queue.Queue()
# Lista para armazenar resultados (protegida por lock)
results_lock = threading.Lock()
results = []  # cada item: {"port": porta, "protocol": "tcp"/"udp", "state": "open"/"closed", "service": banner (opcional)}

# Semáforo para limitar threads simultâneas (opcional, mas já controlado pela queue)
def tcp_scan(host: str, port: int, timeout: float, grab_banner: bool) -> Dict:
    """Escaneia uma porta TCP e retorna dicionário com resultado."""
    result = {"port": port, "protocol": "tcp", "state": "closed", "service": None}
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        # Tenta conexão
        code = sock.connect_ex((host, port))
        if code == 0:
            result["state"] = "open"
            if grab_banner:
                # Banner grabbing: envia algo genérico e recebe resposta
                try:
                    sock.send(b"HEAD / HTTP/1.0\r\n\r\n")  # Para serviços HTTP
                    banner = sock.recv(1024).decode().strip()
                    result["service"] = banner[:50]  # Limita tamanho
                except:
                    # Se falhar, tenta apenas receber o que vier
                    try:
                        banner = sock.recv(1024).decode().strip()
                        result["service"] = banner[:50]
                    except:
                        result["service"] = "unknown"
        sock.close()
    except Exception:
        pass
    return result

def udp_scan(host: str, port: int, timeout: float) -> Dict:
    """Escaneia uma porta UDP (simples: envia pacote vazio e espera ICMP unreachable)."""
    result = {"port": port, "protocol": "udp", "state": "closed", "service": None}
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(timeout)
        # Envia um pacote vazio (ou pode enviar algo específico)
        sock.sendto(b"", (host, port))
        # Tenta receber resposta (se houver, pode estar aberta)
        try:
            data, addr = sock.recvfrom(1024)
            result["state"] = "open"
            # Se recebeu algo, pode ser banner (mas UDP é sem conexão)
            if data:
                result["service"] = data.decode(errors='ignore')[:50]
        except socket.timeout:
            # Timeout: porta pode estar aberta ou filtrada (método impreciso)
            # Na prática, muitas portas UDP abertas não respondem, então consideramos como "open|filtered"
            result["state"] = "open|filtered"
        sock.close()
    except Exception:
        pass
    return result

def worker(host: str, timeout: float, scan_type: str, grab_banner: bool):
    """Função executada por cada thread."""
    while True:
        try:
            port = port_queue.get_nowait()
        except queue.Empty:
            break
        if scan_type == "tcp" or scan_type == "both":
            res = tcp_scan(host, port, timeout, grab_banner)
            with results_lock:
                if res["state"] != "closed":
                    results.append(res)
        if scan_type == "udp" or scan_type == "both":
            res = udp_scan(host, port, timeout)
            with results_lock:
                if res["state"] != "closed":
                    results.append(res)
        port_queue.task_done()

def parse_ports(port_str: str) -> List[int]:
    """Interpreta string de portas: '80', '1-1024', '22,80,443'."""
    ports = []
    for part in port_str.split(','):
        if '-' in part:
            start, end = part.split('-')
            ports.extend(range(int(start), int(end)+1))
        else:
            ports.append(int(part))
    return ports

def export_results(results: List[Dict], filename: str, format: str):
    """Exporta resultados para JSON ou CSV."""
    if format == "json":
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
    elif format == "csv":
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["port", "protocol", "state", "service"])
            writer.writeheader()
            writer.writerows(results)

def main():
    parser = argparse.ArgumentParser(description="Port Scanner Avançado")
    parser.add_argument("target", help="IP ou hostname alvo")
    parser.add_argument("-p", "--ports", default="1-1024", help="Portas a escanear (ex: '80', '1-1024', '22,80,443')")
    parser.add_argument("-t", "--timeout", type=float, default=1.0, help="Timeout em segundos (padrão: 1.0)")
    parser.add_argument("-T", "--threads", type=int, default=10, help="Número de threads (padrão: 10)")
    parser.add_argument("--type", choices=["tcp", "udp", "both"], default="tcp", help="Tipo de escaneamento")
    parser.add_argument("-b", "--banner", action="store_true", help="Tenta obter banner (apenas TCP)")
    parser.add_argument("-o", "--output", help="Arquivo de saída (formato definido por --format)")
    parser.add_argument("--format", choices=["json", "csv"], default="json", help="Formato de saída")
    
    args = parser.parse_args()

    # Resolve hostname
    try:
        ip = socket.gethostbyname(args.target)
    except socket.gaierror:
        print("Erro: Não foi possível resolver o hostname.")
        sys.exit(1)

    # Parse portas
    try:
        ports = parse_ports(args.ports)
    except ValueError:
        print("Erro: Formato de portas inválido.")
        sys.exit(1)

    print("=" * 60)
    print("            Port Scanner Avançado")
    print("=" * 60)
    print(f"Alvo: {args.target} ({ip})")
    print(f"Portas: {args.ports} ({len(ports)} portas)")
    print(f"Tipo: {args.type}")
    print(f"Timeout: {args.timeout}s")
    print(f"Threads: {args.threads}")
    if args.banner:
        print("Banner grabbing: ativado")
    print("-" * 60)
    print("Escaneando... (pressione Ctrl+C para interromper)")
    start_time = datetime.now()

    # Preenche fila com portas
    for port in ports:
        port_queue.put(port)

    # Cria e inicia threads
    threads = []
    for _ in range(args.threads):
        t = threading.Thread(target=worker, args=(ip, args.timeout, args.type, args.banner))
        t.start()
        threads.append(t)

    # Aguarda conclusão
    try:
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        print("\n\nEscaneamento interrompido pelo usuário.")
        # Para novas threads (opcional, mas não é trivial interromper sockets)
        sys.exit(0)

    end_time = datetime.now()
    duration = end_time - start_time

    print("\n" + "-" * 60)
    print("Resultados:")
    if results:
        for res in sorted(results, key=lambda x: (x["protocol"], x["port"])):
            service = f" - {res['service']}" if res['service'] else ""
            print(f"Porta {res['port']}/{res['protocol']}: {res['state']}{service}")
    else:
        print("Nenhuma porta aberta encontrada.")
    print("-" * 60)
    print(f"Tempo total: {duration.total_seconds():.2f} segundos")
    print(f"Portas abertas encontradas: {len(results)}")

    # Exporta se solicitado
    if args.output:
        export_results(results, args.output, args.format)
        print(f"Resultados exportados para {args.output}")

if __name__ == "__main__":
    main()