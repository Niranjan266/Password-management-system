# VaultX

A Django password-management application.

## Run locally

```powershell
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Deploy to Vercel

Vercel detects this Django project from the root-level `manage.py`. No custom
`vercel.json` routing is required.

1. In the Vercel project, add a Postgres integration from the Marketplace
   (Neon, Supabase, or another provider) and make sure it supplies a
   `DATABASE_URL` environment variable.
2. Add these Vercel environment variables for Production and Preview:

   - `DJANGO_SECRET_KEY`: a long random secret.
   - `VAULT_ENCRYPTION_KEY`: a long random secret that must never change after
     passwords have been saved.
   - `DJANGO_ALLOWED_HOSTS`: `.vercel.app,your-domain.example`
   - `DJANGO_CSRF_TRUSTED_ORIGINS`: `https://*.vercel.app,https://your-domain.example`

3. Run the database migrations against the production database once:

```powershell
$env:DATABASE_URL="<your-postgres-connection-string>"
python manage.py migrate
```

4. Push the repository to GitHub and redeploy it in Vercel.

Do not use the repository's SQLite database in production. Vercel Functions
have an ephemeral/read-only filesystem, so SQLite writes are not persistent.
