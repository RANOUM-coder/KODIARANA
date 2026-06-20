from django.urls import path
from . import views

urlpatterns = [
    # 1-PATH HO AN'NY ACCUEIL :
    path('', views.accueil, name='accueil'),
    
    # 2-PATH HO AN'NY CLIENT :
    path('clients/', views.client_list, name='client_list'),
    path('clients/add/', views.client_create, name='client_add'),
    path('clients/<int:id>/edit/', views.client_edit, name='client_edit'),
    path('clients/<int:id>/delete/', views.client_delete, name='client_delete'),
    
    # 3-PATH HO AN'NY MOTO :
    path('motos/', views.moto_list, name='moto_list'),
    path('motos/add/', views.moto_create, name='moto_add'),
    path('motos/<int:id>/edit/', views.moto_edit, name='moto_edit'),
    path('motos/<int:id>/delete/', views.moto_delete, name='moto_delete'),

    # 4-PATH HO AN'NY MOTOS CLIENT :
    path('portal/motos/', views.client_motos, name='client_motos'),
    path('portal/motos/add/', views.client_moto_add, name='client_moto_add'),
    path('portal/motos/<int:id>/delete/', views.client_moto_delete, name='client_moto_delete'),

    # 5-PATH HO AN'NY REPARATION :
    path('reparations/', views.reparation_list, name='reparation_list'),
    path('reparations/add/', views.reparation_create, name='reparation_add'),
    path('reparations/<int:id>/', views.reparation_detail, name='reparation_detail'),
    path('reparations/<int:id>/edit/', views.reparation_edit, name='reparation_edit'),
    path('reparations/<int:id>/delete/', views.reparation_delete, name='reparation_delete'),

    # 6-PATH HO AN'NY REPARATION RENDEZ-VOUS ADMIN :
    path('reparations/rendezvous/', views.rendezvous_list, name='rendezvous_list'),
    path('reparations/rendezvous/<int:id>/edit/', views.rendezvous_edit, name='rendezvous_edit'),
    path('reparations/rendezvous/<int:id>/valider/', views.valider_rdv, name='valider_rdv'),
    path('reparations/rendezvous/<int:id>/rejeter/', views.rejeter_rdv, name='rejeter_rdv'),

    # 7-PATH HO AN'NY PAIEMENT REPARATION :
    path('reparations/<int:reparation_id>/paiement/', views.paiement_reparation_create, name='paiement_reparation_create'),

    # 8-PATH HO AN'NY PIECES :
    path('pieces/', views.piece_list, name='piece_list'),
    path('pieces/add/', views.piece_create, name='piece_add'),
    path('pieces/<int:id>/edit/', views.piece_edit, name='piece_edit'),
    path('pieces/<int:id>/delete/', views.piece_delete, name='piece_delete'),

    # 9-PATH HO AN'NY COMMANDES :
    path('commandes/', views.commande_list, name='commande_list'),
    path('commandes/add/', views.commande_create, name='commande_add'),
    path('commandes/<int:id>/edit/', views.commande_edit, name='commande_edit'),
    path('commandes/<int:id>/delete/', views.commande_delete, name='commande_delete'),
    path('commandes/<int:id>/', views.commande_detail, name='commande_detail'),
    path('commandes/<int:commande_id>/paiement/', views.paiement_create, name='paiement_create'),

    # 10-PATH HO AN'NY AUTH :
    path('accounts/login/', views.login_view, name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
    path('accounts/register/', views.register_view, name='register'),

    # 11-PATH HO AN'NY CLIENT PORTAL :
    path('portal/', views.client_portal, name='client_portal'),
    path('portal/commandes/', views.client_orders, name='client_orders'),
    path('portal/reparations/', views.client_repairs, name='client_repairs'),
    path('portal/rendezvous/', views.client_rendezvous, name='client_rendezvous'),
    path('portal/catalogue/', views.client_catalogue, name='client_catalogue'),

    # 12-PATH HO AN'NY CATALOGUE & PANIER :
    path('catalogue/', views.catalogue_pieces, name='catalogue_pieces'),
    path('catalogue/piece/<int:id>/', views.piece_detail, name='piece_detail'),
    path('panier/', views.voir_panier, name='voir_panier'),
    path('panier/ajouter/<int:piece_id>/', views.ajouter_au_panier, name='ajouter_au_panier'),
    path('panier/retirer/<int:ligne_id>/', views.retirer_du_panier, name='retirer_du_panier'),
    path('panier/valider/', views.valider_panier, name='valider_panier'),

    # 13-PATH HO AN'NY PROFIL :
    path('profil/', views.profil_utilisateur, name='profil_utilisateur'),

    # 14-PATH HO AN'NY TEMOIGNAGE :
    path('temoignages/', views.temoignage_list, name='temoignage_list'),
    path('temoignages/nouveau/', views.temoignage_create, name='temoignage_create'),
    path('temoignages/merci/', views.temoignage_merci, name='temoignage_merci'),
    path('temoignages/<int:id>/activer/', views.temoignage_activer, name='temoignage_activer'),
    path('temoignages/<int:id>/desactiver/', views.temoignage_desactiver, name='temoignage_desactiver'),
    path('temoignages/<int:id>/delete/', views.temoignage_delete, name='temoignage_delete'),

    # 15-PATH HO AN'NY A PROPOS :
    path('a-propos/', views.a_propos, name='a_propos'),

    # 16-PATH HO AN'NY SERVICES & CONTACT :
    path('services/', views.services, name='services'),
    path('contact/', views.contact, name='contact'),

    # PATH HO AN'NY TOUS LES TEMOIGNAGES :
    path('temoignages/tous/', views.tous_temoignages, name='tous_temoignages'),

]