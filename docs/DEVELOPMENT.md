# Development setup

## Requirements

- Python 3.13 (the version used for the local setup and screenshots)
- pip
- A browser

Runtime packages are listed in `requirements.txt`: Django 5.2 and Pillow. The project uses Django templates and CSS; no frontend build step or JavaScript package install is needed.

## Windows / PowerShell

From the repository root:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
$env:DJANGO_DB_PATH = Join-Path (Get-Location) 'local.sqlite3'
$env:DJANGO_MEDIA_ROOT = Join-Path (Get-Location) 'media'
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

The local database path is set deliberately so development commands do not use the repository’s existing `db.sqlite3`. The project reads the configured paths from environment variables and defaults to its usual local Django paths when they are unset.

## Linux / macOS

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
export DJANGO_DB_PATH="$PWD/local.sqlite3"
export DJANGO_MEDIA_ROOT="$PWD/media"
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

## Demo catalog

`python manage.py seed_demo` is repeatable. It upserts five categories, eight sample products, four customer reviews, two active product discounts, and the `WELCOME10` promo code. Catalog images and copy are synthetic. The review authors have unusable passwords and cannot sign in; create an account through the storefront to try user-facing account and review flows.

The command creates or updates only its named demo records. It does not create a Django superuser. To use Django Admin locally:

```powershell
python manage.py createsuperuser
```

Then sign in at `/admin/`. The admin uses Django’s built-in staff permissions.

## Environment settings

| Variable               | Purpose                         | Local default                         |
| ---------------------- | ------------------------------- | ------------------------------------- |
| `DJANGO_SECRET_KEY`    | Django signing key              | A random process-local value if unset |
| `DJANGO_DEBUG`         | Enable Django debug mode        | `true`                                |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated host names      | `127.0.0.1,localhost,testserver`      |
| `DJANGO_DB_PATH`       | SQLite database file            | `db.sqlite3` in the project root      |
| `DJANGO_MEDIA_ROOT`    | Upload and demo asset directory | `media/` in the project root          |

For local development, the generated secret is convenient but changes after a process restart. Set a stable secret in the environment when you need stable sessions. Before any public deployment, provide a strong secret, set `DJANGO_DEBUG=false`, configure the real allowed host names, review Django’s deployment checklist, and configure secure cookies, HTTPS, static files, media storage, backups, and a production database.

## Useful commands

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py migrate
```

Uploaded profile images and catalog uploads belong under the configured media directory. The included demo SVG files are stored under `media/demo/` and are safe to use in screenshots.
