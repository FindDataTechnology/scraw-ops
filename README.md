# scraw-ops

Shared central service that all `scraw-*` projects deploy into: **scrapyd** + **scrapyd-web** + **redis** in one `docker-compose`.

| Service      | Port  | Role                                                        |
|--------------|-------|-------------------------------------------------------------|
| scrapyd      | 6800  | Receives eggs, runs spider jobs                             |
| scrapyd-web  | 5000  | One UI managing every `scraw-*` project/node                |
| redis        | 6379  | `scrapy-redis` scheduler queue + dupefilter for all projects |

## Run

```bash
cd scraw-ops
docker compose up -d --build
```

Verify:
```bash
curl -s http://localhost:6800/listprojects.json | python3 -m json.tool   # scrapyd
open http://localhost:5000                                                # scrapyd-web UI
redis-cli -h localhost -p 6379 ping                                       # -> PONG
```

## How scraw-* projects use it

Each `scraw-*` project ships only an egg + client config (no infra). From a project directory:

```bash
SCRAPYD_URL=http://localhost:6800 ./deploy.sh     # build egg + scrapyd-deploy
python schedule.py <spider>                       # schedule via scrapyd API
```

Deployed projects appear in the scrapyd-web project list and can be scheduled/stopped/inspected from the UI.

## Distributed-ready (scaling out)

`scrapy-redis` backs every project's scheduler + dupefilter against the shared redis. To add a worker node:

1. Run another scrapyd instance that can reach the same redis (e.g. another host with `REDIS_URL=redis://<shared-redis>:6379/0`).
2. Add it to `SCRAPYD_SERVERS` in `scrapydweb_settings.py` and redeploy `scrapydweb`.
3. Deploy the project's egg to the new node too.

Both nodes consume the same per-project queue (`scraw_<src>:*`); neither re-emits an item the other already emitted.

## Per-project redis isolation

Each project namespaces its keys as `scraw_<src>:*`. Flush one project's queue without touching others:

```bash
redis-cli --scan --pattern 'scraw_world_bank_data:*' | xargs -r redis-cli del
```

## Files

- `docker-compose.yml` - the three services
- `Dockerfile.scrapyd` / `Dockerfile.scrapydweb` - images (python:3.11-slim + installs)
- `scrapyd.conf` - scrapyd config (bind, eggs/logs/dbs dirs, max_proc)
- `scrapydweb_settings.py` - scrapyd-web nodes + UI auth
- `redis.conf` - AOF persistence
