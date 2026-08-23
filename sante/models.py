"""
models.py — Cartographie sanitaire (périmètre : commune de Thiès Ouest)

Ce fichier a été restructuré pour coller aux colonnes réellement présentes
dans la table source "Infrastructure_sanitaire_thies_ouest" :

    id, geom, objectid, descriptif, reg, cod_reg, dept, cod_dept,
    cav, cod_cav, longitude, latitude, num_dept, num_cav, arr,
    millieu, typ_qvh, observatio, commune, num_commun, cod_commun,
    quartier, num_quarti, cod_quarti, statut_par

Le travail portant uniquement sur une seule commune, les niveaux
Région/Département de la source (reg, cod_reg, dept, cod_dept) ne sont
pas modélisés en tables séparées : ils ne varient pas dans ce périmètre.

-> descriptif        : type d'établissement (Clinique, Pharmacie, ...)
-> cav / cod_cav      : commune d'arrondissement / de ville (nom + code)
-> num_cav            : numéro de la CAV
-> arr                : arrondissement
-> millieu            : milieu (URBAIN / PERI / RURAL) de l'établissement
-> typ_qvh            : type de subdivision (QUARTIER / VILLAGE / HAMEAU)
-> observatio         : nom / observation de l'établissement
-> commune, cod_commun, num_commun : commune de rattachement
-> quartier, cod_quarti, num_quarti, statut_par : quartier de rattachement
   et son statut d'occupation (HABITEE / NON HABITEE)
-> objectid           : identifiant de l'objet dans le fichier source (SIG)
"""

from django.contrib.gis.db import models


class Commune(models.Model):
    nom = models.CharField(
        max_length=100,
        verbose_name="Nom de la commune"
    )

    code_commune = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Code commune"
    )

    numero_commune = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name="Numéro de la commune"
    )

    # "cav" = commune d'arrondissement / commune de ville dans la table source
    commune_arrondissement = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Commune d'arrondissement (CAV)"
    )

    code_commune_arrondissement = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Code CAV"
    )

    arrondissement = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Arrondissement"
    )

    geom = models.MultiPolygonField(
        srid=4326,
        blank=True,
        null=True,
        verbose_name="Limite de la commune"
    )

    class Meta:
        verbose_name = "Commune"
        verbose_name_plural = "Communes"
        ordering = ["nom"]

    def __str__(self):
        return self.nom


class Quartier(models.Model):
    STATUT_CHOICES = [
        ("HABITEE", "Habitée"),
        ("NON_HABITEE", "Non habitée"),
    ]

    TYPE_CHOICES = [
        ("QUARTIER", "Quartier"),
        ("VILLAGE", "Village"),
        ("HAMEAU", "Hameau"),
    ]

    nom = models.CharField(
        max_length=100,
        verbose_name="Nom du quartier"
    )

    code_quartier = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        verbose_name="Code quartier"
    )

    numero_quartier = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name="Numéro du quartier"
    )

    type_quartier = models.CharField(
        max_length=15,
        choices=TYPE_CHOICES,
        blank=True,
        null=True,
        verbose_name="Type (quartier/village/hameau)"
    )

    statut_occupation = models.CharField(
        max_length=15,
        choices=STATUT_CHOICES,
        blank=True,
        null=True,
        verbose_name="Statut d'occupation"
    )

    commune = models.ForeignKey(
        Commune,
        on_delete=models.CASCADE,
        related_name="quartiers",
        verbose_name="Commune"
    )

    geom = models.MultiPolygonField(
        srid=4326,
        blank=True,
        null=True,
        verbose_name="Limite du quartier"
    )

    class Meta:
        verbose_name = "Quartier"
        verbose_name_plural = "Quartiers"
        ordering = ["nom"]
        constraints = [
            models.UniqueConstraint(
                fields=["nom", "commune"],
                name="unique_quartier_commune"
            )
        ]

    def __str__(self):
        return f"{self.nom} ({self.commune.nom})"


# ---------------------------------------------------------------------------
# Types et établissements de santé
# ---------------------------------------------------------------------------

class TypeEtablissement(models.Model):
    libelle = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Type d'établissement"
    )

    class Meta:
        verbose_name = "Type d'établissement"
        verbose_name_plural = "Types d'établissements"
        ordering = ["libelle"]

    def __str__(self):
        return self.libelle

    @property
    def couleur(self):
        couleurs = {
            "Hôpital": "#FF0000",
            "Centre de santé": "#FF6B00",
            "Poste de santé": "#FFC107",
            "Clinique": "#2196F3",
            "Pharmacie": "#4CAF50",
            "Laboratoire": "#9C27B0",
            "Maternité": "#E91E63",
            "Dispensaire": "#795548",
            "Cabinet dentaire": "#00BCD4",
            "Cabinet médical": "#3F51B5",
        }

        return couleurs.get(self.libelle, "#607D8B")


class EtablissementSante(models.Model):

    MILIEU_CHOICES = [
        ("URBAIN", "Urbain"),
        ("PERI", "Péri-urbain"),
        ("RURAL", "Rural"),
    ]

    STATUT_CHOICES = [
        ("PUBLIC", "Public"),
        ("PRIVE", "Privé"),
        ("COMM", "Communautaire"),
        ("MIL", "Militaire"),
        ("AUTRE", "Autre"),
    ]

    # Identifiant de l'objet dans la couche SIG source (permet de ré-importer
    # / mettre à jour sans créer de doublons)
    objectid = models.BigIntegerField(
        unique=True,
        blank=True,
        null=True,
        verbose_name="ID objet SIG (source)"
    )

    # Identification
    nom = models.CharField(
        max_length=200,
        verbose_name="Nom de l'établissement"
    )

    type_etablissement = models.ForeignKey(
        TypeEtablissement,
        on_delete=models.PROTECT,
        related_name="etablissements",
        verbose_name="Type"
    )

    # Localisation administrative
    commune = models.ForeignKey(
        Commune,
        on_delete=models.CASCADE,
        related_name="etablissements",
        verbose_name="Commune"
    )

    quartier = models.ForeignKey(
        Quartier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="etablissements",
        verbose_name="Quartier"
    )

    milieu = models.CharField(
        max_length=10,
        choices=MILIEU_CHOICES,
        blank=True,
        null=True,
        verbose_name="Milieu"
    )

    # Statut
    statut = models.CharField(
        max_length=10,
        choices=STATUT_CHOICES,
        blank=True,
        null=True,
        verbose_name="Statut"
    )

    # Informations complémentaires
    observation = models.TextField(
        blank=True,
        verbose_name="Observation"
    )

    adresse = models.TextField(
        blank=True,
        verbose_name="Adresse"
    )

    telephone = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Téléphone"
    )

    email = models.EmailField(
        blank=True,
        verbose_name="Email"
    )

    # Coordonnées
    latitude = models.FloatField(
        verbose_name="Latitude"
    )

    longitude = models.FloatField(
        verbose_name="Longitude"
    )

    # Géométrie PostGIS
    geom = models.PointField(
        srid=4326,
        verbose_name="Localisation"
    )

    actif = models.BooleanField(
        default=True,
        verbose_name="Actif"
    )

    date_creation = models.DateTimeField(
        auto_now_add=True
    )

    date_modification = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name = "Établissement de santé"
        verbose_name_plural = "Établissements de santé"
        ordering = ["nom"]

        indexes = [
            models.Index(fields=["type_etablissement"]),
            models.Index(fields=["commune"]),
            models.Index(fields=["quartier"]),
            models.Index(fields=["statut"]),
            models.Index(fields=["objectid"]),
        ]

    def __str__(self):
        return self.nom

    @property
    def couleur(self):
        return self.type_etablissement.couleur


# ---------------------------------------------------------------------------
# Population
# ---------------------------------------------------------------------------

class Population(models.Model):

    annee = models.IntegerField(
        verbose_name="Année"
    )

    effectif = models.BigIntegerField(
        verbose_name="Population"
    )

    commune = models.ForeignKey(
        Commune,
        on_delete=models.CASCADE,
        related_name="populations",
        null=True,
        blank=True,
        verbose_name="Commune"
    )

    quartier = models.ForeignKey(
        Quartier,
        on_delete=models.CASCADE,
        related_name="populations",
        null=True,
        blank=True,
        verbose_name="Quartier"
    )

    class Meta:
        verbose_name = "Population"
        verbose_name_plural = "Populations"
        ordering = ["-annee"]

    def __str__(self):
        if self.quartier:
            lieu = self.quartier.nom
        elif self.commune:
            lieu = self.commune.nom
        else:
            lieu = "Inconnu"

        return f"{lieu} - {self.annee} : {self.effectif} habitants"