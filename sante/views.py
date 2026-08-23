from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.db.models import Count
import json
import csv

from .models import EtablissementSante, TypeEtablissement, Quartier, Commune


# ============================================================
# PAGES PRINCIPALES
# ============================================================

def accueil(request):
    """Page d'accueil"""
    nb_etablissements = EtablissementSante.objects.count()
    nb_types = TypeEtablissement.objects.count()
    nb_quartiers = Quartier.objects.count()
    
    context = {
        'nb_etablissements': nb_etablissements,
        'nb_types': nb_types,
        'nb_quartiers': nb_quartiers,
        'population': '150 000',
    }
    # ✅ Utilise "accueil.html" (dans sante/templates/)
    return render(request, "accueil.html", context)


def carte(request):
    """Page de la carte sanitaire"""
    types = TypeEtablissement.objects.all()
    nb_etablissements = EtablissementSante.objects.count()
    context = {
        'types_list': types,
        'nb_etablissements': nb_etablissements,
    }
    # ✅ Utilise "carte.html" (dans sante/templates/)
    return render(request, "carte.html", context)


def dashboard(request):
    """Tableau de bord avec statistiques"""
    
    # --- Statistiques générales ---
    nb_etablissements = EtablissementSante.objects.count()
    nb_types = TypeEtablissement.objects.count()
    nb_quartiers = Quartier.objects.count()
    
    # --- Statistiques par type ---
    statistiques = EtablissementSante.objects.values(
        'type_etablissement__libelle'
    ).annotate(
        nombre=Count('id')
    ).order_by('-nombre')
    
    # Ajouter la couleur à chaque statistique
    for stat in statistiques:
        type_obj = TypeEtablissement.objects.filter(
            libelle=stat['type_etablissement__libelle']
        ).first()
        stat['couleur'] = type_obj.couleur if type_obj else '#0d6efd'
    
    # --- Statistiques par statut ---
    statistiques_statut = EtablissementSante.objects.values('statut').annotate(
        nombre=Count('id')
    ).order_by('-nombre')
    
    # --- Statistiques par quartier ---
    statistiques_quartier = EtablissementSante.objects.values(
        'quartier__nom'
    ).annotate(
        nombre=Count('id')
    ).order_by('-nombre')[:10]
    
    # --- Statistiques par milieu ---
    statistiques_milieu = EtablissementSante.objects.values('milieu').annotate(
        nombre=Count('id')
    ).order_by('-nombre')
    
    # --- Compteurs publics/privés ---
    nb_public = EtablissementSante.objects.filter(statut='PUBLIC').count()
    nb_prive = EtablissementSante.objects.filter(statut='PRIVE').count()
    
    # Ratio public/privé
    ratio_public_prive = round(nb_public / nb_prive, 1) if nb_prive > 0 else nb_public
    
    # Pourcentage public
    ratio_public = round((nb_public / nb_etablissements) * 100, 0) if nb_etablissements > 0 else 0
    
    # --- Population ---
    population = 150000
    densite = 1500
    ratio_pop_etab = round(population / nb_etablissements, 0) if nb_etablissements > 0 else 0
    
    # --- Tous les établissements pour le tableau ---
    etablissements = EtablissementSante.objects.select_related(
        'type_etablissement', 'commune', 'quartier'
    )[:100]
    
    # --- Types pour les filtres ---
    types_list = TypeEtablissement.objects.all()
    
    # --- Zones sous-équipées ---
    zones_sous_equipees_list = []
    
    context = {
        # Statistiques générales
        'nb_etablissements': nb_etablissements,
        'nb_types': nb_types,
        'nb_quartiers': nb_quartiers,
        'nb_public': nb_public,
        'nb_prive': nb_prive,
        'ratio_public': ratio_public,
        'ratio_public_prive': ratio_public_prive,
        
        # Population
        'population': population,
        'densite': densite,
        'ratio_pop_etab': ratio_pop_etab,
        
        # Statistiques détaillées
        'statistiques': statistiques,
        'statistiques_statut': statistiques_statut,
        'statistiques_quartier': statistiques_quartier,
        'statistiques_milieu': statistiques_milieu,
        
        # Données pour les tableaux
        'etablissements': etablissements,
        'types_list': types_list,
        
        # Indicateurs
        'annee_actuelle': 2026,
        'couverture_globale': 85,
        'nb_quartiers_couverts': nb_quartiers,
        'zones_sous_equipees': 0,
        'zones_sous_equipees_list': zones_sous_equipees_list,
        'temps_acces_moyen': 12.5,
        'nb_lits': 350,
        'ratio_lits_pop': 2.3,
        'couverture_urbaine': 90,
        'couverture_rurale': 70,
    }
    
    # ✅ Utilise "dashboard.html" (dans sante/templates/)
    return render(request, "dashboard.html", context)


# ============================================================
# API
# ============================================================

def api_etablissements(request):
    """API GeoJSON des établissements"""
    try:
        etablissements = EtablissementSante.objects.select_related(
            'type_etablissement', 'commune', 'quartier'
        )
        
        features = []
        for etab in etablissements:
            if etab.latitude and etab.longitude:
                type_libelle = etab.type_etablissement.libelle if etab.type_etablissement else "Inconnu"
                
                # Normaliser les noms
                if type_libelle == "Poste de santÃ©":
                    type_libelle = "Poste de santé"
                elif type_libelle == "Centre de santÃ©":
                    type_libelle = "Centre de santé"
                elif type_libelle == "Hopital":
                    type_libelle = "Hôpital"
                
                feature = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [float(etab.longitude), float(etab.latitude)]
                    },
                    "properties": {
                        "id": etab.id,
                        "nom": etab.nom,
                        "type": type_libelle,
                        "commune": etab.commune.nom if etab.commune else "Inconnue",
                        "quartier": etab.quartier.nom if etab.quartier else "",
                        "milieu": etab.get_milieu_display() if etab.milieu else "",
                        "statut": etab.get_statut_display() if etab.statut else "Non défini",
                        "observation": etab.observation or "",
                        "telephone": etab.telephone or "",
                        "email": etab.email or "",
                        "latitude": float(etab.latitude),
                        "longitude": float(etab.longitude),
                        "couleur": etab.type_etablissement.couleur if etab.type_etablissement else "#0d6efd",
                        "actif": etab.actif
                    }
                }
                features.append(feature)
        
        data = {
            "type": "FeatureCollection",
            "features": features
        }
        
        return JsonResponse(data, safe=False)
        
    except Exception as e:
        return JsonResponse({
            "type": "FeatureCollection",
            "features": [],
            "error": str(e)
        }, status=500)


# ============================================================
# EXPORT DE DONNÉES
# ============================================================

def export_donnees(request):
    """Export des données au format GeoJSON ou CSV"""
    format_type = request.GET.get('format', 'geojson')
    
    etablissements = EtablissementSante.objects.select_related(
        'type_etablissement', 'commune', 'quartier'
    )
    
    if format_type == 'geojson':
        data = {
            "type": "FeatureCollection",
            "features": []
        }
        
        for etab in etablissements:
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [etab.longitude, etab.latitude]
                },
                "properties": {
                    "id": etab.id,
                    "nom": etab.nom,
                    "type": etab.type_etablissement.libelle,
                    "commune": etab.commune.nom,
                    "quartier": etab.quartier.nom if etab.quartier else "",
                    "statut": etab.get_statut_display(),
                    "milieu": etab.get_milieu_display() if etab.milieu else "",
                    "observation": etab.observation,
                    "telephone": etab.telephone,
                    "email": etab.email,
                    "latitude": etab.latitude,
                    "longitude": etab.longitude
                }
            }
            data["features"].append(feature)
        
        response = JsonResponse(data, safe=False)
        response['Content-Disposition'] = 'attachment; filename=etablissements.geojson'
        return response
    
    elif format_type == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=etablissements.csv'
        
        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Nom', 'Type', 'Commune', 'Quartier', 
            'Statut', 'Milieu', 'Téléphone', 'Email', 
            'Latitude', 'Longitude'
        ])
        
        for etab in etablissements:
            writer.writerow([
                etab.id,
                etab.nom,
                etab.type_etablissement.libelle,
                etab.commune.nom,
                etab.quartier.nom if etab.quartier else '',
                etab.get_statut_display(),
                etab.get_milieu_display() if etab.milieu else '',
                etab.telephone,
                etab.email,
                etab.latitude,
                etab.longitude
            ])
        
        return response
    
    else:
        return JsonResponse({'error': 'Format non supporté'}, status=400)


# ============================================================
# CONTRIBUTION CITOYENNE
# ============================================================

def contribution(request):
    """Page de contribution citoyenne"""
    return render(request, 'contribution.html')


def signaler(request):
    """Page de signalement citoyen"""
    etablissement_id = request.GET.get('etablissement')
    etablissement = None
    
    if etablissement_id:
        try:
            etablissement = EtablissementSante.objects.get(id=etablissement_id)
        except EtablissementSante.DoesNotExist:
            pass
    
    context = {
        'etablissement': etablissement,
    }
    
    if request.method == 'POST':
        messages.success(request, 'Merci pour votre signalement !')
        return render(request, 'contribution.html', context)
    
    return render(request, 'contribution.html', context)