# SPIP Database to Markdown
Script(s) to export the SPIP MySQL database of the current website to plain text Markdown files with YAML front-matter metadata.

## Notes on exporting the SPIP MySQL data to Markdown files
There are 40 tables, of which :

- 8 contain the major part of the data
- 4 are relations between other tables
- 5 contain as few data as global parameters
- 13 seems to be technical information specific to SPIP
- 10 are completely empty

### Tables & Database schema
Elents to take into account :

- SPIP [Markup language](https://www.spip.net/fr_article1578.html)
- SPIP [Database structure](https://www.spip.net/fr_article713.html)
- SPIP [HTML templates](https://www.spip.net/fr_article879.html)

#### Main tables, with a lot of data
These tables contains a lot of data. Each row will probably correspond to one Markdown file.

- spip_articles
- spip_auteurs
- spip_documents
- spip_evenements
- spip_meta
- spip_mots
- spip_rubriques
- spip_syndic_articles

#### Relational tables, making links between main tables
These tables join information between main tables. They will probably correspond to entries in YAML front-matters.

- spip_auteurs_liens
- spip_documents_liens
- spip_mots_liens
- spip_zones_liens

#### Tables with little data
These tables contains a few rows. They will probably correspond to global configuration files in static website. 

- spip_groupes_mots
- spip_meslettres
- spip_messages
- spip_syndic
- spip_zones

#### Technical tables
These tables contain technical information that is probably specific to SPIP or the system on which it is installed.

- spip_depots
- spip_depots_plugins
- spip_jobs
- spip_ortho_cache
- spip_paquets
- spip_plugins
- spip_referers
- spip_referers_articles
- spip_types_documents
- spip_versions
- spip_versions_fragments
- spip_visites
- spip_visites_articles

#### Empty tables
These tables are empty, so they don’t need to be treated.

- spip_breves
- spip_evenements_participants
- spip_forum
- spip_jobs_liens
- spip_ortho_dico
- spip_petitions
- spip_resultats
- spip_signatures
- spip_test
- spip_urls
