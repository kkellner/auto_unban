# auto_unban
Home Assistant HACS plugin for automatically removing IP from ban list

WARNING: This is a work-in-progress


NOTE: Only the `never_ban` feature is currently implemented.

# Configuration
Example config to be added to `configuration.yaml`

```yaml
auto_unban:
    max_time: 600   # Maximum time to ban auto_unban IPs (not implemented yet)
    never_ban:
        - 172.20.0.60
        - 172.20.0.61
        - 127.0.0.1
    auto_unban:  # Not implemented yet
        - 172.20.0.0/24
```

