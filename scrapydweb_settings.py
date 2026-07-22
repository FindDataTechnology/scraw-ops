# scrapydweb settings for the shared scraw-ops service.
# Docs: https://github.com/my8100/scrapydweb
#
# This file is scrapydweb's actual configuration mechanism (a Python settings
# module read from the working directory). The design doc referred to it as
# scrapydweb.conf; it is realized here as scrapydweb_settings.py.

# scrapyd nodes managed by this scrapyd-web instance.
# To scale out, add more entries here - each pointing at the SAME redis so
# workers share one per-project queue (scrapy-redis distributed-ready).
SCRAPYD_SERVERS = ["scrapyd:6800"]
# Parallel to SCRAPYD_SERVERS; "" = no auth, or "username:password".
SCRAPYD_SERVERS_AUTH = [""]

SCRAPYDWEB_BIND = "0.0.0.0"
SCRAPYDWEB_PORT = 5000

# Optional web UI auth - uncomment and set to enable login.
# USERNAME = "admin"
# PASSWORD = "change-me"
