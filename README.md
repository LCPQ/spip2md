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
- python-slugify (unidecode variant prefered)

## Installation

### Simple `pip` method

Install the package with `pip install spip2md` (or `python -m pip install spip2md`
if you don’t have pip installed).

Assuming your `$PATH` contains your `pip` install directory, you can now run
`spip2md` a normal command of the same name.

### Traditional method

Clone this git repo with command `git clone` and `cd` into the created directory.

Either make sure you have the dependencies installed system-wide, or create a
Python virtual-environment and install them inside.

You can then run `spip2md` as a Python module with command `python -m spip2md`.
Make sure to replace `spip2md` with a path to directory `spip2md` if you
didn’t `cd` into this repository’s directory.

## Configuration and Usage

Make sure you have access to the SPIP database you want to export on a
MySQL/MariaDB server. By default, `spip2md` expects a database named `spip` hosted on
`localhost`, with a user named `spip` of which password is `password`, but you can
totally configure this as well as other settings in the YAML config file.

If you want to copy over attached files like images, you also need access to
the data directory of your SPIP website, usually named `IMG`, and either rename it
`data` in your current working directory, or set `data_dir` setting to its path.

### YAML configuration file

To configure `spip2md` you can place a file named `spip2md.yml` in standard \*nix
configuration locations, set it with the command line argument, or run the
program with a `spip2md.yml` file in your working directory.

Here’s the *default configuration options* with comments explaining their meaning :

```yaml
# Data source settings
db: spip # Name of the database
db_host: localhost # Host of the database
db_user: spip # The database user
db_pass: password # The database password
data_dir: data # The directory in which SPIP images & files are stored

# Data destination settings
export_languages: ["en"] # Array of languages to export, two letter lang code
# If set, directories will be created only for this language, according to this
# language’s titles. Other languages will be written along with correct url: attribute
storage_language: null
output_dir: output/ # The directory in which files will be written

# Destination directories names settings
# Prepend ID to directory slug, preventing collisions
# If false, a counter will be appended in case of name collision
prepend_id: false
# Prepend lang of the object to directory slug, prenventing collision between langs
prepend_lang: false
title_max_length: 42 # Maximum length (chars) of a single filename

# Text body processing settings
remove_html: true # Should we clean remaining HTML blocks
metadata_markup: false # Should we keep markup (Markdown) in metadata fields, like title
unknown_char_replacement: ?? # String to replace broken encoding that cannot be repaired
prepend_h1: false # Add title of articles as Markdown h1, looks better on certain themes
# Array of objects with 2 or 3 values, allowing to move some fields into others.
# {src: moved_field_name, dest: destination_field_name, repr: "how to merge them"}
# repr is formatted with "{}" being the moved field, and "_" the destination one
# For example, to append a field "subtitle" to a field "title":
#   - src: subtitle
#     dest: title
#     repr: "{} _" # (this is the default repr)
move_fields: []
# Some taxonomies (Spip Mots types) to not export, typically specific to Spip functions
ignore_taxonomies: ["Gestion du site", "Gestion des articles", "Mise en page"]
rename_taxonomies: { equipes: "tag-equipes" } # Rename taxonomies (prenvent conflict)

# Ignored data settings
export_drafts: true # Should we export drafts
export_empty: true # Should we export empty articles
ignore_patterns: [] # List of regexes : Matching sections or articles will be ignored

# Settings you probably don’t want to modify
clear_log: true # Clear logfile between runs instead of appending to
clear_output: true # Clear output dir between runs instead of merging into

logfile: log-spip2md.log # Name of the logs file
loglevel: WARNING # Refer to Python’s loglevels

export_filetype: md # Filetype of exported text files
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
