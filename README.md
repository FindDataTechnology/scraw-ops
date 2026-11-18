# scraw-ops

> **Part of the [Wire line (寻数·柏讯)](https://www.finddatatech.cloud/products/wire) of [FindData](https://www.finddatatech.cloud)** — Crawl operations — the shared scrapyd + redis service every crawler project deploys into.

Shared central service that all `scraw-*` projects deploy into: **scrapyd** + **redis** in one `docker-compose`.

> **scrapydweb 已退役（2026-09-26）。** 它曾是统一管理 UI；现役的操作台是
> fd-open-data-mcp 的 panel（`/panel`，crawl-control-center 能力面），调度由
> `crawl-reconciler` CronJob 驱动。本仓保留 scrapyd + redis 仅作为
> `RECONCILER_LAUNCHER=scrapyd` 的本地回退通道，不再是生产入口。

| Service | Port  | Role                                                        |
|---------|-------|-------------------------------------------------------------|
| scrapyd | 6800  | Receives eggs, runs spider jobs (local fallback launcher)   |
| redis   | 6379  | `scrapy-redis` scheduler queue + dupefilter for all projects |

## Run

```bash
cd scraw-ops
docker compose up -d --build
```

Verify:
```bash
curl -s http://localhost:6800/listprojects.json | python3 -m json.tool   # scrapyd
redis-cli -h localhost -p 6379 ping                                       # -> PONG
```

## How scraw-* projects use it

Each `scraw-*` project ships only an egg + client config (no infra). From a project directory:

```bash
SCRAPYD_URL=http://localhost:6800 ./deploy.sh     # build egg + scrapyd-deploy
python schedule.py <spider>                       # schedule via scrapyd API
```

## Distributed-ready (scaling out)

`scrapy-redis` backs every project's scheduler + dupefilter against the shared redis. To add a worker node:

1. Run another scrapyd instance that can reach the same redis (e.g. another host with `REDIS_URL=redis://<shared-redis>:6379/0`).
2. Deploy the project's egg to the new node too.

Both nodes consume the same per-project queue (`scraw_<src>:*`); neither re-emits an item the other already emitted.

## Per-project redis isolation

Each project namespaces its keys as `scraw_<src>:*`. Flush one project's queue without touching others:

```bash
redis-cli --scan --pattern 'scraw_world_bank_data:*' | xargs -r redis-cli del
```

## Files

- `docker-compose.yml` - the services
- `Dockerfile.scrapyd` / `Dockerfile.scrapydweb` - images (scrapydweb 退役仅留档)
- `scrapyd.conf` - scrapyd config (bind, eggs/logs/dbs dirs, max_proc)
- `scrapydweb_settings.py` - 退役留档（不再部署）
- `redis.conf` - AOF persistence
