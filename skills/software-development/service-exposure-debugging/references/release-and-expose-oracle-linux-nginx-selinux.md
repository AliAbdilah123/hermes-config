# Oracle Linux 9 nginx + SELinux fix checklist
- Confirm SELinux mode: `getenforce` -> if `Enforcing`, either set bools or use `/usr/share/nginx/html`.
- Allow nginx to reach localhost upstreams: `sudo setsebool -P httpd_can_network_connect on`
- Allow nginx to traverse home dirs (rarely needed): `chmod o+x /home /home/opc /home/opc/projects /home/opc/projects/<name>`
- Preferred: deploy static assets to `/usr/share/nginx/html/<project>/` owned by `nginx:nginx`.
- Reload: `sudo nginx -t && sudo nginx -s reload`
