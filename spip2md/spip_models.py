"""
This file is part of spip2md.
Copyright (C) 2023 LCPQ/Guilhem Fauré

spip2md is free software: you can redistribute it and/or modify it under the terms of
the GNU General Public License version 2 as published by the Free Software Foundation.

spip2md is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with spip2md.
If not, see <https://www.gnu.org/licenses/>.
"""
# type: ignore
from peewee import (
    SQL,
    BigAutoField,
    BigIntegerField,
    CharField,
    CompositeKey,
    DateField,
    DateTimeField,
    FloatField,
    IntegerField,
    Model,
    MySQLDatabase,
    TextField,
)

DB = MySQLDatabase(None)


# class UnknownField(object):
#     def __init__(self, *_, **__):
#         pass


class BaseModel(Model):
    class Meta:
        database: MySQLDatabase = DB


class SpipArticles(BaseModel):
    accepter_forum = CharField(constraints=[SQL("DEFAULT ''")])
    chapo = TextField()
    date = DateTimeField(constraints=[SQL("DEFAULT '0000-00-00 00:00:00'")])
    date_modif = DateTimeField(constraints=[SQL("DEFAULT '0000-00-00 00:00:00'")])
    date_redac = DateTimeField(constraints=[SQL("DEFAULT '0000-00-00 00:00:00'")])
    descriptif = TextField()
    export = CharField(constraints=[SQL("DEFAULT 'oui'")], null=True)
    extra = TextField(null=True)
    id_article = BigAutoField()
    id_rubrique = BigIntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    id_secteur = BigIntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    id_trad = BigIntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    id_version = IntegerField(constraints=[SQL("DEFAULT 0")])
    lang = CharField(constraints=[SQL("DEFAULT ''")], index=True)
    langue_choisie = CharField(constraints=[SQL("DEFAULT 'non'")], null=True)
    maj = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    microblog = CharField(constraints=[SQL("DEFAULT ''")])
    nom_site = TextField()
    popularite = FloatField(constraints=[SQL("DEFAULT 0")])
    ps = TextField()
    referers = IntegerField(constraints=[SQL("DEFAULT 0")])
    soustitre = TextField()
    statut = CharField(constraints=[SQL("DEFAULT '0'")])
    surtitre = TextField()
    texte = TextField()
    titre = TextField()
    url_site = CharField(constraints=[SQL("DEFAULT ''")])
    virtuel = CharField(constraints=[SQL("DEFAULT ''")])
    visites = IntegerField(constraints=[SQL("DEFAULT 0")])

    class Meta:
        table_name: str = "spip_articles"
        indexes = ((("statut", "date"), False),)


class SpipAuteurs(BaseModel):
    alea_actuel = TextField()
    alea_futur = TextField()
    bio = TextField()
    cookie_oubli = TextField()
    email = TextField()
    en_ligne = DateTimeField(
        constraints=[SQL("DEFAULT '0000-00-00 00:00:00'")], index=True
    )
    extra = TextField(null=True)
    htpass = TextField()
    id_auteur = BigAutoField()
    imessage = CharField()
    lang = CharField(constraints=[SQL("DEFAULT ''")])
    login = CharField(index=True)
    low_sec = TextField()
    maj = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    messagerie = CharField()
    nom = TextField()
    nom_site = TextField()
    pass_ = TextField(column_name="pass")
    pgp = TextField()
    prefs = TextField()
    source = CharField(constraints=[SQL("DEFAULT 'spip'")])
    statut = CharField(constraints=[SQL("DEFAULT '0'")], index=True)
    url_site = TextField()
    webmestre = CharField(constraints=[SQL("DEFAULT 'non'")])

    class Meta:
        table_name: str = "spip_auteurs"


class SpipAuteursLiens(BaseModel):
    id_auteur = BigIntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    id_objet = BigIntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    objet = CharField(constraints=[SQL("DEFAULT ''")], index=True)
    vu = CharField(constraints=[SQL("DEFAULT 'non'")])

    class Meta:
        table_name: str = "spip_auteurs_liens"
        indexes = ((("id_auteur", "id_objet", "objet"), True),)
        primary_key = CompositeKey("id_auteur", "id_objet", "objet")


class SpipBreves(BaseModel):
    date_heure = DateTimeField(constraints=[SQL("DEFAULT '0000-00-00 00:00:00'")])
    extra = TextField(null=True)
    id_breve = BigAutoField()
    id_rubrique = BigIntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    lang = CharField(constraints=[SQL("DEFAULT ''")])
    langue_choisie = CharField(constraints=[SQL("DEFAULT 'non'")], null=True)
    lien_titre = TextField()
    lien_url = TextField()
    maj = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    statut = CharField(constraints=[SQL("DEFAULT '0'")])
    texte = TextField()
    titre = TextField()

    class Meta:
        table_name: str = "spip_breves"


class SpipDepots(BaseModel):
    descriptif = TextField()
    id_depot = BigAutoField()
    maj = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    nbr_autres = IntegerField(constraints=[SQL("DEFAULT 0")])
    nbr_paquets = IntegerField(constraints=[SQL("DEFAULT 0")])
    nbr_plugins = IntegerField(constraints=[SQL("DEFAULT 0")])
    sha_paquets = CharField(constraints=[SQL("DEFAULT ''")])
    titre = TextField()
    type = CharField(constraints=[SQL("DEFAULT ''")])
    url_archives = CharField(constraints=[SQL("DEFAULT ''")])
    url_brouteur = CharField(constraints=[SQL("DEFAULT ''")])
    url_commits = CharField(constraints=[SQL("DEFAULT ''")])
    url_serveur = CharField(constraints=[SQL("DEFAULT ''")])
    xml_paquets = CharField(constraints=[SQL("DEFAULT ''")])

    class Meta:
        table_name: str = "spip_depots"


class SpipDepotsPlugins(BaseModel):
    id_depot = BigIntegerField()
    id_plugin = BigIntegerField()

    class Meta:
        table_name: str = "spip_depots_plugins"
        indexes = ((("id_depot", "id_plugin"), True),)
        primary_key = CompositeKey("id_depot", "id_plugin")


class SpipDocuments(BaseModel):
    brise = IntegerField(constraints=[SQL("DEFAULT 0")], null=True)
    credits = CharField(constraints=[SQL("DEFAULT ''")])
    date = DateTimeField(constraints=[SQL("DEFAULT '0000-00-00 00:00:00'")])
    date_publication = DateTimeField(constraints=[SQL("DEFAULT '0000-00-00 00:00:00'")])
    descriptif = TextField()
    distant = CharField(constraints=[SQL("DEFAULT 'non'")], null=True)
    extension = CharField(constraints=[SQL("DEFAULT ''")], index=True)
    fichier = TextField()
    hauteur = IntegerField(null=True)
    id_document = BigAutoField()
    id_vignette = BigIntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    largeur = IntegerField(null=True)
    maj = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    media = CharField(constraints=[SQL("DEFAULT 'file'")])
    mode = CharField(constraints=[SQL("DEFAULT 'document'")], index=True)
    statut = CharField(constraints=[SQL("DEFAULT '0'")])
    taille = BigIntegerField(null=True)
    titre = TextField()

    class Meta:
        table_name: str = "spip_documents"


class SpipDocumentsLiens(BaseModel):
    id_document = BigIntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    id_objet = BigIntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    objet = CharField(constraints=[SQL("DEFAULT ''")], index=True)
    vu = CharField(constraints=[SQL("DEFAULT 'non'")])

    class Meta:
        table_name: str = "spip_documents_liens"
        indexes = ((("id_document", "id_objet", "objet"), True),)
        primary_key = CompositeKey("id_document", "id_objet", "objet")


class SpipEvenements(BaseModel):
    adresse = TextField()
    attendee = CharField(constraints=[SQL("DEFAULT ''")])
    date_creation = DateTimeField(constraints=[SQL("DEFAULT '0000-00-00 00:00:00'")])
    date_debut = DateTimeField(
        constraints=[SQL("DEFAULT '0000-00-00 00:00:00'")], index=True
    )
    date_fin = DateTimeField(
        constraints=[SQL("DEFAULT '0000-00-00 00:00:00'")], index=True
    )
    descriptif = TextField()
    horaire = CharField(constraints=[SQL("DEFAULT 'oui'")])
    id_article = BigIntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    id_evenement = BigAutoField()
    id_evenement_source = BigIntegerField()
    inscription = IntegerField(constraints=[SQL("DEFAULT 0")])
    lieu = TextField()
    maj = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    notes = TextField()
    origin = CharField(constraints=[SQL("DEFAULT ''")])
    places = IntegerField(constraints=[SQL("DEFAULT 0")])
    statut = CharField(constraints=[SQL("DEFAULT '0'")])
    titre = TextField()

    class Meta:
        table_name: str = "spip_evenements"


class SpipEvenementsParticipants(BaseModel):
    date = DateTimeField(constraints=[SQL("DEFAULT '0000-00-00 00:00:00'")])
    email = TextField()
    id_auteur = BigIntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    id_evenement = BigIntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    id_evenement_participant = BigAutoField()
    nom = TextField()
    reponse = CharField(constraints=[SQL("DEFAULT '?'")])

    class Meta:
        table_name: str = "spip_evenements_participants"


class SpipForum(BaseModel):
    auteur = TextField()
    date_heure = DateTimeField(constraints=[SQL("DEFAULT '0000-00-00 00:00:00'")])
    date_thread = DateTimeField(constraints=[SQL("DEFAULT '0000-00-00 00:00:00'")])
    email_auteur = TextField()
    id_auteur = BigIntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    id_forum = BigAutoField()
    id_objet = BigIntegerField(constraints=[SQL("DEFAULT 0")])
    id_parent = BigIntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    id_thread = BigIntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    ip = CharField(constraints=[SQL("DEFAULT ''")])
    maj = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    nom_site = TextField()
    objet = CharField(constraints=[SQL("DEFAULT ''")])
    statut = CharField(constraints=[SQL("DEFAULT '0'")])
    texte = TextField()
    titre = TextField()
    url_site = TextField()

    class Meta:
        table_name: str = "spip_forum"
        indexes = ((("statut", "id_parent", "id_objet", "objet", "date_heure"), False),)


class SpipGroupesMots(BaseModel):
    comite = CharField(constraints=[SQL("DEFAULT ''")])
    descriptif = TextField()
    forum = CharField(constraints=[SQL("DEFAULT ''")])
    id_groupe = BigAutoField()
    maj = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    minirezo = CharField(constraints=[SQL("DEFAULT ''")])
    obligatoire = CharField(constraints=[SQL("DEFAULT ''")])
    tables_liees = TextField()
    texte = TextField()
    titre = TextField()
    unseul = CharField(constraints=[SQL("DEFAULT ''")])

    class Meta:
        table_name: str = "spip_groupes_mots"


class SpipJobs(BaseModel):
    args = TextField()
    date = DateTimeField(constraints=[SQL("DEFAULT '0000-00-00 00:00:00'")], index=True)
    descriptif = TextField()
    fonction = CharField()
    id_job = BigAutoField()
    inclure = CharField()
    md5args = CharField(constraints=[SQL("DEFAULT ''")])
    priorite = IntegerField(constraints=[SQL("DEFAULT 0")])
    status = IntegerField(constraints=[SQL("DEFAULT 1")], index=True)

    class Meta:
        table_name: str = "spip_jobs"


class SpipJobsLiens(BaseModel):
    id_job = BigIntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    id_objet = BigIntegerField(constraints=[SQL("DEFAULT 0")])
    objet = CharField(constraints=[SQL("DEFAULT ''")])

    class Meta:
        table_name: str = "spip_jobs_liens"
        indexes = ((("id_job", "id_objet", "objet"), True),)
        primary_key = CompositeKey("id_job", "id_objet", "objet")


class SpipMeslettres(BaseModel):
    date = DateTimeField(constraints=[SQL("DEFAULT '0000-00-00 00:00:00'")])
    id_malettre = BigAutoField()
    lang = CharField()
    titre = TextField()
    url_html = CharField(null=True)
    url_txt = CharField()

    class Meta:
        table_name: str = "spip_meslettres"


class SpipMessages(BaseModel):
    date_fin = DateTimeField(constraints=[SQL("DEFAULT '0000-00-00 00:00:00'")])
    date_heure = DateTimeField(constraints=[SQL("DEFAULT '0000-00-00 00:00:00'")])
    destinataires = TextField()
    id_auteur = BigIntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    id_message = BigAutoField()
    maj = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    rv = CharField(constraints=[SQL("DEFAULT ''")])
    statut = CharField(constraints=[SQL("DEFAULT '0'")])
    texte = TextField()
    titre = TextField()
    type = CharField(constraints=[SQL("DEFAULT ''")])

    class Meta:
        table_name: str = "spip_messages"


class SpipMeta(BaseModel):
    impt = CharField(constraints=[SQL("DEFAULT 'oui'")])
    maj = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    nom = CharField(primary_key=True)
    valeur = TextField(null=True)

    class Meta:
        table_name: str = "spip_meta"


class SpipMots(BaseModel):
    descriptif = TextField()
    extra = TextField(null=True)
    id_groupe = BigIntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    id_mot = BigAutoField()
    maj = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    texte = TextField()
    titre = TextField()
    type = TextField()

    class Meta:
        table_name: str = "spip_mots"


class SpipMotsLiens(BaseModel):
    id_mot = BigIntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    id_objet = BigIntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    objet = CharField(constraints=[SQL("DEFAULT ''")], index=True)

    class Meta:
        table_name: str = "spip_mots_liens"
        indexes = ((("id_mot", "id_objet", "objet"), True),)
        primary_key = CompositeKey("id_mot", "id_objet", "objet")


class SpipOrthoCache(BaseModel):
    lang = CharField()
    maj = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")], index=True)
    mot = CharField()
    ok = IntegerField()
    suggest = TextField()

    class Meta:
        table_name: str = "spip_ortho_cache"
        indexes = ((("lang", "mot"), True),)
        primary_key = CompositeKey("lang", "mot")


class SpipOrthoDico(BaseModel):
    id_auteur = BigIntegerField()
    lang = CharField()
    maj = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    mot = CharField()

    class Meta:
        table_name: str = "spip_ortho_dico"
        indexes = ((("lang", "mot"), True),)
        primary_key = CompositeKey("lang", "mot")


class SpipPaquets(BaseModel):
    actif = CharField(constraints=[SQL("DEFAULT 'non'")])
    attente = CharField(constraints=[SQL("DEFAULT 'non'")])
    auteur = TextField()
    branches_spip = CharField(constraints=[SQL("DEFAULT ''")])
    compatibilite_spip = CharField(constraints=[SQL("DEFAULT ''")])
    constante = CharField(constraints=[SQL("DEFAULT ''")])
    copyright = TextField()
    credit = TextField()
    date_crea = DateTimeField(constraints=[SQL("DEFAULT '0000-00-00 00:00:00'")])
    date_modif = DateTimeField(constraints=[SQL("DEFAULT '0000-00-00 00:00:00'")])
    dependances = TextField()
    description = TextField()
    etat = CharField(constraints=[SQL("DEFAULT ''")])
    etatnum = IntegerField(constraints=[SQL("DEFAULT 0")])
    id_depot = BigIntegerField(constraints=[SQL("DEFAULT 0")])
    id_paquet = BigAutoField()
    id_plugin = BigIntegerField(index=True)
    installe = CharField(constraints=[SQL("DEFAULT 'non'")])
    licence = TextField()
    lien_demo = TextField()
    lien_dev = TextField()
    lien_doc = TextField()
    logo = CharField(constraints=[SQL("DEFAULT ''")])
    maj_archive = DateTimeField(constraints=[SQL("DEFAULT '0000-00-00 00:00:00'")])
    maj_version = CharField(constraints=[SQL("DEFAULT ''")])
    nbo_archive = IntegerField(constraints=[SQL("DEFAULT 0")])
    nom_archive = CharField(constraints=[SQL("DEFAULT ''")])
    obsolete = CharField(constraints=[SQL("DEFAULT 'non'")])
    prefixe = CharField(constraints=[SQL("DEFAULT ''")])
    procure = TextField()
    recent = IntegerField(constraints=[SQL("DEFAULT 0")])
    signature = CharField(constraints=[SQL("DEFAULT ''")])
    src_archive = CharField(constraints=[SQL("DEFAULT ''")])
    superieur = CharField(constraints=[SQL("DEFAULT 'non'")])
    traductions = TextField()
    version = CharField(constraints=[SQL("DEFAULT ''")])
    version_base = CharField(constraints=[SQL("DEFAULT ''")])

    class Meta:
        table_name: str = "spip_paquets"


class SpipPetitions(BaseModel):
    email_unique = CharField(constraints=[SQL("DEFAULT ''")])
    id_article = BigIntegerField(constraints=[SQL("DEFAULT 0")], unique=True)
    id_petition = BigAutoField()
    maj = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    message = CharField(constraints=[SQL("DEFAULT ''")])
    site_obli = CharField(constraints=[SQL("DEFAULT ''")])
    site_unique = CharField(constraints=[SQL("DEFAULT ''")])
    statut = CharField(constraints=[SQL("DEFAULT 'publie'")])
    texte = TextField()

    class Meta:
        table_name: str = "spip_petitions"


class SpipPlugins(BaseModel):
    branches_spip = CharField(constraints=[SQL("DEFAULT ''")])
    categorie = CharField(constraints=[SQL("DEFAULT ''")])
    compatibilite_spip = CharField(constraints=[SQL("DEFAULT ''")])
    date_crea = DateTimeField(constraints=[SQL("DEFAULT '0000-00-00 00:00:00'")])
    date_modif = DateTimeField(constraints=[SQL("DEFAULT '0000-00-00 00:00:00'")])
    id_plugin = BigAutoField()
    nom = TextField()
    prefixe = CharField(constraints=[SQL("DEFAULT ''")], index=True)
    slogan = TextField()
    tags = TextField()
    vmax = CharField(constraints=[SQL("DEFAULT ''")])

    class Meta:
        table_name: str = "spip_plugins"


class SpipReferers(BaseModel):
    date = DateField()
    maj = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    referer = CharField(null=True)
    referer_md5 = BigAutoField()
    visites = IntegerField()
    visites_jour = IntegerField(constraints=[SQL("DEFAULT 0")])
    visites_veille = IntegerField(constraints=[SQL("DEFAULT 0")])

    class Meta:
        table_name: str = "spip_referers"


class SpipReferersArticles(BaseModel):
    id_article = IntegerField()
    maj = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    referer = CharField(constraints=[SQL("DEFAULT ''")])
    referer_md5 = BigIntegerField(index=True)
    visites = IntegerField()

    class Meta:
        table_name: str = "spip_referers_articles"
        indexes = ((("id_article", "referer_md5"), True),)
        primary_key = CompositeKey("id_article", "referer_md5")


class SpipResultats(BaseModel):
    id = IntegerField()
    maj = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    points = IntegerField(constraints=[SQL("DEFAULT 0")])
    recherche = CharField(constraints=[SQL("DEFAULT ''")])
    serveur = CharField(constraints=[SQL("DEFAULT ''")])
    table_objet = CharField(constraints=[SQL("DEFAULT ''")])

    class Meta:
        table_name: str = "spip_resultats"
        primary_key = False


class SpipRubriques(BaseModel):
    agenda = IntegerField(constraints=[SQL("DEFAULT 0")])
    date = DateTimeField(constraints=[SQL("DEFAULT '0000-00-00 00:00:00'")])
    date_tmp = DateTimeField(constraints=[SQL("DEFAULT '0000-00-00 00:00:00'")])
    descriptif = TextField()
    extra = TextField(null=True)
    id_parent = BigIntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    id_rubrique = BigAutoField()
    id_secteur = BigIntegerField(constraints=[SQL("DEFAULT 0")])
    id_trad = BigIntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    lang = CharField(constraints=[SQL("DEFAULT ''")], index=True)
    langue_choisie = CharField(constraints=[SQL("DEFAULT 'non'")], null=True)
    maj = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    profondeur = IntegerField(constraints=[SQL("DEFAULT 0")])
    statut = CharField(constraints=[SQL("DEFAULT '0'")])
    statut_tmp = CharField(constraints=[SQL("DEFAULT '0'")])
    texte = TextField()
    titre = TextField()

    class Meta:
        table_name: str = "spip_rubriques"


class SpipSignatures(BaseModel):
    ad_email = TextField()
    date_time = DateTimeField(constraints=[SQL("DEFAULT '0000-00-00 00:00:00'")])
    id_petition = BigIntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    id_signature = BigAutoField()
    maj = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    message = TextField()
    nom_email = TextField()
    nom_site = TextField()
    statut = CharField(constraints=[SQL("DEFAULT '0'")], index=True)
    url_site = TextField()

    class Meta:
        table_name: str = "spip_signatures"


class SpipSyndic(BaseModel):
    date = DateTimeField(constraints=[SQL("DEFAULT '0000-00-00 00:00:00'")])
    date_index = DateTimeField(constraints=[SQL("DEFAULT '0000-00-00 00:00:00'")])
    date_syndic = DateTimeField(constraints=[SQL("DEFAULT '0000-00-00 00:00:00'")])
    descriptif = TextField()
    extra = TextField(null=True)
    id_rubrique = BigIntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    id_secteur = BigIntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    id_syndic = BigAutoField()
    maj = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    miroir = CharField(constraints=[SQL("DEFAULT 'non'")], null=True)
    moderation = CharField(constraints=[SQL("DEFAULT 'non'")], null=True)
    nom_site = TextField()
    oubli = CharField(constraints=[SQL("DEFAULT 'non'")], null=True)
    resume = CharField(constraints=[SQL("DEFAULT 'oui'")], null=True)
    statut = CharField(constraints=[SQL("DEFAULT '0'")])
    syndication = CharField(constraints=[SQL("DEFAULT ''")])
    url_site = TextField()
    url_syndic = TextField()

    class Meta:
        table_name: str = "spip_syndic"
        indexes = ((("statut", "date_syndic"), False),)


class SpipSyndicArticles(BaseModel):
    date = DateTimeField(constraints=[SQL("DEFAULT '0000-00-00 00:00:00'")])
    descriptif = TextField()
    id_syndic = BigIntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    id_syndic_article = BigAutoField()
    lang = CharField(constraints=[SQL("DEFAULT ''")])
    lesauteurs = TextField()
    maj = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    source = TextField()
    statut = CharField(constraints=[SQL("DEFAULT '0'")], index=True)
    tags = TextField()
    titre = TextField()
    url = TextField(index=True)
    url_source = TextField()

    class Meta:
        table_name: str = "spip_syndic_articles"


class SpipTest(BaseModel):
    a = IntegerField(null=True)

    class Meta:
        table_name: str = "spip_test"
        primary_key = False


class SpipTypesDocuments(BaseModel):
    descriptif = TextField()
    extension = CharField(constraints=[SQL("DEFAULT ''")], primary_key=True)
    inclus = CharField(constraints=[SQL("DEFAULT 'non'")], index=True)
    maj = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    media_defaut = CharField(constraints=[SQL("DEFAULT 'file'")])
    mime_type = CharField(constraints=[SQL("DEFAULT ''")])
    titre = TextField()
    upload = CharField(constraints=[SQL("DEFAULT 'oui'")])

    class Meta:
        table_name: str = "spip_types_documents"


class SpipUrls(BaseModel):
    date = DateTimeField(constraints=[SQL("DEFAULT '0000-00-00 00:00:00'")])
    id_objet = BigIntegerField()
    id_parent = BigIntegerField(constraints=[SQL("DEFAULT 0")])
    perma = IntegerField(constraints=[SQL("DEFAULT 0")])
    segments = IntegerField(constraints=[SQL("DEFAULT 1")])
    type = CharField(constraints=[SQL("DEFAULT 'article'")])
    url = CharField()

    class Meta:
        table_name: str = "spip_urls"
        indexes = (
            (("id_parent", "url"), True),
            (("type", "id_objet"), False),
        )
        primary_key = CompositeKey("id_parent", "url")


class SpipVersions(BaseModel):
    champs = TextField()
    date = DateTimeField(constraints=[SQL("DEFAULT '0000-00-00 00:00:00'")])
    id_auteur = CharField(constraints=[SQL("DEFAULT ''")])
    id_objet = BigIntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    id_version = BigIntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    objet = CharField(constraints=[SQL("DEFAULT ''")], index=True)
    permanent = CharField(constraints=[SQL("DEFAULT ''")])
    titre_version = TextField()

    class Meta:
        table_name: str = "spip_versions"
        indexes = ((("id_version", "id_objet", "objet"), True),)
        primary_key = CompositeKey("id_objet", "id_version", "objet")


class SpipVersionsFragments(BaseModel):
    compress = IntegerField()
    fragment = TextField(null=True)
    id_fragment = IntegerField(constraints=[SQL("DEFAULT 0")])
    id_objet = BigIntegerField(constraints=[SQL("DEFAULT 0")])
    objet = CharField(constraints=[SQL("DEFAULT ''")])
    version_max = IntegerField(constraints=[SQL("DEFAULT 0")])
    version_min = IntegerField(constraints=[SQL("DEFAULT 0")])

    class Meta:
        table_name: str = "spip_versions_fragments"
        indexes = ((("id_objet", "objet", "id_fragment", "version_min"), True),)
        primary_key = CompositeKey("id_fragment", "id_objet", "objet", "version_min")


class SpipVisites(BaseModel):
    date = DateField(primary_key=True)
    maj = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    visites = IntegerField(constraints=[SQL("DEFAULT 0")])

    class Meta:
        table_name: str = "spip_visites"


class SpipVisitesArticles(BaseModel):
    date = DateField()
    id_article = IntegerField()
    maj = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    visites = IntegerField(constraints=[SQL("DEFAULT 0")])

    class Meta:
        table_name: str = "spip_visites_articles"
        indexes = ((("date", "id_article"), True),)
        primary_key = CompositeKey("date", "id_article")


class SpipZones(BaseModel):
    descriptif = TextField()
    id_zone = BigAutoField()
    maj = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    privee = CharField(constraints=[SQL("DEFAULT 'non'")])
    publique = CharField(constraints=[SQL("DEFAULT 'oui'")])
    titre = CharField(constraints=[SQL("DEFAULT ''")])

    class Meta:
        table_name: str = "spip_zones"


class SpipZonesLiens(BaseModel):
    id_objet = BigIntegerField(constraints=[SQL("DEFAULT 0")])
    id_zone = BigIntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    objet = CharField(constraints=[SQL("DEFAULT ''")])

    class Meta:
        table_name: str = "spip_zones_liens"
        indexes = ((("id_zone", "id_objet", "objet"), True),)
        primary_key = CompositeKey("id_objet", "id_zone", "objet")
