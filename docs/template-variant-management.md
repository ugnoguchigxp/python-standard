# FastAPI Standard Variant Management

この文書は `fastapi-standard` を複数のテンプレート variant として保守し、NightWorkers などの外部ツールから clone して再利用できる状態に保つための指示書です。

## 目的

- Web アプリの標準 starter を毎回ゼロから生成せず、clone 可能なテンプレートとして再利用する。
- SQLite、PostgreSQL、pgvector などの永続化方式を branch / tag / snapshot で明確に分ける。
- テンプレートの既定値をプロダクト要件として無批判に採用しないよう、variant の責務と検証手順を明文化する。
- NightWorkers などの agent が「どの variant を使うべきか」を短い判断で選べる状態にする。

## 基本方針

- テンプレート本体は NightWorkers などの利用側 repo に vendoring しない。必要時に `git clone` または archive 展開で取得する。
- 継続保守する差分は branch で管理し、固定スナップショットは tag と archive で残す。
- `main` は最小共通の標準 baseline とし、DB や deploy の強い前提を持ちすぎない。
- DB、auth、deploy、AI/RAG などの大きな前提差分は `variant/*` branch に分離する。
- SSG、SSR、認証追加、Storybook 強化など、既存 variant に重ねられる小さめの差分はまず `overlay/*` branch または patch として管理する。
- 既存プロダクト向けの実験 branch とテンプレート variant branch を混ぜない。

## Branch 構成

### Canonical branches

| Branch | 用途 |
| --- | --- |
| `main` | 共通 baseline。FastAPI + SQLModel + Alembic + React + Vite + Tailwind CSS v4 + TanStack の標準構成。 |
| `variant/sqlite` | local-first、desktop、prototype、小規模 single-user 向け。SQLite を既定にする。 |
| `variant/postgres` | 通常の Web app 向け。PostgreSQL を既定にする（Docker Compose 同梱）。 |
| `variant/pgvector` | RAG、embedding、AI 検索向け。PostgreSQL + pgvector を既定にする。 |
| `variant/turso` | Turso/libSQL を既定にする。 |
| `variant/cloudflare` | Cloudflare Workers Python 前提。 D1 / KV / R2 bindings を含む。 |
| `variant/api-only` | frontend を持たない、FastAPI backend 専用構成。 |
| `variant/auth` | cookie/session JWT 認証サンプルを厚めに持つ variant。 |

### Overlay branches

| Branch | 用途 |
| --- | --- |
| `overlay/ssr` | React/Vite の client-only baseline に SSR entry、server render、hydration、SSR build を追加する。 |
| `overlay/ssg` | prerender、static route manifest などを追加する。 |
| `overlay/celery` | Celery + Redis による非同期ジョブ実行環境を追加する。 |
| `overlay/opentelemetry` | OpenTelemetry による分散トレーシングと構造化ログを追加する。 |

## Tag 命名

tag は「固定して clone できるリリース地点」として使う。branch の代わりに tag だけで差分管理しない。

形式:
```text
<variant>-v<major>.<minor>.<patch>
```

例:
```text
sqlite-v1.0.0
postgres-v1.0.0
pgvector-v1.0.0
cloudflare-v1.0.0
overlay-ssr-v1.0.0
```

## Clone 利用

### Branch を指定して clone
```bash
git clone --depth 1 --branch variant/sqlite <repo-url> my-app
cd my-app
```

### Tag を指定して clone
```bash
git clone --depth 1 --branch sqlite-v1.0.0 <repo-url> my-app
cd my-app
```

## Release checklist

release tag を打つ前に確認する項目:

- `git status --short` が意図した変更だけになっている。
- README に variant 固有の起動手順がある。
- `.env.example` が variant と一致している。
- DB migration と seed が fresh DB で通る。
- `uv run pytest` が通る。
- `pnpm build` が通る。
- `node_modules`、`.env`、DB ファイル、test artifacts が snapshot に含まれない。
- tag 名が `<variant>-v<major>.<minor>.<patch>` に従っている。
