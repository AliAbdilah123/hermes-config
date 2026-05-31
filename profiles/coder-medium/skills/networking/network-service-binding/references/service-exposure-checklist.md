# Network Service Exposure Checklist

## Sample diagnostic output

```
ss -tlnp | grep -E '9119|tailscale'
LISTEN 0 2048 127.0.0.1:9119 0.0.0.0:* users:(("hermes",pid=99162,fd=13))

tailscale status --json | python3 -c "import sys,json; d=json.load(sys.stdin); print('Tailscale IP:', d.get('Self',{}).get('TailscaleIPs',[]), 'Self:', d.get('Self',{}).get('HostName'), 'State:', d.get('Self',{}).get('Online'))"
Tailscale IP: ['100.81.145.98', 'fd7a:115c:a1e0::9532:9163'] Self: instance-20260530-2033 State: True
```

If you see `127.0.0.1:<PORT>` but Tailscale is online, the service must be reconfigured to `0.0.0.0`.

## Environment notes

- Oracle Linux 9
- nginx 1.20.1 present
- SELinux Enforcing by default
- Home dirs default to `700/drwx------`
- Backend API commonly on `127.0.0.1:8080` before nginx proxy
- Public project URLs at `http://168.110.196.49/projects/<project>` via nginx
