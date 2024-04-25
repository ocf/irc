from pathlib import Path

import yaml
from transpire.resources import Deployment
from transpire.types import Image
from transpire.utils import get_image_tag, get_versions

name = "ergo"


def images():
    yield Image(name="gamja", path=Path("/"), target="gamja")
    yield Image(name="sopel", path=Path("/"), target="sopel")


def objects():
    version = get_versions(__file__)[name]["version"]
    ip_sharing_hash = "2ec8f273ced93e06"
    server_dns = "irc.ocf.berkeley.edu"

    # ircd.motd
    ergo_motd = "Welcome to the OCF IRC network!"

    # ircd.yaml
    ergo_config = {
        "network": {"name": "OCF"},
        "server": {
            "name": server_dns,
            "listeners": {
                "127.0.0.1:6667": None,
                "[::1]:6667": None,
                "[::]:6697": {
                    "tls": {"cert": "/etc/ssl/server_certs/tls.crt", "key": "/etc/ssl/server_certs/tls.key"},
                    "proxy": False,
                    "min-tls-version": 1.2,
                },
                "[::]:8097": {
                    "websocket": True,
                    "tls": {"cert": "/etc/ssl/server_certs/tls.crt", "key": "/etc/ssl/server_certs/tls.key"},
                },
            },
            "unix-bind-mode": 511,
            "tor-listeners": {
                "require-sasl": False,
                "vhost": "tor-network.onion",
                "max-connections": 64,
                "throttle-duration": "10m",
                "max-connections-per-duration": 64,
            },
            "sts": {
                "enabled": True,
                "duration": "1mo2d5m",
                "port": 6697,
                "preload": True,
            },
            "websockets": {"allowed-origins": [f"https://{server_dns}"]},
            "casemapping": "ascii",
            "enforce-utf8": True,
            "lookup-hostnames": False,
            "forward-confirm-hostnames": True,
            "check-ident": False,
            "coerce-ident": "~u",
            "motd": "ircd.motd",
            "motd-formatting": True,
            "relaymsg": {
                "enabled": True,
                "separators": "/",
                "available-to-chanops": True,
            },
            "proxy-allowed-from": ["localhost"],
            "webirc": [
                {
                    "hosts": ["localhost"],
                    "certfp": "370fa3d1e64cfa5947255be412af899c8783c26d57e4ca334d01f458c55848e2",
                }
            ],
            "max-sendq": "96k",
            "compatibility": {
                "force-trailing": True,
                "send-unprefixed-sasl": True,
                "allow-truncation": False,
            },
            "ip-limits": {
                "count": True,
                "max-concurrent-connections": 16,
                "throttle": True,
                "window": "10m",
                "max-connections-per-window": 32,
                "cidr-len-ipv4": 32,
                "cidr-len-ipv6": 64,
                "exempted": [
                    "localhost",
                    "169.229.226.0/24",
                    "2607:f140:8801::/64",
                    "2607:f140:8800::/48",
                ],
                "custom-limits": None,
            },
            "ip-check-script": {
                "enabled": False,
                "command": "/usr/local/bin/check-ip-ban",
                "args": [],
                "timeout": "9s",
                "kill-timeout": "1s",
                "max-concurrency": 64,
                "exempt-sasl": False,
            },
            "ip-cloaking": {
                "enabled": True,
                "enabled-for-always-on": True,
                "netname": server_dns,
                "cidr-len-ipv4": 32,
                "cidr-len-ipv6": 64,
                "num-bits": 64,
            },
            "secure-nets": None,
            "suppress-lusers": False,
        },
        "accounts": {
            "authentication-enabled": True,
            "registration": {
                "enabled": False,
                "allow-before-connect": True,
                "throttling": {"enabled": True, "duration": "10m", "max-attempts": 30},
                "bcrypt-cost": 4,
                "verify-timeout": "32h",
                "email-verification": {
                    "enabled": False,
                    "sender": "admin@my.network",
                    "require-tls": True,
                    "helo-domain": "my.network",
                    "address-blacklist": None,
                    "address-blacklist-syntax": "glob",
                    "timeout": "60s",
                    "password-reset": {
                        "enabled": False,
                        "cooldown": "1h",
                        "timeout": "1d",
                    },
                },
            },
            "login-throttling": {"enabled": True, "duration": "1m", "max-attempts": 3},
            "skip-server-password": False,
            "login-via-pass-command": True,
            "advertise-scram": True,
            "require-sasl": {"enabled": False, "exempted": ["localhost"]},
            "nick-reservation": {
                "enabled": True,
                "additional-nick-limit": 0,
                "method": "strict",
                "allow-custom-enforcement": False,
                "guest-nickname-format": "Guest-*",
                "force-guest-format": False,
                "force-nick-equals-account": True,
                "forbid-anonymous-nick-changes": False,
            },
            "multiclient": {
                "enabled": True,
                "allowed-by-default": True,
                "always-on": "opt-in",
                "auto-away": "opt-in",
            },
            "vhosts": {
                "enabled": True,
                "max-length": 64,
                "valid-regexp": "^[0-9A-Za-z.\\-_/]+$",
            },
            "default-user-modes": "+i",
            "auth-script": {
                "enabled": False,
                "command": "/usr/local/bin/authenticate-irc-user",
                "args": [],
                "autocreate": True,
                "timeout": "9s",
                "kill-timeout": "1s",
                "max-concurrency": 64,
            },
            "oauth2": {
                "enabled": True,
                "autocreate": True,
                "introspection-url": "https://idm.ocf.berkeley.edu/realms/ocf/protocol/openid-connect/token/introspect",
                "introspection-timeout": "10s",
                "client-id": "ergo",
                # Set via ERGO__ACCOUNTS__OAUTH2__CLIENT_SECRET
                # "client-secret": ""
            },
        },
        "channels": {
            "default-modes": "+ntC",
            "max-channels-per-client": 100,
            "operator-only-creation": False,
            "registration": {
                "enabled": True,
                "operator-only": True,
                "max-channels-per-account": 15,
            },
            "list-delay": "0s",
            "invite-expiration": "24h",
        },
        "oper-classes": {
            "chat-moderator": {
                "title": "Chat Moderator",
                "capabilities": [
                    "kill",
                    "ban",
                    "nofakelag",
                    "relaymsg",
                    "vhosts",
                    "sajoin",
                    "samode",
                    "snomasks",
                    "roleplay",
                ],
            },
            "server-admin": {
                "title": "Server Admin",
                "extends": "chat-moderator",
                "capabilities": [
                    "rehash",
                    "accreg",
                    "chanreg",
                    "history",
                    "defcon",
                    "massmessage",
                ],
            },
        },
        "opers": {
            "njha": {
                "class": "server-admin",
                "whois-line": "2020-2024 OCF Root Staff",
                "certfp": "37:0F:A3:D1:E6:4C:FA:59:47:25:5B:E4:12:AF:89:9C:87:83:C2:6D:57:E4:CA:33:4D:01:F4:58:C5:58:48:E2",
                "hidden": True,
                "auto": True,
            },
            "oliverni": {
                "class": "server-admin",
                "whois-line": "2020-2024 OCF Root Staff",
                "certfp": "5B:B7:F9:C7:AF:13:D7:46:A2:86:2B:88:C0:42:E9:F2:EF:D3:50:ED:3D:0C:F0:4C:DF:C1:D9:14:AE:D6:16:FA",
                "hidden": True,
                "auto": True,
            },
        },
        "logging": [{"method": "stderr", "type": "* -userinput -useroutput", "level": "debug"}],
        "debug": {"recover-from-errors": True},
        "lock-file": "/ircd/db/ircd.lock",
        "datastore": {
            "path": "/ircd/db/ircd.db",
            "autoupgrade": True,
            "mysql": {
                "enabled": False,
                "host": "localhost",
                "port": 3306,
                "user": "ergo",
                "password": "hunter2",
                "history-database": "ergo_history",
                "timeout": "3s",
                "max-conns": 4,
            },
        },
        "limits": {
            "nicklen": 32,
            "identlen": 20,
            "channellen": 64,
            "awaylen": 390,
            "kicklen": 390,
            "topiclen": 390,
            "monitor-entries": 100,
            "whowas-entries": 100,
            "chan-list-modes": 60,
            "registration-messages": 1024,
            "multiline": {"max-bytes": 4096, "max-lines": 100},
        },
        "fakelag": {
            "enabled": True,
            "window": "1s",
            "burst-limit": 7,
            "messages-per-window": 3,
            "cooldown": "2s",
            "command-budgets": {
                "CHATHISTORY": 16,
                "MARKREAD": 16,
                "MONITOR": 1,
                "WHO": 4,
            },
        },
        "roleplay": {
            "enabled": False,
            "require-oper": True,
            "require-chanops": False,
            "add-suffix": True,
        },
        "extjwt": None,
        "history": {
            "enabled": True,
            "channel-length": 2048,
            "client-length": 256,
            "autoresize-window": "3d",
            "autoreplay-on-join": 0,
            "chathistory-maxmessages": 1000,
            "znc-maxmessages": 2048,
            "restrictions": {
                "expire-time": "1w",
                "query-cutoff": "none",
                "grace-period": "1h",
            },
            "persistent": {
                "enabled": False,
                "unregistered-channels": False,
                "registered-channels": "opt-out",
                "direct-messages": "opt-out",
            },
            "retention": {
                "allow-individual-delete": False,
                "enable-account-indexing": False,
            },
            "tagmsg-storage": {
                "default": False,
                "whitelist": ["+draft/react", "+react"],
            },
        },
        "allow-environment-overrides": True,
    }

    # ConfigMap
    yield {
        "apiVersion": "v1",
        "kind": "ConfigMap",
        "metadata": {"name": "ircd-config"},
        "data": {
            "ircd.motd": ergo_motd,
            "ircd.yaml": yaml.dump(ergo_config),
        },
    }

    # Secrets
    yield {
        "apiVersion": "v1",
        "kind": "Secret",
        "metadata": {"name": "ircd-secrets"},
        "stringData": {
            "ERGO__ACCOUNTS__OAUTH2__CLIENT_SECRET": "",
        },
    }

    ircd_labels = {"k8s.ocf.io/app": name, "k8s.ocf.io/component": "ircd"}
    yield {
        "apiVersion": "apps/v1",
        "kind": "StatefulSet",
        "metadata": {"name": name},
        "spec": {
            "replicas": 1,
            "selector": {"matchLabels": ircd_labels},
            "serviceName": "ergo",
            "template": {
                "metadata": {"labels": ircd_labels},
                "spec": {
                    "containers": [
                        {
                            "name": "ergo",
                            "image": f"ghcr.io/ergochat/ergo:{version}",
                            "ports": [{"containerPort": 8097}, {"containerPort": 6697}],
                            "volumeMounts": [
                                {"name": "ircd-volume", "mountPath": "/ircd/db"},
                                {"name": "ircd-config", "mountPath": "/ircd"},
                                {"name": "ircd-tls", "mountPath": "/etc/ssl/server_certs"},
                            ],
                            "envFrom": [{"secretRef": {"name": "ircd-secrets"}}],
                        },
                        {
                            "name": "gamja",
                            "image": get_image_tag("gamja"),
                            "ports": [{"containerPort": 80}, {"containerPort": 443}],
                            "volumeMounts": [
                                {"name": "ircd-tls", "mountPath": "/etc/ssl/server_certs"},
                            ],
                        },
                        {
                            "name": "config-reloader",
                            "image": f"ghcr.io/ergochat/ergo:{version}",
                            "command": ["/bin/sh"],
                            "args": [
                                "-c",
                                'echo "Watching /ircd/";\ninotifyd - /ircd/:wMymndox /etc/ssl/server_certs/:wMymndox | while read -r notifies ; do\n  echo "$notifies";\n  echo "notify received, sending SIGHUP";\n  pkill -HUP ergo;\ndone\necho "Exiting.";\n',
                            ],
                            "volumeMounts": [
                                {"name": "ircd-config", "mountPath": "/ircd"},
                                {"name": "ircd-tls", "mountPath": "/etc/ssl/server_certs"},
                            ],
                        },
                    ],
                    "volumes": [
                        {
                            "name": "ircd-config",
                            "configMap": {"name": "ircd-config"},
                        },
                        {
                            "name": "ircd-tls",
                            "secret": {"secretName": f"{name}"},
                        },
                    ],
                },
            },
            "volumeClaimTemplates": [
                {
                    "metadata": {"name": "ircd-volume"},
                    "spec": {
                        "accessModes": ["ReadWriteOnce"],
                        "resources": {"requests": {"storage": "16Gi"}},
                    },
                }
            ],
        },
    }

    yield {
        "apiVersion": "v1",
        "kind": "Secret",
        "metadata": {"name": "sopel-config"},
        "stringData": {
            "default.cfg": "This file exists only on Vault.",
        },
    }

    def get_plugin(name):
        return Path(__file__).parent.joinpath("sopel", "plugins", name).read_text()

    # This feels a bit hacky but like... meh... it's not going to go over the 1MB limit.
    yield {
        "apiVersion": "v1",
        "kind": "ConfigMap",
        "metadata": {"name": "sopel-plugins"},
        "data": {
            "check.py": get_plugin("check.py"),
            "lab.py": get_plugin("lab.py"),
            "create.py": get_plugin("create.py"),
        },
    }

    sopel_labels = {"k8s.ocf.io/app": name, "k8s.ocf.io/component": "sopel"}
    yield {
        "apiVersion": "apps/v1",
        "kind": "StatefulSet",
        "metadata": {"name": "sopel"},
        "spec": {
            "replicas": 1,
            "serviceName": "sopel",
            "selector": {"matchLabels": sopel_labels},
            "template": {
                "metadata": {"labels": sopel_labels},
                "spec": {
                    "containers": [
                        {
                            "name": "sopel",
                            "image": get_image_tag("sopel"),
                            # Mount default.cfg to /home/sopel/.sopel/default.cfg
                            "volumeMounts": [
                                {
                                    "name": "sopel-config",
                                    "mountPath": "/home/sopel/.sopel/default.cfg",
                                    "subPath": "default.cfg",
                                },
                                {
                                    "name": "sopel-data",
                                    "mountPath": "/home/sopel/.sopel/",
                                },
                                {
                                    "name": "sopel-plugins",
                                    "mountPath": "/home/sopel/.sopel/plugins/",
                                },
                            ],
                        }
                    ],
                    "volumes": [
                        {
                            "name": "sopel-config",
                            "secret": {"secretName": "sopel-config"},
                        },
                        {
                            "name": "sopel-plugins",
                            "configMap": {"name": "sopel-plugins"},
                        },
                    ],
                },
            },
            "volumeClaimTemplates": [
                {
                    "metadata": {"name": "sopel-data"},
                    "spec": {
                        "accessModes": ["ReadWriteOnce"],
                        "resources": {"requests": {"storage": "32Gi"}},
                    },
                }
            ],
        },
    }

    yield {
        "apiVersion": "v1",
        "kind": "Service",
        "metadata": {
            "name": name,
            "labels": ircd_labels,
            "annotations": {
                "metallb.universe.tf/loadBalancerIPs": "169.229.226.83,2607:f140:8801::1:83",
                "metallb.universe.tf/allow-shared-ip": ip_sharing_hash,
            },
        },
        "spec": {
            "type": "LoadBalancer",
            "selector": ircd_labels,
            "ipFamilyPolicy": "PreferDualStack",
            "ports": [
                {"name": "websocket", "port": 8097, "targetPort": 8097},
                {"name": "irc", "port": 6697, "targetPort": 6697},
                {"name": "http", "port": 80, "targetPort": 80},
                {"name": "https", "port": 443, "targetPort": 443},
            ],
        },
    }

    yield {
        "apiVersion": "cert-manager.io/v1",
        "kind": "Certificate",
        "metadata": {"name": f"{name}-tls"},
        "spec": {
            "secretName": name,
            "dnsNames": [server_dns],
            "issuerRef": {"name": "letsencrypt", "kind": "ClusterIssuer"},
        },
    }
