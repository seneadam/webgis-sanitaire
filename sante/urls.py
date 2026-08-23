from django.urls import path
from . import views

app_name = 'sante'

urlpatterns = [
    # Pages principales
    path('', views.accueil, name='accueil'),
    path('carte/', views.carte, name='carte'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # API
    path('api/etablissements/', views.api_etablissements, name='api_etablissements'),
    path('api/export/', views.export_donnees, name='export_donnees'),
    
    # Contribution
    path('contribution/', views.contribution, name='contribution'),
    path('contribution/signaler/', views.signaler, name='signaler'),
]