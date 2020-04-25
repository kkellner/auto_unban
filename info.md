# Description

Allow more control over the `ip_ban_enabled` feature of Home Assistant.
You can configure home assistant with `ip_ban_enabled: true` as shown below.

```yaml
http:
  base_url: https://my-hass.my-domain.com
  ip_ban_enabled: true
  login_attempts_threshold: 3
```

This configuration will ban any IP that has 3 failed attempts to authenticate.  The list of
banned IPs can be found in `ip_bans.yaml` in the root of the config directory.  There are
use-cases where you either never want to ban some IPs, or want to auto-remove the banned IP
after a specified amount of time.  This plugin allows for these enhanced ban configurations.

WARNING: only the `never_ban` feature is currently implemented at this time.


## Features
* Specify IPs or Networks that should never be banned.
* (TODO) Automatically removing IP from ban list


## Getting Started

Add entries to the `configurqtion.yaml` as shown in the [Configuration] section



## Configuration

Example config to be added to `configuration.yaml`

```yaml
unban:
    max_time: 600   # Maximum time to ban auto_unban IPs (not implemented yet)
    never_ban:
        - 172.20.0.60
        - 172.20.0.61
        - 127.0.0.1
    auto_unban:  # Not implemented yet
        - 172.20.0.0/24
```
