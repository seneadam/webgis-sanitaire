# import_data_correct.py
# -*- coding: utf-8 -*-
import os
import sys

# ============================================================
# CONFIGURATION GDAL
# ============================================================

QGIS_BIN = r"C:\Program Files\QGIS 4.0.3\bin"
QGIS_PROJ = r"C:\Program Files\QGIS 4.0.3\share\proj"
QGIS_GDAL_DATA = r"C:\Program Files\QGIS 4.0.3\share\gdal"

if os.name == "nt":
    if os.path.exists(QGIS_BIN):
        try:
            os.add_dll_directory(QGIS_BIN)
            os.environ["PATH"] = QGIS_BIN + os.pathsep + os.environ.get("PATH", "")
        except:
            pass
    
    if os.path.exists(QGIS_PROJ):
        os.environ["PROJ_LIB"] = QGIS_PROJ
        os.environ["PROJ_DATA"] = QGIS_PROJ
    
    if os.path.exists(QGIS_GDAL_DATA):
        os.environ["GDAL_DATA"] = QGIS_GDAL_DATA

GDAL_DLL = os.path.join(QGIS_BIN, "gdal313.dll")
GEOS_DLL = os.path.join(QGIS_BIN, "geos_c.dll")

if os.path.exists(GDAL_DLL):
    os.environ["GDAL_LIBRARY_PATH"] = GDAL_DLL
if os.path.exists(GEOS_DLL):
    os.environ["GEOS_LIBRARY_PATH"] = GEOS_DLL

# ============================================================
# CONFIGURATION DJANGO
# ============================================================

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

try:
    import django
    django.setup()
    print("✅ Django configuré avec succès")
except Exception as e:
    print(f"❌ Erreur de configuration Django: {e}")
    sys.exit(1)

# ============================================================
# IMPORT DES MODÈLES
# ============================================================

try:
    from django.contrib.gis.geos import Point
    from django.db import connection
    from sante.models import EtablissementSante, TypeEtablissement, Commune, Quartier
    print("✅ Modèles importés avec succès")
except Exception as e:
    print(f"❌ Erreur d'import des modèles: {e}")
    sys.exit(1)

# ============================================================
# DÉBUT DE L'IMPORT
# ============================================================

print("=" * 70)
print("IMPORT DES DONNÉES EXISTANTES")
print("=" * 70)

# -----------------------------------------------------------------
# Récupérer les données depuis la table source
# -----------------------------------------------------------------

try:
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                objectid,
                descriptif,
                longitude,
                latitude,
                millieu,
                observatio,
                quartier,
                statut_par,
                commune
            FROM "Infrastructure_sanitaire_thies_ouest"
            WHERE longitude IS NOT NULL 
            AND latitude IS NOT NULL
            AND descriptif IS NOT NULL
        """)
        
        rows = cursor.fetchall()
        print(f"📊 {len(rows)} enregistrements trouvés dans la table source")
        
        if len(rows) == 0:
            print("⚠️ Aucune donnée trouvée !")
            sys.exit(0)
            
except Exception as e:
    print(f"❌ Erreur de lecture de la table source: {e}")
    sys.exit(1)

# -----------------------------------------------------------------
# Créer ou récupérer la commune
# -----------------------------------------------------------------

try:
    commune, created = Commune.objects.get_or_create(
        nom="THIES OUEST",
        defaults={"code_commune": "07230122"}
    )
    print(f"✓ Commune: {commune.nom} ({'créée' if created else 'existante'})")
except Exception as e:
    print(f"❌ Erreur de création de la commune: {e}")
    sys.exit(1)

# -----------------------------------------------------------------
# Importer les données
# -----------------------------------------------------------------

types_cache = {}
quartiers_cache = {}
count_imported = 0
count_skipped = 0
count_errors = 0

print("\n📌 Importation en cours...\n")

for row in rows:
    try:
        objectid, descriptif, longitude, latitude, millieu, observatio, quartier_nom, statut_par, commune_nom = row
        
        # Nettoyer les données
        if not descriptif:
            descriptif = "Autre"
        if not observatio:
            observatio = "Sans nom"
        
        nom = observatio.strip()[:200]
        type_libelle = descriptif.strip()
        
        # Nettoyer le milieu
        milieu_map = {
            'URBAIN': 'URBAIN',
            'PERI': 'PERI', 
            'RURAL': 'RURAL',
            'URE': 'URBAIN',
            'URB': 'URBAIN',
            'RUR': 'RURAL'
        }
        milieu = milieu_map.get(millieu, 'URBAIN') if millieu else 'URBAIN'
        
        # Nettoyer le statut
        statut = 'AUTRE'
        if statut_par:
            statut_upper = str(statut_par).upper()
            if 'PUBLIC' in statut_upper:
                statut = 'PUBLIC'
            elif 'PRIVE' in statut_upper:
                statut = 'PRIVE'
            elif 'COMM' in statut_upper:
                statut = 'COMM'
            elif 'MIL' in statut_upper:
                statut = 'MIL'
        
        # --- Récupérer ou créer le type d'établissement ---
        if type_libelle not in types_cache:
            type_obj, created = TypeEtablissement.objects.get_or_create(
                libelle=type_libelle
            )
            types_cache[type_libelle] = type_obj
            if created:
                print(f"  ✓ Nouveau type: {type_libelle}")
        type_obj = types_cache[type_libelle]
        
        # --- Récupérer ou créer le quartier ---
        quartier_obj = None
        if quartier_nom:
            quartier_nom_clean = quartier_nom.strip()
            quartier_key = f"{quartier_nom_clean}_{commune.id}"
            if quartier_key not in quartiers_cache:
                quartier_obj, created = Quartier.objects.get_or_create(
                    nom=quartier_nom_clean,
                    commune=commune
                )
                quartiers_cache[quartier_key] = quartier_obj
                if created:
                    print(f"  ✓ Nouveau quartier: {quartier_nom_clean}")
            else:
                quartier_obj = quartiers_cache[quartier_key]
        
        # --- Vérifier si l'établissement existe déjà ---
        existing = None
        if objectid:
            existing = EtablissementSante.objects.filter(objectid=objectid).first()
        
        if not existing and observatio:
            existing = EtablissementSante.objects.filter(
                nom=nom,
                latitude=float(latitude),
                longitude=float(longitude)
            ).first()
        
        if existing:
            print(f"  ⏩ Déjà existant: {nom}")
            count_skipped += 1
            continue
        
        # --- Créer l'établissement ---
        point = Point(float(longitude), float(latitude), srid=4326)
        
        etab = EtablissementSante(
            objectid=int(objectid) if objectid else None,
            nom=nom,
            type_etablissement=type_obj,
            commune=commune,
            quartier=quartier_obj,
            latitude=float(latitude),
            longitude=float(longitude),
            geom=point,
            milieu=milieu,
            statut=statut,
            observation=f"Importé depuis la table source - Type: {type_libelle}",
            actif=True
        )
        etab.save()
        count_imported += 1
        print(f"  ✅ {nom} ({type_libelle})")
        
    except Exception as e:
        print(f"  ❌ Erreur pour {nom}: {e}")
        count_errors += 1

# -----------------------------------------------------------------
# Résumé
# -----------------------------------------------------------------

print("\n" + "=" * 70)
print("RÉSUMÉ DE L'IMPORTATION")
print("=" * 70)
print(f"✅ Établissements importés  : {count_imported}")
print(f"⏩ Établissements ignorés   : {count_skipped} (déjà existants)")
print(f"❌ Erreurs                  : {count_errors}")
print(f"📊 Total dans la base      : {EtablissementSante.objects.count()}")
print("=" * 70)

# -----------------------------------------------------------------
# Vérification des données
# -----------------------------------------------------------------

print("\n📋 Aperçu des données importées:")
try:
    for etab in EtablissementSante.objects.all()[:10]:
        print(f"  - {etab.nom} : {etab.type_etablissement.libelle} @ ({etab.latitude}, {etab.longitude})")
    
    if EtablissementSante.objects.count() > 10:
        print(f"  ... et {EtablissementSante.objects.count() - 10} autres")
        
except Exception as e:
    print(f"  ❌ Erreur d'affichage: {e}")

print("\n" + "=" * 70)
print("✅ Importation terminée !")
print("=" * 70)