# pyright: basic
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

db = MySQLDatabase(None)


# class UnknownField(object):
#     def __init__(self, *_, **__):
#         pass


class BaseModel(Model):
    class Meta:
        database: MySQLDatabase = db


class SpipArticles(BaseModel):
    accepter_forum: str = CharField(constraints=[SQL("DEFAULT ''")])
    chapo: str = TextField()
    date: str = DateTimeField(constraints=[SQL("DEFAULT '0000-00-00 00:00:00'")])
    date_modif: str = DateTimeField(constraints=[SQL("DEFAULT '0000-00-00 00:00:00'")])
    date_redac: str = DateTimeField(constraints=[SQL("DEFAULT '0000-00-00 00:00:00'")])
    descriptif: str = TextField()
    export: str = CharField(constraints=[SQL("DEFAULT 'oui'")], null=True)
    extra: str = TextField(null=True)
    id_article: int = BigAutoField()
    id_rubrique: int = BigIntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    id_secteur: int = BigIntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    id_trad: int = BigIntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    id_version: int = IntegerField(constraints=[SQL("DEFAULT 0")])
    lang: str = CharField(constraints=[SQL("DEFAULT ''")], index=True)
    langue_choisie: str = CharField(constraints=[SQL("DEFAULT 'non'")], null=True)
    maj: str = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    microblog: str = CharField(constraints=[SQL("DEFAULT ''")])
    nom_site: str = TextField()
    popularite: float = FloatField(constraints=[SQL("DEFAULT 0")])
    ps: str = TextField()
    referers: int = IntegerField(constraints=[SQL("DEFAULT 0")])
    soustitre: str = TextField()
    statut: str = CharField(constraints=[SQL("DEFAULT '0'")])
    surtitre: str = TextField()
    texte: str = TextField()
    titre: str = TextField()
    url_site: str = CharField(constraints=[SQL("DEFAULT ''")])
    virtuel: str = CharField(constraints=[SQL("DEFAULT ''")])
    visites: int = IntegerField(constraints=[SQL("DEFAULT 0")])

    class Meta:
        table_name: str = "spip_articles"
        indexes = ((("statut", "date"), False),)


class SpipAuteurs(BaseModel):
    alea_actuel: str = TextField()
    alea_futur: str = TextField()
    bio: str = TextField()
    cookie_oubli: str = TextField()
    email: str = TextField()
    en_ligne: str = DateTimeField(
        constraints=[SQL("DEFAULT '0000-00-00 00:00:00'")], index=True
    )
    extra: str = TextField(null=True)
    htpass: str = TextField()
    id_auteur: int = BigAutoField()
    imessage: str = CharField()
    lang: str = CharField(constraints=[SQL("DEFAULT ''")])
    login: str = CharField(index=True)
    low_sec: str = TextField()
    maj: str = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    messagerie: str = CharField()
    nom: str = TextField()
    nom_site: str = TextField()
    pass_: str = TextField(column_name="pass")
    pgp: str = TextField()
    prefs: str = TextField()
    source: str = CharField(constraints=[SQL("DEFAULT 'spip'")])
    statut: str = CharField(constraints=[SQL("DEFAULT '0'")], index=True)
    url_site: str = TextField()
    webmestre: str = CharField(constraints=[SQL("DEFAULT 'non'")])

    class Meta:
        table_name: str = "spip_auteurs"


class SpipAuteursLiens(BaseModel):
    id_auteur: int = BigIntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    id_objet: int = BigIntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    objet: str = CharField(constraints=[SQL("DEFAULT ''")], index=True)
    vu: str = CharField(constraints=[SQL("DEFAULT 'non'")])

    class Meta:
        table_name: str = "spip_auteurs_liens"
        indexes = ((("id_auteur", "id_objet", "objet"), True),)
        primary_key = CompositeKey("id_auteur", "id_objet", "objet")


class SpipBreves(BaseModel):
    date_heure: str = DateTimeField(constraints=[SQL("DEFAULT '0000-00-00 00:00:00'")])
    extra: str = TextField(null=True)
    id_breve: int = BigAutoField()
    id_rubrique: int = BigIntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    lang: str = CharField(constraints=[SQL("DEFAULT ''")])
    langue_choisie: str = CharField(constraints=[SQL("DEFAULT 'non'")], null=True)
    lien_titre: str = TextField()
    lien_url: str = TextField()
    maj: str = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    statut: str = CharField(constraints=[SQL("DEFAULT '0'")])
    texte: str = TextField()
    titre: str = TextField()

    class Meta:
        table_name: str = "spip_breves"


class SpipDepots(BaseModel):
    descriptif: str = TextField()
    id_depot: int = BigAutoField()
    maj: str = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    nbr_autres: int = IntegerField(constraints=[SQL("DEFAULT 0")])
    nbr_paquets: int = IntegerField(constraints=[SQL("DEFAULT 0")])
    nbr_plugins: int = IntegerField(constraints=[SQL("DEFAULT 0")])
    sha_paquets: str = CharField(constraints=[SQL("DEFAULT ''")])
    titre: str = TextField()
    type: str = CharField(constraints=[SQL("DEFAULT ''")])
    url_archives: str = CharField(constraints=[SQL("DEFAULT ''")])
    url_brouteur: str = CharField(constraints=[SQL("DEFAULT ''")])
    url_commits: str = CharField(constraints=[SQL("DEFAULT ''")])
    url_serveur: str = CharField(constraints=[SQL("DEFAULT ''")])
    xml_paquets: str = CharField(constraints=[SQL("DEFAULT ''")])

    class Meta:
        table_name: str = "spip_depots"


class SpipDepotsPlugins(BaseModel):
    id_depot: int = BigIntegerField()
    id_plugin: int = BigIntegerField()

    class Meta:
        table_name: str = "spip_depots_plugins"
        indexes = ((("id_depot", "id_plugin"), True),)
        primary_key = CompositeKey("id_depot", "id_plugin")


class SpipDocuments(BaseModel):
    brise: int = IntegerField(constraints=[SQL("DEFAULT 0")], null=True)
    credits: str = CharField(constraints=[SQL("DEFAULT ''")])
    date: str = DateTimeField(constraints=[SQL("DEFAULT '0000-00-00 00:00:00'")])
    date_publication: str = DateTimeField(
        constraints=[SQL("DEFAULT '0000-00-00 00:00:00'")]
    )
    descriptif: str = TextField()
    distant: str = CharField(constraints=[SQL("DEFAULT 'non'")], null=True)
    extension: str = CharField(constraints=[SQL("DEFAULT ''")], index=True)
    fichier: str = TextField()
    hauteur: int = IntegerField(null=True)
    id_document: int = BigAutoField()
    id_vignette: int = BigIntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    largeur: int = IntegerField(null=True)
    maj: str = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    media: str = CharField(constraints=[SQL("DEFAULT 'file'")])
    mode: str = CharField(constraints=[SQL("DEFAULT 'document'")], index=True)
    statut: str = CharField(constraints=[SQL("DEFAULT '0'")])
    taille: int = BigIntegerField(null=True)
    titre: str = TextField()

    class Meta:
        table_name: str = "spip_documents"


class SpipDocumentsLiens(BaseModel):
    id_document: int = BigIntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    id_objet: int = BigIntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    objet: str = CharField(constraints=[SQL("DEFAULT ''")], index=True)
    vu: str = CharField(constraints=[SQL("DEFAULT 'non'")])

    class Meta:
        table_name: str = "spip_documents_liens"
        indexes = ((("id_document", "id_objet", "objet"), True),)
        primary_key = CompositeKey("id_document", "id_objet", "objet")


class SpipEvenements(BaseModel):
    adresse: str = TextField()
    attendee: str = CharField(constraints=[SQL("DEFAULT ''")])
    date_creation: str = DateTimeField(
        constraints=[SQL("DEFAULT '0000-00-00 00:00:00'")]
    )
    date_debut: str = DateTimeField(
        constraints=[SQL("DEFAULT '0000-00-00 00:00:00'")], index=True
    )
    date_fin: str = DateTimeField(
        constraints=[SQL("DEFAULT '0000-00-00 00:00:00'")], index=True
    )
    descriptif: str = TextField()
    horaire: str = CharField(constraints=[SQL("DEFAULT 'oui'")])
    id_article: int = BigIntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    id_evenement: int = BigAutoField()
    id_evenement_source: int = BigIntegerField()
    inscription: int = IntegerField(constraints=[SQL("DEFAULT 0")])
    lieu: str = TextField()
    maj: str = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    notes: str = TextField()
    origin: str = CharField(constraints=[SQL("DEFAULT ''")])
    places: int = IntegerField(constraints=[SQL("DEFAULT 0")])
    statut: str = CharField(constraints=[SQL("DEFAULT '0'")])
    titre: str = TextField()

    class Meta:
        table_name: str = "spip_evenements"


class SpipEvenementsParticipants(BaseModel):
    date: str = DateTimeField(constraints=[SQL("DEFAULT '0000-00-00 00:00:00'")])
    email: str = TextField()
    id_auteur: int = BigIntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    id_evenement: int = BigIntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    id_evenement_participant: int = BigAutoField()
    nom: str = TextField()
    reponse: str = CharField(constraints=[SQL("DEFAULT '?'")])

    class Meta:
        table_name: str = "spip_evenements_participants"


class SpipForum(BaseModel):
    auteur: str = TextField()
    date_heure: str = DateTimeField(constraints=[SQL("DEFAULT '0000-00-00 00:00:00'")])
    date_thread: str = DateTimeField(constraints=[SQL("DEFAULT '0000-00-00 00:00:00'")])
    email_auteur: str = TextField()
    id_auteur: int = BigIntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    id_forum: int = BigAutoField()
    id_objet: int = BigIntegerField(constraints=[SQL("DEFAULT 0")])
    id_parent: int = BigIntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    id_thread: int = BigIntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    ip: str = CharField(constraints=[SQL("DEFAULT ''")])
    maj: str = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    nom_site: str = TextField()
    objet: str = CharField(constraints=[SQL("DEFAULT ''")])
    statut: str = CharField(constraints=[SQL("DEFAULT '0'")])
    texte: str = TextField()
    titre: str = TextField()
    url_site: str = TextField()

    class Meta:
        table_name: str = "spip_forum"
        indexes = ((("statut", "id_parent", "id_objet", "objet", "date_heure"), False),)


class SpipGroupesMots(BaseModel):
    comite: str = CharField(constraints=[SQL("DEFAULT ''")])
    descriptif: str = TextField()
    forum: str = CharField(constraints=[SQL("DEFAULT ''")])
    id_groupe: int = BigAutoField()
    maj: str = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    minirezo: str = CharField(constraints=[SQL("DEFAULT ''")])
    obligatoire: str = CharField(constraints=[SQL("DEFAULT ''")])
    tables_liees: str = TextField()
    texte: str = TextField()
    titre: str = TextField()
    unseul: str = CharField(constraints=[SQL("DEFAULT ''")])

    class Meta:
        table_name: str = "spip_groupes_mots"


class SpipJobs(BaseModel):
    args: str = TextField()
    date: str = DateTimeField(
        constraints=[SQL("DEFAULT '0000-00-00 00:00:00'")], index=True
    )
    descriptif: str = TextField()
    fonction: str = CharField()
    id_job: int = BigAutoField()
    inclure: str = CharField()
    md5args: str = CharField(constraints=[SQL("DEFAULT ''")])
    priorite: int = IntegerField(constraints=[SQL("DEFAULT 0")])
    status: int = IntegerField(constraints=[SQL("DEFAULT 1")], index=True)

    class Meta:
        table_name: str = "spip_jobs"


class SpipJobsLiens(BaseModel):
    id_job: int = BigIntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    id_objet: int = BigIntegerField(constraints=[SQL("DEFAULT 0")])
    objet: str = CharField(constraints=[SQL("DEFAULT ''")])

    class Meta:
        table_name: str = "spip_jobs_liens"
        indexes = ((("id_job", "id_objet", "objet"), True),)
        primary_key = CompositeKey("id_job", "id_objet", "objet")


class SpipMeslettres(BaseModel):
    date: str = DateTimeField(constraints=[SQL("DEFAULT '0000-00-00 00:00:00'")])
    id_malettre: int = BigAutoField()
    lang: str = CharField()
    titre: str = TextField()
    url_html: str = CharField(null=True)
    url_txt: str = CharField()

    class Meta:
        table_name: str = "spip_meslettres"


class SpipMessages(BaseModel):
    date_fin: str = DateTimeField(constraints=[SQL("DEFAULT '0000-00-00 00:00:00'")])
    date_heure: str = DateTimeField(constraints=[SQL("DEFAULT '0000-00-00 00:00:00'")])
    destinataires: str = TextField()
    id_auteur: int = BigIntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    id_message: int = BigAutoField()
    maj: str = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    rv: str = CharField(constraints=[SQL("DEFAULT ''")])
    statut: str = CharField(constraints=[SQL("DEFAULT '0'")])
    texte: str = TextField()
    titre: str = TextField()
    type: str = CharField(constraints=[SQL("DEFAULT ''")])

    class Meta:
        table_name: str = "spip_messages"


class SpipMeta(BaseModel):
    impt: str = CharField(constraints=[SQL("DEFAULT 'oui'")])
    maj: str = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    nom: str = CharField(primary_key=True)
    valeur: str = TextField(null=True)

    class Meta:
        table_name: str = "spip_meta"


class SpipMots(BaseModel):
    descriptif: str = TextField()
    extra: str = TextField(null=True)
    id_groupe: int = BigIntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    id_mot: int = BigAutoField()
    maj: str = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    texte: str = TextField()
    titre: str = TextField()
    type: str = TextField()

    class Meta:
        table_name: str = "spip_mots"


class SpipMotsLiens(BaseModel):
    id_mot: int = BigIntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    id_objet: int = BigIntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    objet: str = CharField(constraints=[SQL("DEFAULT ''")], index=True)

    class Meta:
        table_name: str = "spip_mots_liens"
        indexes = ((("id_mot", "id_objet", "objet"), True),)
        primary_key = CompositeKey("id_mot", "id_objet", "objet")


class SpipOrthoCache(BaseModel):
    lang: str = CharField()
    maj: str = DateTimeField(
        constraints=[SQL("DEFAULT current_timestamp()")], index=True
    )
    mot: str = CharField()
    ok: int = IntegerField()
    suggest: str = TextField()

    class Meta:
        table_name: str = "spip_ortho_cache"
        indexes = ((("lang", "mot"), True),)
        primary_key = CompositeKey("lang", "mot")


class SpipOrthoDico(BaseModel):
    id_auteur: int = BigIntegerField()
    lang: str = CharField()
    maj: str = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    mot: str = CharField()

    class Meta:
        table_name: str = "spip_ortho_dico"
        indexes = ((("lang", "mot"), True),)
        primary_key = CompositeKey("lang", "mot")


class SpipPaquets(BaseModel):
    actif: str = CharField(constraints=[SQL("DEFAULT 'non'")])
    attente: str = CharField(constraints=[SQL("DEFAULT 'non'")])
    auteur: str = TextField()
    branches_spip: str = CharField(constraints=[SQL("DEFAULT ''")])
    compatibilite_spip: str = CharField(constraints=[SQL("DEFAULT ''")])
    constante: str = CharField(constraints=[SQL("DEFAULT ''")])
    copyright: str = TextField()
    credit: str = TextField()
    date_crea: str = DateTimeField(constraints=[SQL("DEFAULT '0000-00-00 00:00:00'")])
    date_modif: str = DateTimeField(constraints=[SQL("DEFAULT '0000-00-00 00:00:00'")])
    dependances: str = TextField()
    description: str = TextField()
    etat: str = CharField(constraints=[SQL("DEFAULT ''")])
    etatnum: int = IntegerField(constraints=[SQL("DEFAULT 0")])
    id_depot: int = BigIntegerField(constraints=[SQL("DEFAULT 0")])
    id_paquet: int = BigAutoField()
    id_plugin: int = BigIntegerField(index=True)
    installe: str = CharField(constraints=[SQL("DEFAULT 'non'")])
    licence: str = TextField()
    lien_demo: str = TextField()
    lien_dev: str = TextField()
    lien_doc: str = TextField()
    logo: str = CharField(constraints=[SQL("DEFAULT ''")])
    maj_archive: str = DateTimeField(constraints=[SQL("DEFAULT '0000-00-00 00:00:00'")])
    maj_version: str = CharField(constraints=[SQL("DEFAULT ''")])
    nbo_archive: int = IntegerField(constraints=[SQL("DEFAULT 0")])
    nom_archive: str = CharField(constraints=[SQL("DEFAULT ''")])
    obsolete: str = CharField(constraints=[SQL("DEFAULT 'non'")])
    prefixe: str = CharField(constraints=[SQL("DEFAULT ''")])
    procure: str = TextField()
    recent: int = IntegerField(constraints=[SQL("DEFAULT 0")])
    signature: str = CharField(constraints=[SQL("DEFAULT ''")])
    src_archive: str = CharField(constraints=[SQL("DEFAULT ''")])
    superieur: str = CharField(constraints=[SQL("DEFAULT 'non'")])
    traductions: str = TextField()
    version: str = CharField(constraints=[SQL("DEFAULT ''")])
    version_base: str = CharField(constraints=[SQL("DEFAULT ''")])

    class Meta:
        table_name: str = "spip_paquets"


class SpipPetitions(BaseModel):
    email_unique: str = CharField(constraints=[SQL("DEFAULT ''")])
    id_article: int = BigIntegerField(constraints=[SQL("DEFAULT 0")], unique=True)
    id_petition: int = BigAutoField()
    maj: str = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    message: str = CharField(constraints=[SQL("DEFAULT ''")])
    site_obli: str = CharField(constraints=[SQL("DEFAULT ''")])
    site_unique: str = CharField(constraints=[SQL("DEFAULT ''")])
    statut: str = CharField(constraints=[SQL("DEFAULT 'publie'")])
    texte: str = TextField()

    class Meta:
        table_name: str = "spip_petitions"


class SpipPlugins(BaseModel):
    branches_spip: str = CharField(constraints=[SQL("DEFAULT ''")])
    categorie: str = CharField(constraints=[SQL("DEFAULT ''")])
    compatibilite_spip: str = CharField(constraints=[SQL("DEFAULT ''")])
    date_crea: str = DateTimeField(constraints=[SQL("DEFAULT '0000-00-00 00:00:00'")])
    date_modif: str = DateTimeField(constraints=[SQL("DEFAULT '0000-00-00 00:00:00'")])
    id_plugin: int = BigAutoField()
    nom: str = TextField()
    prefixe: str = CharField(constraints=[SQL("DEFAULT ''")], index=True)
    slogan: str = TextField()
    tags: str = TextField()
    vmax: str = CharField(constraints=[SQL("DEFAULT ''")])

    class Meta:
        table_name: str = "spip_plugins"


class SpipReferers(BaseModel):
    date: str = DateField()
    maj: str = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    referer: str = CharField(null=True)
    referer_md5: int = BigAutoField()
    visites: int = IntegerField()
    visites_jour: int = IntegerField(constraints=[SQL("DEFAULT 0")])
    visites_veille: int = IntegerField(constraints=[SQL("DEFAULT 0")])

    class Meta:
        table_name: str = "spip_referers"


class SpipReferersArticles(BaseModel):
    id_article: int = IntegerField()
    maj: str = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    referer: str = CharField(constraints=[SQL("DEFAULT ''")])
    referer_md5: int = BigIntegerField(index=True)
    visites: int = IntegerField()

    class Meta:
        table_name: str = "spip_referers_articles"
        indexes = ((("id_article", "referer_md5"), True),)
        primary_key = CompositeKey("id_article", "referer_md5")


class SpipResultats(BaseModel):
    id: int = IntegerField()
    maj: str = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    points: int = IntegerField(constraints=[SQL("DEFAULT 0")])
    recherche: str = CharField(constraints=[SQL("DEFAULT ''")])
    serveur: str = CharField(constraints=[SQL("DEFAULT ''")])
    table_objet: str = CharField(constraints=[SQL("DEFAULT ''")])

    class Meta:
        table_name: str = "spip_resultats"
        primary_key = False


class SpipRubriques(BaseModel):
    agenda: int = IntegerField(constraints=[SQL("DEFAULT 0")])
    date: str = DateTimeField(constraints=[SQL("DEFAULT '0000-00-00 00:00:00'")])
    date_tmp: str = DateTimeField(constraints=[SQL("DEFAULT '0000-00-00 00:00:00'")])
    descriptif: str = TextField()
    extra: str = TextField(null=True)
    id_parent: int = BigIntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    id_rubrique: int = BigAutoField()
    id_secteur: int = BigIntegerField(constraints=[SQL("DEFAULT 0")])
    id_trad: int = BigIntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    lang: str = CharField(constraints=[SQL("DEFAULT ''")], index=True)
    langue_choisie: str = CharField(constraints=[SQL("DEFAULT 'non'")], null=True)
    maj: str = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    profondeur: int = IntegerField(constraints=[SQL("DEFAULT 0")])
    statut: str = CharField(constraints=[SQL("DEFAULT '0'")])
    statut_tmp: str = CharField(constraints=[SQL("DEFAULT '0'")])
    texte: str = TextField()
    titre: str = TextField()

    class Meta:
        table_name: str = "spip_rubriques"


class SpipSignatures(BaseModel):
    ad_email: str = TextField()
    date_time: str = DateTimeField(constraints=[SQL("DEFAULT '0000-00-00 00:00:00'")])
    id_petition: int = BigIntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    id_signature: int = BigAutoField()
    maj: str = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    message: str = TextField()
    nom_email: str = TextField()
    nom_site: str = TextField()
    statut: str = CharField(constraints=[SQL("DEFAULT '0'")], index=True)
    url_site: str = TextField()

    class Meta:
        table_name: str = "spip_signatures"


class SpipSyndic(BaseModel):
    date: str = DateTimeField(constraints=[SQL("DEFAULT '0000-00-00 00:00:00'")])
    date_index: str = DateTimeField(constraints=[SQL("DEFAULT '0000-00-00 00:00:00'")])
    date_syndic: str = DateTimeField(constraints=[SQL("DEFAULT '0000-00-00 00:00:00'")])
    descriptif: str = TextField()
    extra: str = TextField(null=True)
    id_rubrique: int = BigIntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    id_secteur: int = BigIntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    id_syndic: int = BigAutoField()
    maj: str = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    miroir: str = CharField(constraints=[SQL("DEFAULT 'non'")], null=True)
    moderation: str = CharField(constraints=[SQL("DEFAULT 'non'")], null=True)
    nom_site: str = TextField()
    oubli: str = CharField(constraints=[SQL("DEFAULT 'non'")], null=True)
    resume: str = CharField(constraints=[SQL("DEFAULT 'oui'")], null=True)
    statut: str = CharField(constraints=[SQL("DEFAULT '0'")])
    syndication: str = CharField(constraints=[SQL("DEFAULT ''")])
    url_site: str = TextField()
    url_syndic: str = TextField()

    class Meta:
        table_name: str = "spip_syndic"
        indexes = ((("statut", "date_syndic"), False),)


class SpipSyndicArticles(BaseModel):
    date: str = DateTimeField(constraints=[SQL("DEFAULT '0000-00-00 00:00:00'")])
    descriptif: str = TextField()
    id_syndic: int = BigIntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    id_syndic_article: int = BigAutoField()
    lang: str = CharField(constraints=[SQL("DEFAULT ''")])
    lesauteurs: str = TextField()
    maj: str = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    source: str = TextField()
    statut: str = CharField(constraints=[SQL("DEFAULT '0'")], index=True)
    tags: str = TextField()
    titre: str = TextField()
    url: str = TextField(index=True)
    url_source: str = TextField()

    class Meta:
        table_name: str = "spip_syndic_articles"


class SpipTest(BaseModel):
    a: int = IntegerField(null=True)

    class Meta:
        table_name: str = "spip_test"
        primary_key = False


class SpipTypesDocuments(BaseModel):
    descriptif: str = TextField()
    extension: str = CharField(constraints=[SQL("DEFAULT ''")], primary_key=True)
    inclus: str = CharField(constraints=[SQL("DEFAULT 'non'")], index=True)
    maj: str = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    media_defaut: str = CharField(constraints=[SQL("DEFAULT 'file'")])
    mime_type: str = CharField(constraints=[SQL("DEFAULT ''")])
    titre: str = TextField()
    upload: str = CharField(constraints=[SQL("DEFAULT 'oui'")])

    class Meta:
        table_name: str = "spip_types_documents"


class SpipUrls(BaseModel):
    date: str = DateTimeField(constraints=[SQL("DEFAULT '0000-00-00 00:00:00'")])
    id_objet: int = BigIntegerField()
    id_parent: int = BigIntegerField(constraints=[SQL("DEFAULT 0")])
    perma: int = IntegerField(constraints=[SQL("DEFAULT 0")])
    segments: int = IntegerField(constraints=[SQL("DEFAULT 1")])
    type: str = CharField(constraints=[SQL("DEFAULT 'article'")])
    url: str = CharField()

    class Meta:
        table_name: str = "spip_urls"
        indexes = (
            (("id_parent", "url"), True),
            (("type", "id_objet"), False),
        )
        primary_key = CompositeKey("id_parent", "url")


class SpipVersions(BaseModel):
    champs: str = TextField()
    date: str = DateTimeField(constraints=[SQL("DEFAULT '0000-00-00 00:00:00'")])
    id_auteur: str = CharField(constraints=[SQL("DEFAULT ''")])
    id_objet: int = BigIntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    id_version: int = BigIntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    objet: str = CharField(constraints=[SQL("DEFAULT ''")], index=True)
    permanent: str = CharField(constraints=[SQL("DEFAULT ''")])
    titre_version: str = TextField()

    class Meta:
        table_name: str = "spip_versions"
        indexes = ((("id_version", "id_objet", "objet"), True),)
        primary_key = CompositeKey("id_objet", "id_version", "objet")


class SpipVersionsFragments(BaseModel):
    compress: int = IntegerField()
    fragment: str = TextField(null=True)
    id_fragment: int = IntegerField(constraints=[SQL("DEFAULT 0")])
    id_objet: int = BigIntegerField(constraints=[SQL("DEFAULT 0")])
    objet: str = CharField(constraints=[SQL("DEFAULT ''")])
    version_max: int = IntegerField(constraints=[SQL("DEFAULT 0")])
    version_min: int = IntegerField(constraints=[SQL("DEFAULT 0")])

    class Meta:
        table_name: str = "spip_versions_fragments"
        indexes = ((("id_objet", "objet", "id_fragment", "version_min"), True),)
        primary_key = CompositeKey("id_fragment", "id_objet", "objet", "version_min")


class SpipVisites(BaseModel):
    date: str = DateField(primary_key=True)
    maj: str = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    visites: int = IntegerField(constraints=[SQL("DEFAULT 0")])

    class Meta:
        table_name: str = "spip_visites"


class SpipVisitesArticles(BaseModel):
    date: str = DateField()
    id_article: int = IntegerField()
    maj: str = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    visites: int = IntegerField(constraints=[SQL("DEFAULT 0")])

    class Meta:
        table_name: str = "spip_visites_articles"
        indexes = ((("date", "id_article"), True),)
        primary_key = CompositeKey("date", "id_article")


class SpipZones(BaseModel):
    descriptif: str = TextField()
    id_zone: int = BigAutoField()
    maj: str = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    privee: str = CharField(constraints=[SQL("DEFAULT 'non'")])
    publique: str = CharField(constraints=[SQL("DEFAULT 'oui'")])
    titre: str = CharField(constraints=[SQL("DEFAULT ''")])

    class Meta:
        table_name: str = "spip_zones"


class SpipZonesLiens(BaseModel):
    id_objet: int = BigIntegerField(constraints=[SQL("DEFAULT 0")])
    id_zone: int = BigIntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    objet: str = CharField(constraints=[SQL("DEFAULT ''")])

    class Meta:
        table_name: str = "spip_zones_liens"
        indexes = ((("id_zone", "id_objet", "objet"), True),)
        primary_key = CompositeKey("id_objet", "id_zone", "objet")
