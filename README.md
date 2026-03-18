# 🔍 Port Scanner Avançado

[![Python](https://img.shields.io/badge/Python-3.6%2B-blue)](https://python.org)

Um scanner de portas TCP/UDP desenvolvido em Python, com suporte a **multithreading**, **banner grabbing**, **exportação de resultados** e argumentos de linha de comando flexíveis. Ideal para aprendizado de redes e segurança, ou como base para ferramentas mais complexas.

> ⚠️ **Aviso:** Use apenas em sistemas que você possui autorização para testar.

---

## 🧠 Sobre o Projeto

Este projeto faz parte do meu portfólio e demonstra na prática como funciona um scanner de portas. Ele tenta estabelecer conexões TCP ou enviar pacotes UDP para um alvo (IP ou domínio) em um intervalo de portas definido pelo usuário, identificando quais estão acessíveis e, opcionalmente, coletando banners para identificar serviços.

A ferramenta é **didática e extensível**: usa threads para agilizar o escaneamento, suporta UDP (com limitações), e pode exportar resultados em JSON ou CSV.

---

## ⚙️ Funcionalidades

- ✅ Escaneamento **TCP** (conexão completa) e **UDP** (envio de pacote vazio).
- ✅ **Multithreading** – várias portas simultaneamente, com controle do número de threads.
- ✅ **Banner grabbing** para TCP – tenta obter a resposta inicial do serviço.
- ✅ **Argumentos de linha de comando** flexíveis (portas, timeout, tipo, etc.).
- ✅ Suporte a intervalos e listas de portas (ex: `1-1024` ou `22,80,443`).
- ✅ **Exportação** para JSON ou CSV.
- ✅ Resolução automática de hostname para IP.
- ✅ Tratamento de interrupção (Ctrl+C) e timeouts.

---

## 📦 Instalação

### Pré-requisitos
- Python 3.6 ou superior.

### Passos

1. Clone o repositório:
   ```bash
   git clone https://github.com/Acacio-Gabriel/port-scanner-adv.git
   cd port-scanner-avancado
---

## 🚀 Como usar
```bash
python port-scanner-adv.py <alvo> [opções]
```
### Opções disponiveis
|Argumento|Descrição|
|---------|---------|
|`target`   |IP ou Hostname do alvo (Obrigaatorio)|
|`-p,--ports`|Portas a escanear|
|`-t, --timeout`|Timeout em segundos (padrão 1.0s)|
|`-T,--threads`|Número de threads | 
|`--type`| Tipo de escaneamento: `tcp, udp ou both` (padrão: `tcp`)|
| `-b, --banner`|Ativa o banner grapping (somente TCP)
|`-o, --output`|Arquivo de saida exporta resultados|
|`--format`|Formato do arquivo exportado: `json ou csv`(padrão `json`)|

---

## 🖥️ Exemplos de uso
### Escaneamento TCP básico (portas 1-1024)
```bash
python port-scanner-adv.py scanme.nmap.org
```
### Escaneamento rápido com 50 threads e timeout menor
```bash
python port-scanner-adv.py scanme.nmap.org -p 1-1000 -T 50 -t 0.5
```
 ### Escaneamento UDP + TCP, com banner grabbing
 ```bash
python port-scanner-adv.py scanme.nmap.org --type both -b
```
### Exportar para JSON
```bash
python port-scanner-adv.py scanme.nmap.org -p 22,80,443 -o resultado.json --format json
```
### Exportar para CSV
```bash
python port.scanner-adv.py scanme.nmap.org -p 1-100 -o resultado.csv --format csv
```
### Exemplo de saida de terminal
```bash
============================================================
            Port Scanner Avançado
============================================================
Alvo: scanme.nmap.org (45.33.32.156)
Portas: 1-100 (100 portas)
Tipo: tcp
Timeout: 1.0s
Threads: 10
Banner grabbing: ativado
------------------------------------------------------------
Escaneando... (pressione Ctrl+C para interromper)

------------------------------------------------------------
Resultados:
Porta 22/tcp: open - SSH-2.0-OpenSSH_6.6.1p1 Ubuntu-2ubuntu2.13
Porta 80/tcp: open - HTTP/1.1 200 OK
Porta 443/tcp: open - <html>...
------------------------------------------------------------
Tempo total: 2.34 segundos
Portas abertas encontradas: 3
Resultados exportados para resultado.json
```
---

## 📝 Explicação do Código
O código está organizado em funções principais:
- `tcp_scan(host, port, timeout, grab_banner)`
Cria um socket TCP, tenta conectar e, se bem‑sucedido, coleta banner (se solicitado).
- `udp_scan(host, port, timeout)`
Envia um pacote vazio via UDP e espera resposta; se timeout ocorrer, classifica como open|filtered (método impreciso, mas comum).
- `worker()`
Função executada por cada thread: retira portas da fila e chama as funções de scan de acordo com o tipo escolhido.
- `parse_ports(port_str)`
Interpreta strings como "1-1024" ou "22,80,443" e gera uma lista de inteiros.
- `export_results()`
Salva os resultados em JSON ou CSV.
- `main()`
Processa argumentos, resolve o alvo, inicia as threads e exibe/exporta resultados.
> O uso de threads com uma fila (`queue.Queue`) garante que as portas sejam distribuídas de forma eficiente, enquanto o lock protege a lista de resultados contra acesso concorrente.
---

## 🌐 Conceitos de Redes
1. Socket: Interface de comunicação bidirecional. Usamos socket.AF_INET (IPv4) e SOCK_STREAM (TCP) ou SOCK_DGRAM (UDP).
2. Porta: Número que identifica um serviço no host. Portas < 1024 são "well‑known".
3. TCP: Protocolo orientado à conexão. O scanner tenta completar o three‑way handshake; se conseguir, a porta está aberta.
4. UDP: Protocolo sem conexão. Enviamos um pacote e aguardamos resposta ou erro ICMP (traduzido em timeout).
5. Timeout: Evita que o programa trave ao tentar conectar em portas que não respondem.
6. Banner grabbing: Após estabelecer conexão TCP, enviamos uma requisição genérica (ex: HEAD / HTTP/1.0) e capturamos a resposta inicial, que muitas vezes revela o serviço e versão.
7. Multithreading: Permite escanear várias portas simultaneamente, reduzindo drasticamente o tempo total.
---

## ⚖️ Aviso Legal
**Este software é fornecido apenas para fins educacionais**. O uso não autorizado de scanners de porta em sistemas de terceiros pode violar leis locais e políticas de uso aceitável. O autor não se responsabiliza por qualquer uso indevido ou danos causados pela ferramenta


