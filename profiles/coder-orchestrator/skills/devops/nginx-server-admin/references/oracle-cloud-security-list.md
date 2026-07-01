# Oracle Cloud Security List — Opening a Port

The OCI Security List is a network-level firewall configured in the Oracle Cloud Console. It cannot be modified from the server terminal. If `curl localhost:<port>` works but `curl 168.110.213.104:<port>` times out, the Security List is blocking the port.

## Steps to Open a Port (e.g. 443 for HTTPS)

1. Go to **https://cloud.oracle.com** → **Compute → Instances**
2. Click the instance (hostname pattern: `instance-YYYYMMDD-NNNN`)
3. In the instance details page, scroll to the **VCN** section → click the VCN link
4. In the VCN page, left sidebar under **Resources** → click **Security Lists**
5. Click the security list used by the instance (usually `Default Security List for <vcn-name>`)
6. Click **Add Ingress Rules**:
   - **Source Type:** CIDR
   - **Source CIDR:** `0.0.0.0/0`
   - **IP Protocol:** TCP
   - **Destination Port Range:** `<port>` (e.g. `443`)
   - **Description:** `HTTPS` (or whatever is appropriate)
7. Click **Add Ingress Rule**

The rule takes effect immediately — no server-side action needed.

## Verification

After adding the rule, test from the server:

```bash
curl -k https://168.110.213.104/health
# Should return "OK" (for self-signed, use -k to skip verification)
```

If it still times out, also check:
- **NSG (Network Security Group)**: if the subnet uses NSGs in addition to security lists, the NSG must also allow the port. Check VCN → Network Security Groups.
- **iptables**: `sudo iptables -L INPUT -n | grep <port>` — Oracle Cloud images sometimes have iptables rules that supplement ufw.

## Currently Open Ports (as of 2026-06-30)

| Port | Protocol | Purpose |
|------|----------|---------|
| 22   | TCP      | SSH     |
| 80   | TCP      | HTTP (nginx) |
| 443  | TCP      | HTTPS (nginx) — ufw opened, **OCI Security List rule NOT yet confirmed** |

Port 443 was opened in ufw (`sudo ufw allow 443/tcp`) on 2026-06-30. The user was instructed to add the corresponding OCI Security List ingress rule but has not yet confirmed doing so. If `curl -k https://168.110.213.104/health` times out but `curl -k https://localhost/health` works, the OCI rule is still missing.
