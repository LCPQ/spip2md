---
lang: en
---

# SPIP Database to Markdown

`spip2md` is a litle Python app that can export a SPIP database into a plain text,
Markdown + YAML repository, usable with static site generators.

## Features

`spip2md` is currently able to :

- Export every section (`spip_rubriques`), with every article (`spip_articles`) they
  contain
  - Replace authors (`spip_auteurs`) IDs with their name (in YAML block)
  - Generate different files for each language found in `<multi>` blocks
  - Copy over all the attached files (`spip_documents`), with proper links
  - Convert SPIP [Markup language](https://www.spip.net/fr_article1578.html)
  - Convert SPIP ID-based internal links (like `<art123>`) into path-based, normal links

## Dependencies

`spip2md` needs Python version 3.9 or supperior.

`spip2md` uses three Python libraries (as defined in pyproject.toml) :

- Peewee, with a database connection for your database :
  - pymysql (MySQL/MariaDB)
- PyYaml
- python-slugify (unidecode)

## Usage

First make sure you have the dependencies installed (system-wide or in a
Python virtual-environment).

Next, make sure you have access to the SPIP database you want to export on a
MySQL/MariaDB server. By default, `spip2md` expects a database named `spip` hosted on
`localhost`, with a user named `spip` of which password is `password`, but you can
totally configure this as well as other settings in the YAML config file.

If you want to copy over attached files like images, you also need access to
the data directory of your SPIP website, usually named `IMG`, and either rename it
`data` in your current working directory, or set `data_dir` setting to its path.

Currently, the config file can be given as the only CLI parameter, or if no parameter
is given, the program searches a `spip2md.yml` file in the current working directory.
Here’s the *configuration options* :

```yaml
db: Name of the database (default is spip)
db_host: Host of the database (default is localhost)
db_user: The database user (default is spip)
db_pass: The database password (default is password)
data_dir: The directory in which SPIP images & files are stored
export_languages: Array of languages to export (default is ["en",])
output_dir: The directory in which files will be written (default is output/)
prepend_h1: Should spip2md prepend the title of articles as Markdown h1 (default true)
prepend_id: Whether to prepend ID of the object to directory slug
prepend_lang: Whether to prepend lang of the object to directory slug
export_drafts: Should we export drafts (default true)
remove_html: Should we clean remaining HTML blocks (default true)
unknown_char_replacement: Broken encoding that cannot be repaired is replaced with that
clear_log: Clear logfile between runs instead of appending to (default false)
clear_output: Clear output dir between runs instead of merging into (default false)
logfile: Name of the logs file (default is spip2md.log)
```

## External links

- SPIP [Database structure](https://www.spip.net/fr_article713.html)

## TODO

These tables seem to contain not-as-useful information,
but this needs to be investicated :

- `spip_evenements`
- `spip_meta`
- `spip_mots`
- `spip_syndic_articles`
- `spip_mots_liens`
- `spip_zones_liens`
- `spip_groupes_mots`
- `spip_meslettres`
- `spip_messages`
- `spip_syndic`
- `spip_zones`

These tables seem technical, SPIP specific :

- `spip_depots`
- `spip_depots_plugins`
- `spip_jobs`
- `spip_ortho_cache`
- `spip_paquets`
- `spip_plugins`
- `spip_referers`
- `spip_referers_articles`
- `spip_types_documents`
- `spip_versions`
- `spip_versions_fragments`
- `spip_visites`
- `spip_visites_articles`

These tables are empty :

- `spip_breves`
- `spip_evenements_participants`
- `spip_forum`
- `spip_jobs_liens`
- `spip_ortho_dico`
- `spip_petitions`
- `spip_resultats`
- `spip_signatures`
- `spip_test`
- `spip_urls`
