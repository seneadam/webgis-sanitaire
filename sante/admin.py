from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin
from django.utils.html import format_html

from .models import (
    TypeEtablissement,
    EtablissementSante,
    Population,
    Commune,
    Quartier,
)


@admin.register(TypeEtablissement)
class TypeEtablissementAdmin(admin.ModelAdmin):
    list_display = ['libelle', 'couleur_demo']
    search_fields = ['libelle']

    def couleur_demo(self, obj):
        """Affiche un aperçu de la couleur."""
        return format_html(
            '<span style="display:inline-block;'
            'width:30px;height:20px;'
            'background:{};border-radius:4px;"></span>',
            obj.couleur
        )

    couleur_demo.short_description = "Couleur"


@admin.register(EtablissementSante)
class EtablissementSanteAdmin(GISModelAdmin):
    """Administration des établissements de santé avec carte GIS."""

    list_display = [
        'nom',
        'type_etablissement',
        'statut_colore',
        'milieu',
        'telephone',
        'actif',
    ]

    list_filter = [
        'type_etablissement',
        'statut',
        'milieu',
        'actif',
    ]

    search_fields = [
        'nom',
        'telephone',
    ]

    fieldsets = (
        (
            'Informations générales',
            {
                'fields': (
                    'nom',
                    'type_etablissement',
                    'statut',
                    'milieu',
                    'actif',
                )
            },
        ),
        (
            'Localisation',
            {
                'fields': (
                    'geom',
                ),
                'description': (
                    "Position géographique de l'établissement."
                ),
            },
        ),
        (
            'Contact',
            {
                'fields': (
                    'telephone',
                    'email',
                ),
                'classes': ('collapse',),
            },
        ),
    )

    gis_widget_kwargs = {
        'attrs': {
            'map_width': 800,
            'map_height': 600,
            'default_lat': 14.8,
            'default_lon': -16.9,
            'default_zoom': 12,
        }
    }

    def statut_colore(self, obj):
        """Affiche le statut avec une couleur."""

        couleurs = {
            'PUB': '#28a745',
            'PRV': '#007bff',
            'COM': '#ffc107',
            'MIL': '#dc3545',
        }

        couleur = couleurs.get(
            obj.statut,
            '#6c757d'
        )

        return format_html(
            '<span style="background:{};'
            'color:white;'
            'padding:3px 8px;'
            'border-radius:12px;'
            'font-size:0.8em;">{}</span>',
            couleur,
            obj.get_statut_display()
        )

    statut_colore.short_description = "Statut"


@admin.register(Population)
class PopulationAdmin(admin.ModelAdmin):
    list_display = [
        'annee',
        'effectif_formate',
        'commune',
        'quartier',
    ]

    list_filter = ['annee']

    search_fields = [
        'commune__nom',
        'quartier__nom',
    ]

    ordering = [
        '-annee',
        'commune',
    ]

    def effectif_formate(self, obj):
        """Affiche la population avec séparateur de milliers."""

        if hasattr(obj, 'formatted_effectif'):
            return obj.formatted_effectif

        return obj.effectif

    effectif_formate.short_description = "Population"


@admin.register(Commune)
class CommuneAdmin(GISModelAdmin):
    list_display = [
        'nom',
    ]

    search_fields = [
        'nom',
    ]


@admin.register(Quartier)
class QuartierAdmin(GISModelAdmin):
    list_display = [
        'nom',
        'commune',
        'nb_etablissements',
    ]

    list_filter = [
        'commune',
    ]

    search_fields = [
        'nom',
    ]

    def nb_etablissements(self, obj):
        """Affiche le nombre d'établissements du quartier."""

        if hasattr(obj, 'nb_etablissements'):
            return obj.nb_etablissements

        return '-'

    nb_etablissements.short_description = "Établissements"