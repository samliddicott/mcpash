#!/usr/bin/env bash
# DIFF_BASELINE: bash
# Coverage: bash redirection extensions (&>, &>>, {varname}>...)

set +e

tmp="${TMPDIR:-/tmp}/mctash-redir-ext-$$"
: > "$tmp"

echo both &> "$tmp"
cat "$tmp"

echo append1 &>> "$tmp"
cat "$tmp"

exec {fd}>"$tmp"
echo named-fd >&"$fd"
exec {fd}>&-
cat "$tmp"

tcp_port_file="${TMPDIR:-/tmp}/mctash-redir-ext-tcp-port-$$"
tcp_out="${TMPDIR:-/tmp}/mctash-redir-ext-tcp-out-$$"
: > "$tcp_port_file"
: > "$tcp_out"
python3 -c 'import socket,sys; pf,of=sys.argv[1],sys.argv[2]; s=socket.socket(socket.AF_INET,socket.SOCK_STREAM); s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1); s.bind(("127.0.0.1",0)); s.listen(1); s.settimeout(5.0); open(pf,"w",encoding="utf-8").write(str(s.getsockname()[1])); c,_=s.accept(); d=c.recv(4096); open(of,"wb").write(d); c.close(); s.close()' "$tcp_port_file" "$tcp_out" &
tcp_srv=$!
for _ in 1 2 3 4 5 6 7 8 9 10; do
  [ -s "$tcp_port_file" ] && break
  sleep 0.1
done
tcp_port="$(cat "$tcp_port_file")"
printf 'tcp-msg\n' > "/dev/tcp/127.0.0.1/$tcp_port"
wait "$tcp_srv"
cat "$tcp_out"

udp_port_file="${TMPDIR:-/tmp}/mctash-redir-ext-udp-port-$$"
udp_out="${TMPDIR:-/tmp}/mctash-redir-ext-udp-out-$$"
: > "$udp_port_file"
: > "$udp_out"
python3 -c 'import socket,sys; pf,of=sys.argv[1],sys.argv[2]; s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM); s.bind(("127.0.0.1",0)); s.settimeout(5.0); open(pf,"w",encoding="utf-8").write(str(s.getsockname()[1])); d,_=s.recvfrom(4096); open(of,"wb").write(d); s.close()' "$udp_port_file" "$udp_out" &
udp_srv=$!
for _ in 1 2 3 4 5 6 7 8 9 10; do
  [ -s "$udp_port_file" ] && break
  sleep 0.1
done
udp_port="$(cat "$udp_port_file")"
printf 'udp-msg\n' > "/dev/udp/127.0.0.1/$udp_port"
wait "$udp_srv"
cat "$udp_out"

rm -f "$tmp"
rm -f "$tcp_port_file" "$tcp_out" "$udp_port_file" "$udp_out"
