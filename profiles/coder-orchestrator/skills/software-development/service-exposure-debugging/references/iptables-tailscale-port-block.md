# Reproduction: port DROP with Tailscale loophole

## Symptom
- `ss` shows `0.0.0.0:<port>` LISTEN.
- `curl` from the same host to 127.0.0.1:<port> and `<local-ip>:<port>` both timeout.
- `curl` succeeds only when launched via a proxy/tunnel that arrives on `tailscale0`.

## Root cause
Two input rules work together:
```
-A INPUT -i tailscale0 -p tcp --dport <PORT> -j ACCEPT
-A INPUT -p tcp --dport <PORT> -j DROP
```
Local-originated TCP never enters on `tailscale0`, so it hits the unconditional DROP.

## Verification commands
```bash
iptables-save | grep -- '-p tcp --dport <PORT>'
ip route get 127.0.0.1
ip route get <local-ip>
ss -tlnp | grep <PORT>
```

## Fix options
1. Add a loopback exception before the DROP:
   `iptables -I INPUT 3 -i lo -p tcp --dport <PORT> -j ACCEPT`
2. If the service does not need external access, bind loopback-only:
   `--host 127.0.0.1`
3. If external access is required, expose the service through nginx/proxy behind existing allow rules instead of removing the DROP.

## Caveats
- `--noproxy '*'` does not bypass iptables; the test above still fails.
- These rules are ephemeral on some boxes unless saved; persist only when the user wants port 9119 reachable without tailscale.
- Tailscale’s own filter chain (`ts-input`) may later RETURN or DROP non-tailscale 100.x traffic; don’t assume opening one port fixes whole-subnet access.
