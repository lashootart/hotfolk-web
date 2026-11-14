# HOTFOLK® – hotfolk.sk

- `site/` – hotový web, ktorý sa nahráva na WebSupport (`/hotfolk.sk/web/`)
- `src/` – generátor stránok: texty a ceny v `src/content.py`, šablóny v `src/build.py`, hlasovanie v `src/google/`
- Pregenerovanie: `python3 src/build.py site`

Každý push do vetvy `main` web automaticky nahrá cez FTP (GitHub Actions → `.github/workflows/deploy.yml`).
Potrebné secrets v repozitári: `FTP_SERVER`, `FTP_USERNAME`, `FTP_PASSWORD`.
