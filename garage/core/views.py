from urllib import request

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.utils.dateparse import parse_datetime
from decimal import Decimal
import os
from .forms import CustomUserCreationForm
from .models import (Client, Moto, Piece, Commande, Reparation, LigneCommande, 
                     Paiement, PaiementReparation, Panier, LignePanier, Profil, Temoignage)
from django.contrib import messages 
from django.utils.timezone import now, make_aware
from datetime import datetime, timedelta


# -----------------------1-ETO NY VIEWS HO AN'NY ACCUEIL:---------------------


def render_with_active(request, template, context, active_page):
    data = {**context, 'active_page': active_page}
    if request.user.is_authenticated and not request.user.is_staff:
        panier, created = Panier.objects.get_or_create(utilisateur=request.user)
        data['panier_items_count'] = panier.total_items()

        try:
            profil = Profil.objects.filter(utilisateur=request.user).first()
            if profil and profil.photo_profil and os.path.exists(profil.photo_profil.path):
                data['profile_photo_url'] = profil.photo_profil.url
            else:
                data['profile_photo_url'] = None
        except Exception:
            data['profile_photo_url'] = None
    return render(request, template, data)




def accueil(request):
    clients_count    = Client.objects.count()
    motos_count      = Moto.objects.count()
    pieces_count     = Piece.objects.count()
    commandes_count  = Commande.objects.count()
    reparations_count = Reparation.objects.count()
    temoignages      = Temoignage.objects.filter(statut='actif')[:3]
    temoignages_count = Temoignage.objects.filter(statut='actif').count()
    pieces_populaires = Piece.objects.filter(stock__gt=0)[:4] 

    context = {
        'clients_count':     clients_count,
        'motos_count':       motos_count,
        'pieces_count':      pieces_count,
        'commandes_count':   commandes_count,
        'reparations_count': reparations_count,
        'temoignages':       temoignages,
        'temoignages_count': temoignages_count,
        'pieces_populaires': pieces_populaires,
    }
    return render_with_active(request, 'core/accueil.html', context, 'accueil')

# ----------------------- 2-ETO NY VIEWS HO AN'NY AUTH:---------------------

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        form.fields['username'].label = 'Email'
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.is_staff:
                return redirect('accueil')
            return redirect('client_portal')
    else:
        form = AuthenticationForm()
        form.fields['username'].label = 'Email'
    return render_with_active(request, 'core/login.html', {'form': form}, 'login')
    
    
def logout_view(request):
    logout(request)
    return redirect('accueil')


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Client.objects.create(
                user=user,
                nom=form.cleaned_data['nom'],
                email=user.email,
                telephone=''
            )
            login(request, user)
            return redirect('client_portal')
    else:
        form = CustomUserCreationForm()
    return render_with_active(request, 'core/register.html', {'form': form}, 'register')

# @login_required : VIEWS EFA VOATOKANA HO AN'NY CLIENT INSCRIT, ARY CLIENT PORTAL NO MITONDRA NY PATH-NY AO AMIN'NY URLS AO ==>

@login_required(login_url='login')
def client_portal(request):
    # ⚠️ AJOUTER MESSAGE DE BIENVENUE (première connexion)
    if not request.session.get('welcome_shown', False):
        messages.info(request, 'Bienvenue sur votre espace client KODIARANA !')
        request.session['welcome_shown'] = True
    
    temoignages = Temoignage.objects.filter(statut='actif')[:3]
    temoignages_count = Temoignage.objects.filter(statut='actif').count()
    pieces_populaires = Piece.objects.filter(stock__gt=0)[:4]
    context = {
        'temoignages': temoignages,
        'temoignages_count': temoignages_count,
        'pieces_populaires': pieces_populaires,
    }
    return render_with_active(request, 'core/client_portal.html', context, 'client_portal')

    
@login_required(login_url='login')
def client_orders(request):
    client = Client.objects.filter(user=request.user).first()
    if client:
        commandes = Commande.objects.select_related('client').filter(client=client)
    else:
        commandes = Commande.objects.none()
    return render_with_active(request, 'core/client_orders.html', {'commandes': commandes}, 'client_orders')


@login_required(login_url='login')
def client_repairs(request):
    client = Client.objects.filter(user=request.user).first()
    if client:
        reparations = Reparation.objects.select_related('moto').prefetch_related('pieces').filter(moto__Client=client)
    else:
        reparations = Reparation.objects.none()
    return render_with_active(request, 'core/client_repairs.html', {'reparations': reparations}, 'client_repairs')


@login_required(login_url='login')
def client_catalogue(request):
    pieces = Piece.objects.all()
    return render_with_active(request, 'core/client_catalogue.html', {'pieces': pieces}, 'client_catalogue')


# ----------------------- 3-ETO NY VIEWS HO AN'NY A PROPOS:---------------------

def a_propos(request):
    return render_with_active(request, 'core/a_propos.html', {}, 'a_propos')

# ----------------------- 4-ETO NY VIEWS HO AN'NY RENDEZ-VOUS:---------------------



@login_required(login_url='login')
def client_rendezvous(request):
    client = Client.objects.filter(user=request.user).first()
    if not client:
        return redirect('profil_utilisateur')

    motos = Moto.objects.filter(Client=client)

    if request.method == 'POST':
        moto_id = request.POST.get('moto')
        description = request.POST.get('description', '').strip()
        date_rendezvous_str = request.POST.get('date_rendezvous')
        telephone = request.POST.get('telephone', '').strip() or client.telephone

        # ========== SÉCURISATION DATE ==========
        try:
            date_rendezvous = datetime.fromisoformat(date_rendezvous_str)
        except:
            messages.error(request, "Format de date invalide.")
            return redirect('client_rendezvous')

        # Rendre la date "aware" comme Django
        if not date_rendezvous.tzinfo:
            date_rendezvous = make_aware(date_rendezvous)

        maintenant = now()
        date_limite = maintenant + timedelta(days=30)

        # ❌ 1. Pas dans le passé
        if date_rendezvous < maintenant:
            messages.error(request, "❌ Vous ne pouvez pas prendre un rendez-vous dans le passé.")
            return redirect('client_rendezvous')

        # ❌ 2. Pas trop loin (max 30 jours)
        if date_rendezvous > date_limite:
            messages.error(request, "📅 Vous pouvez réserver jusqu’à 30 jours à l’avance maximum.")
            return redirect('client_rendezvous')

        # éviter doublon de RDV pour cette moto
        deja_rdv = Reparation.objects.filter(
            moto_id=moto_id,
            statut__in=['rendez_vous', 'en attente', 'en cours']
        ).exists()

        if deja_rdv:
            messages.warning(request, "⚠️ Cette moto a déjà un rendez-vous en attente. Patientez.")
            return redirect('client_rendezvous')

        # ========== CRÉATION RDV ==========
        moto = get_object_or_404(Moto, id=moto_id, Client=client)

        Reparation.objects.create(
            moto=moto,
            description=description or 'Demande de rendez-vous',
            montant_total=0,
            statut='rendez_vous',
            date_rendezvous=date_rendezvous,
            telephone=telephone,
        )

        messages.success(request, "✅ Votre demande de rendez-vous a bien été envoyée. L’atelier vous confirmera rapidement.")
        return redirect('client_repairs')

    return render_with_active(request, 'core/rendezvous_form.html', {
        'motos': motos,
        'client': client,
    }, 'client_rendezvous')

@login_required(login_url='login')
def rendezvous_list(request):
    rendezvous = Reparation.objects.filter(statut='rendez_vous').select_related('moto__Client')
    return render_with_active(request, 'core/rendezvous_list.html', {'rendezvous': rendezvous}, 'rendezvous')

def valider_rdv(request, id):
    """Valide un RDV : passe statut rendez_vous → en attente
    puis redirige vers reparation_edit pour compléter"""
    reparation = get_object_or_404(Reparation, id=id)
    reparation.statut = 'en attente'
    reparation.save()
    return redirect('reparation_edit', id=reparation.id)

def rejeter_rdv(request, id):
    """Rejette un RDV : supprime la réparation créée par le client"""
    reparation = get_object_or_404(Reparation, id=id)
    if request.method == 'POST':
        reparation.delete()
        return redirect('rendezvous_list')
    return render_with_active(
        request,
        'core/rendezvous_reject_confirm.html',
        {'reparation': reparation},
        'rendezvous'
    )

def rendezvous_edit(request, id):
    """Modifie uniquement les infos RDV : description, date, téléphone"""
    reparation = get_object_or_404(Reparation, id=id)
    if request.method == 'POST':
        reparation.description     = request.POST.get('description', reparation.description)
        reparation.date_rendezvous = request.POST.get('date_rendezvous') or reparation.date_rendezvous
        reparation.telephone       = request.POST.get('telephone', reparation.telephone)
        reparation.save()
        return redirect('rendezvous_list')
    return render_with_active(
        request,
        'core/rendezvous_edit.html',
        {'reparation': reparation},
        'rendezvous'
    )

# ----------------------- 5-ETO NY VIEWS HO AN'NY MOTOS CLIENT:---------------------

@login_required(login_url='login')
def client_motos(request):
    """Liste les motos du client connecté"""
    client = Client.objects.filter(user=request.user).first()
    if not client:
        return redirect('profil_utilisateur')
    motos = Moto.objects.filter(Client=client)
    return render_with_active(
        request,
        'core/client_motos.html',
        {'motos': motos, 'client': client},
        'client_motos'
    )


@login_required(login_url='login')
def client_moto_add(request):
    """Le client ajoute lui-même sa moto"""
    client = Client.objects.filter(user=request.user).first()
    if not client:
        return redirect('profil_utilisateur')

    if request.method == 'POST':
        marque = request.POST.get('marque', '').strip()
        modele = request.POST.get('model', '').strip()
        if marque and modele:
            Moto.objects.create(Client=client, marque=marque, model=modele)
        return redirect('client_motos')

    return render_with_active(
        request,
        'core/client_moto_form.html',
        {'action': 'Ajouter'},
        'client_motos'
    )


@login_required(login_url='login')
def client_moto_delete(request, id):
    client = Client.objects.filter(user=request.user).first()
    moto = get_object_or_404(Moto, id=id, Client=client)
    
    # 🔐 VÉRIFIER SI LA MOTO A DES RÉPARATIONS EN COURS
    reparations_en_cours = Reparation.objects.filter(
        moto=moto,
        statut__in=['en attente', 'en cours', 'rendez_vous']
    ).exists()
    
    if reparations_en_cours:
        messages.error(request, "❌ Impossible de supprimer cette moto car elle a des réparations en cours ou planifiées.")
        return redirect('client_motos')
    
    if request.method == 'POST':
        moto.delete()
        messages.success(request, f"✅ La moto {moto.marque} {moto.model} a été supprimée.")
        return redirect('client_motos')
    
    return render_with_active(request, 'core/client_moto_confirm_delete.html', {'moto': moto}, 'client_motos')

# ----------------------- 6-ETO NY VIEWS HO AN'NY CLIENTS:---------------------
def client_list(request):
    query = request.GET.get('q', '').strip()
    clients = Client.objects.all()
    if query:
        clients = clients.filter(nom__icontains=query) | clients.filter(telephone__icontains=query)

    clients_count = Client.objects.count()
    motos_count = Moto.objects.count()
    commandes_count = Commande.objects.count()

    # ✅ NOUVEAUX COMPTEURS
    rendezvous_a_valider = Reparation.objects.filter(statut='rendez_vous').count()
    reparations_en_cours = Reparation.objects.filter(statut='en cours').count()

    context = {
        'clients': clients,
        'query': query,
        'clients_count': clients_count,
        'motos_count': motos_count,
        'commandes_count': commandes_count,
        'rendezvous_a_valider': rendezvous_a_valider,        
        'reparations_en_cours': reparations_en_cours,        
    }
    return render_with_active(request, 'core/client_list.html', context, 'clients')

def client_create(request):
    if request.method == 'POST':
        nom = request.POST.get('nom')
        telephone = request.POST.get('telephone')
        Client.objects.create(nom=nom, telephone=telephone)
        return redirect('client_list')
    return render_with_active(request, 'core/client_form.html', {'action': 'Créer', 'client': None}, 'clients')


def client_edit(request, id):
    client = Client.objects.get(id=id)
    if request.method == 'POST':
        client.nom = request.POST.get('nom')
        client.telephone = request.POST.get('telephone')
        client.save()
        return redirect('client_list')
    return render_with_active(request, 'core/client_form.html', {'action': 'Modifier', 'client': client}, 'clients')



def client_delete(request, id):
    client = Client.objects.get(id=id)
    if request.method == 'POST':
        client.delete()
        return redirect('client_list')
    return render_with_active(request, 'core/client_confirm_delete.html', {'client': client}, 'clients')




# ----------------------- 7-ETO NY VIEWS HO AN'NY MOTO:---------------------
def moto_list(request):
    motos = Moto.objects.all()
    return render_with_active(request, 'core/moto_list.html', {'motos': motos}, 'motos')


def moto_create(request):
    clients = Client.objects.all()
    if request.method == 'POST':
        client_id = request.POST.get('client')
        client = Client.objects.get(id=client_id)
        marque = request.POST.get('marque')
        model = request.POST.get('model')
        Moto.objects.create(Client=client, marque=marque, model=model)
        return redirect('moto_list')
    return render_with_active(request, 'core/moto_form.html', {'action': 'Créer', 'moto': None, 'clients': clients}, 'motos')


def moto_edit(request, id):
    moto = Moto.objects.get(id=id)
    clients = Client.objects.all()
    if request.method == 'POST':
        client_id = request.POST.get('client')
        moto.Client = Client.objects.get(id=client_id)
        moto.marque = request.POST.get('marque')
        moto.model = request.POST.get('model')
        moto.save()
        return redirect('moto_list')
    return render_with_active(request, 'core/moto_form.html', {'action': 'Modifier', 'moto': moto, 'clients': clients}, 'motos')


def moto_delete(request, id):
    moto = Moto.objects.get(id=id)
    if request.method == 'POST':
        moto.delete()
        return redirect('moto_list')
    return render_with_active(request, 'core/moto_confirm_delete.html', {'moto': moto}, 'motos')




# ----------------------- 8-ETO NY VIEWS HO AN'NY PIECE:---------------------
def piece_list(request):
    pieces = Piece.objects.all()
    return render_with_active(request, 'core/piece_list.html', {'pieces': pieces}, 'pieces')


def piece_create(request):
    if request.method == 'POST':
        nom = request.POST.get('nom')
        prix = request.POST.get('prix')
        stock = request.POST.get('stock')
        piece = Piece.objects.create(nom=nom, prix=prix, stock=stock)
        
        # ⚠️ AJOUT : Gérer l'upload de l'image ⚠️
        if 'image' in request.FILES:
            piece.image = request.FILES['image']
            piece.save()
        
        return redirect('piece_list')
    return render_with_active(request, 'core/piece_form.html', {'action': 'Créer', 'piece': None}, 'pieces')


def piece_edit(request, id):
    piece = Piece.objects.get(id=id)
    if request.method == 'POST':
        piece.nom = request.POST.get('nom')
        piece.prix = request.POST.get('prix')
        piece.stock = request.POST.get('stock')
        
        
        if 'image' in request.FILES:
            
            if piece.image:
                try:
                    import os
                    if os.path.isfile(piece.image.path):
                        os.remove(piece.image.path)
                except:
                    pass
            piece.image = request.FILES['image']
        
        piece.save()
        return redirect('piece_list')
    return render_with_active(request, 'core/piece_form.html', {'action': 'Modifier', 'piece': piece}, 'pieces')


def piece_delete(request, id):
    piece = Piece.objects.get(id=id)
    if request.method == 'POST':
        piece.delete()
        return redirect('piece_list')
    return render_with_active(request, 'core/piece_confirm_delete.html', {'piece': piece}, 'pieces')


# ----------------------- 9-ETO NY VIEWS HO AN'NY COMMANDE:---------------------
def commande_list(request):
    commandes = Commande.objects.select_related('client').all()
    return render_with_active(request, 'core/commande_list.html', {'commandes': commandes}, 'commandes')


def commande_create(request):
    clients = Client.objects.all()
    pieces = Piece.objects.all()
    if request.method == 'POST':
        client_id = request.POST.get('client')
        client = Client.objects.get(id=client_id)
        commande = Commande.objects.create(client=client)
        
        # Ajouter les lignes de commande
        piece_ids = request.POST.getlist('pieces')
        quantites = request.POST.getlist('quantites')
        
        for piece_id, quantite in zip(piece_ids, quantites):
            if piece_id and quantite:
                piece = Piece.objects.get(id=piece_id)
                LigneCommande.objects.create(
                    commande=commande,
                    piece=piece,
                    quantite=int(quantite)
                )
        
        # Calculer le total
        commande.mettre_a_jour_total()
        
        return redirect('commande_list')
    return render_with_active(request, 'core/commande_form.html', {'action': 'Créer', 'commande': None, 'clients': clients, 'pieces': pieces}, 'commandes')


def commande_edit(request, id):
    commande = Commande.objects.get(id=id)
    clients = Client.objects.all()
    pieces = Piece.objects.all()
    lignes = commande.lignecommande_set.all()
    
    if request.method == 'POST':
        client_id = request.POST.get('client')
        commande.client = Client.objects.get(id=client_id)
        
        # ===== NOUVEAU : METTRE À JOUR LE STATUT =====
        nouveau_statut = request.POST.get('statut')
        if nouveau_statut in ['en_attente', 'en_cours', 'livree', 'annulee']:
            commande.statut = nouveau_statut
        
        # ===== NOUVEAU : METTRE À JOUR LE MONTANT PAYÉ =====
        nouveau_montant_paye = Decimal(request.POST.get('montant_paye', 0))
        if nouveau_montant_paye >= 0 and nouveau_montant_paye <= commande.montant_total:
            commande.montant_paye = nouveau_montant_paye
            commande.mettre_a_jour_statut_paiement()
        
        commande.save()
        
        # Supprimer les anciennes lignes et recréer
        commande.lignecommande_set.all().delete()
        
        piece_ids = request.POST.getlist('pieces')
        quantites = request.POST.getlist('quantites')
        
        for piece_id, quantite in zip(piece_ids, quantites):
            if piece_id and quantite and int(quantite) > 0:
                piece = Piece.objects.get(id=piece_id)
                LigneCommande.objects.create(
                    commande=commande,
                    piece=piece,
                    quantite=int(quantite)
                )
        
        # Recalculer le total
        commande.mettre_a_jour_total()
        
        messages.success(request, f"✅ Commande #{commande.id} mise à jour avec succès.")
        return redirect('commande_list')
    
    return render_with_active(request, 'core/commande_form.html', {
        'action': 'Modifier',
        'commande': commande,
        'clients': clients,
        'pieces': pieces,
        'lignes': lignes
    }, 'commandes')


def commande_delete(request, id):
    commande = Commande.objects.get(id=id)
    if request.method == 'POST':
        commande.delete()
        return redirect('commande_list')
    return render_with_active(request, 'core/commande_confirm_delete.html', {'commande': commande}, 'commandes')


def paiement_create(request, commande_id):
    commande = Commande.objects.get(id=commande_id)
    if request.method == 'POST':
        montant = Decimal(request.POST.get('montant', 0))
        methode = request.POST.get('methode')
        reference = request.POST.get('reference')
        
        Paiement.objects.create(
            commande=commande,
            montant=montant,
            methode=methode,
            reference=reference
        )
        
        # Mettre à jour le montant payé
        commande.montant_paye += montant
        commande.mettre_a_jour_statut_paiement()
        
        return redirect('commande_detail', id=commande_id)
    
    return render_with_active(request, 'core/paiement_form.html', {'commande': commande}, 'commandes')


def commande_detail(request, id):
    commande = Commande.objects.select_related('client').prefetch_related('lignecommande_set__piece', 'paiement_set').get(id=id)
    lignes = commande.lignecommande_set.all()
    paiements = commande.paiement_set.all()
    
    return render_with_active(request, 'core/commande_detail.html', {
        'commande': commande,
        'lignes': lignes,
        'paiements': paiements
    }, 'commandes')


# ----------------------- 10-ETO NY VIEWS HO AN'NY REPARATION:---------------------
def reparation_list(request):
    reparations = Reparation.objects.exclude(statut='rendez_vous').select_related('moto').prefetch_related('pieces').all()
    return render_with_active(request, 'core/reparation_list.html', {'reparations': reparations}, 'reparations')


def reparation_create(request):
    motos = Moto.objects.all()
    pieces = Piece.objects.all()

    if request.method == 'POST':
        moto_id = request.POST.get('moto')
        description = request.POST.get('description')
        statut = request.POST.get('statut', 'en attente')
        piece_ids = request.POST.getlist('pieces')

        moto = Moto.objects.get(id=moto_id)
        reparation = Reparation.objects.create(
            moto=moto,
            description=description,
            montant_total=0,  # sera recalculé juste après
            statut=statut
        )

        # Ajouter les pièces ET calculer le montant automatiquement
        montant_total = 0
        for piece_id in piece_ids:
            if piece_id:
                piece = Piece.objects.get(id=piece_id)
                reparation.pieces.add(piece)
                montant_total += piece.prix  # ← calcul auto

        reparation.montant_total = montant_total
        reparation.save()

        return redirect('reparation_detail', id=reparation.id)

    return render_with_active(request, 'core/reparation_form.html', {
        'action': 'Créer',
        'reparation': None,
        'motos': motos,
        'pieces': pieces,
    }, 'reparations')

def reparation_detail(request, id):
    """Affiche les détails d'une réparation"""
    reparation = Reparation.objects.select_related('moto').prefetch_related('pieces', 'paiements').get(id=id)
    paiements = reparation.paiements.all()
    
    return render_with_active(request, 'core/reparation_detail.html', {
        'reparation': reparation,
        'paiements': paiements
    }, 'reparations')


def reparation_edit(request, id):
    reparation = Reparation.objects.get(id=id)
    motos = Moto.objects.all()
    pieces = Piece.objects.all()

    if request.method == 'POST':
        reparation.description = request.POST.get('description')
        reparation.statut = request.POST.get('statut', 'en attente')
        reparation.save()

        # Recalculer le montant depuis les pièces cochées
        reparation.pieces.clear()
        piece_ids = request.POST.getlist('pieces')
        montant_total = 0
        for piece_id in piece_ids:
            if piece_id:
                piece = Piece.objects.get(id=piece_id)
                reparation.pieces.add(piece)
                montant_total += piece.prix  # ← calcul auto

        reparation.montant_total = montant_total
        reparation.save()

        return redirect('reparation_detail', id=reparation.id)

    return render_with_active(request, 'core/reparation_form.html', {
        'action': 'Modifier',
        'reparation': reparation,
        'motos': motos,
        'pieces': pieces,
    }, 'reparations')
def reparation_delete(request, id):
    """Supprime une réparation"""
    reparation = Reparation.objects.get(id=id)
    if request.method == 'POST':
        reparation.delete()
        return redirect('reparation_list')
    return render_with_active(request, 'core/reparation_confirm_delete.html', {'reparation': reparation}, 'reparations')


# ----------------------- 11-ETO NY VIEWS HO AN'NY CATALOGUE PIECES:---------------------


# [ ---- @login_required(login_url='login') : ito dia natao mba iarovana ny pieces catalogues amidy satria izay olona efa manana compte ihany no 
# afaka mividy na  koa mandrotsaka ao anaty panier. (Mitovy @ BET261) ]

@login_required(login_url='login')
def catalogue_pieces(request):
    """Affiche le catalogue dynamique des pièces"""
    pieces = Piece.objects.filter(stock__gt=0).all()
    return render_with_active(request, 'core/catalogue_pieces.html', {'pieces': pieces}, 'catalogue')


@login_required(login_url='login')
def piece_detail(request, id):
    """Page de détail d'une pièce"""
    piece = get_object_or_404(Piece, id=id)
    return render_with_active(request, 'core/piece_detail.html', {'piece': piece}, 'catalogue')


# ----------------------- 12-ETO NY VIEWS HO AN'NY PANIER:---------------------
@login_required(login_url='login')
def ajouter_au_panier(request, piece_id):
    """Ajoute une pièce au panier de l'utilisateur"""
    piece = get_object_or_404(Piece, id=piece_id)
    quantite = int(request.POST.get('quantite', 1))
    
    if quantite <= 0 or quantite > piece.stock:
        return redirect('catalogue_pieces')


    
    # Famoronana panier raha toa ka mbola tsy misy entana hovidiana ka tsy mbola misy panier koa mazava ho azy :
    panier, created = Panier.objects.get_or_create(utilisateur=request.user)
    
    # Mandrotsaka ao anaty panier na mikitika ny efa ao :
    ligne, created = LignePanier.objects.get_or_create(
        panier=panier,
        piece=piece,
        defaults={'quantite': quantite}
    )
    
    if not created:
        ligne.quantite += quantite
        if ligne.quantite > piece.stock:
            ligne.quantite = piece.stock
        ligne.save()
    
    return redirect('voir_panier')
    
# Mijery ny ao anaty panier (voir):
@login_required(login_url='login')
def voir_panier(request):
    """Affiche le panier de l'utilisateur"""
    panier, created = Panier.objects.get_or_create(utilisateur=request.user)
    lignes = panier.lignepanier_set.all()
    total = panier.total()
    
    return render_with_active(request, 'core/panier.html', {
        'panier': panier,
        'lignes': lignes,
        'total': total
    }, 'panier')
# Return render_with_active no mametraka ilay pejy miasa amin'ny fotoana ankehitriny ho lasa active miaraka @ loko (mavo)

# Manala ny efa ao anaty panier (retirer):
@login_required(login_url='login')
def retirer_du_panier(request, ligne_id):
    """Retire une ligne du panier"""
    ligne = get_object_or_404(LignePanier, id=ligne_id, panier__utilisateur=request.user)
    ligne.delete()
    return redirect('voir_panier')


# Manamarina na manaiky ny ao anaty panier (valider):
@login_required(login_url='login')
def valider_panier(request):
    """Valide le panier et crée une commande"""
    panier = get_object_or_404(Panier, utilisateur=request.user)
    lignes = panier.lignepanier_set.all()
    
    if not lignes.exists():
        return redirect('voir_panier')
    
    if request.method == 'POST':
        # Créer la commande
        client = request.user.client if hasattr(request.user, 'client') else None
        # ( HASATTAR dia midika fa ilay objet(user) ve mitondra ilay attribut(client), izany hoe tsy afaka mividy raha mbola tsy client)
        if not client:
            return redirect('profil')  # Rediriger vers le profil pour créer un client
        
        commande = Commande.objects.create(client=client)
        
        # Ajouter les lignes de commande et réduire le stock
        for ligne in lignes:
            LigneCommande.objects.create(
                commande=commande,
                piece=ligne.piece,
                quantite=ligne.quantite
            )
            # Réduire le stock
            ligne.piece.stock -= ligne.quantite
            ligne.piece.save()
        
        # Calculer le total
        commande.mettre_a_jour_total()
        
        # Vider le panier
        panier.lignepanier_set.all().delete()
        
        return redirect('commande_detail', id=commande.id)
    
    return render_with_active(request, 'core/valider_panier.html', {
        'panier': panier,
        'lignes': lignes,
        'total': panier.total()
    }, 'panier')


# ----------------------- 13-ETO NY VIEWS HO AN'NY PAIEMENT REPARATION:---------------------
def paiement_reparation_create(request, reparation_id):
    """Crée un paiement pour une réparation"""
    reparation = get_object_or_404(Reparation, id=reparation_id)
    
    if request.method == 'POST':
        montant = Decimal(request.POST.get('montant', 0))
        methode = request.POST.get('methode')
        reference = request.POST.get('reference')
        
        PaiementReparation.objects.create(
            reparation=reparation,
            montant=montant,
            methode=methode,
            reference=reference
        )
        
        # Mettre à jour le montant payé
        reparation.montant_paye += montant
        reparation.mettre_a_jour_statut_paiement()
        
        return redirect('client_repairs')
    
    return render_with_active(request, 'core/paiement_reparation_form.html', {'reparation': reparation}, 'reparations')


# ----------------------- 14-ETO NY VIEWS HO AN'NY PROFIL:---------------------
@login_required(login_url='login')
def profil_utilisateur(request):
    """Affiche le profil de l'utilisateur"""
    profil, created = Profil.objects.get_or_create(utilisateur=request.user)
    client = Client.objects.filter(user=request.user).first()
    
    if request.method == 'POST':
        # Mettre à jour le profil
        profil.bio = request.POST.get('bio', '')
        profil.telephone = request.POST.get('telephone', '')
        profil.adresse = request.POST.get('adresse', '')
        
        if 'photo_profil' in request.FILES:
            profil.photo_profil = request.FILES['photo_profil']
        
        profil.save()
        
        # Mettre à jour les infos du client
        if not client:
            client = Client.objects.create(
                user=request.user,
                nom=request.user.get_full_name() or request.user.username,
                email=request.user.email,
                telephone=profil.telephone,
                adresse=profil.adresse
            )
        else:
            client.nom = request.user.get_full_name() or request.user.username
            client.email = request.user.email
            client.telephone = profil.telephone
            client.adresse = profil.adresse
            client.save()
        
        return redirect('profil_utilisateur')
    
    # Vérifier que le fichier existe physiquement avant d'exposer l'URL
    photo_url = None
    if profil.photo_profil:
        try:
            if os.path.exists(profil.photo_profil.path):
                photo_url = profil.photo_profil.url
        except Exception:
            photo_url = None

    return render_with_active(request, 'core/profil.html', {
        'profil': profil,
        'client': client,
        'photo_url': photo_url,
    }, 'profil')

# ---------------------- 15-ETO NY VIEWS HO AN'NY TEMOIGNAGE:---------------------

def temoignage_create(request):
    """Formulaire public — tout visiteur peut laisser un témoignage"""
    if request.method == 'POST':
        auteur = request.POST.get('auteur', '').strip()
        texte  = request.POST.get('texte', '').strip()
        note   = int(request.POST.get('note', 5))
        note   = max(1, min(5, note))  # sécurité : forcer entre 1 et 5

        temoignage = Temoignage(auteur=auteur, texte=texte, note=note)
        if 'photo' in request.FILES:
            temoignage.photo = request.FILES['photo']
        temoignage.save()
        return redirect('temoignage_merci')

    return render_with_active(
        request,
        'core/temoignage_form.html',
        {},
        'temoignage'
    )


def temoignage_merci(request):
    """Page de confirmation après soumission"""
    return render_with_active(
        request,
        'core/temoignage_merci.html',
        {},
        'temoignage'
    )


def temoignage_list(request):
    """Liste admin — séparée en 3 groupes comme le template l'attend"""
    en_attente = Temoignage.objects.filter(statut='en_attente').order_by('-date')
    actifs     = Temoignage.objects.filter(statut='actif').order_by('-date')
    archives   = Temoignage.objects.filter(statut='archive').order_by('-date')
    actifs_count = actifs.count()

    return render_with_active(
        request,
        'core/temoignage_list.html',
        {
            'en_attente':   en_attente,
            'actifs':       actifs,
            'archives':     archives,
            'actifs_count': actifs_count,
        },
        'temoignages'
    )


def temoignage_activer(request, id):
    """Passe le statut à 'actif' — apparaît sur la page d'accueil"""
    temoignage = get_object_or_404(Temoignage, id=id)
    temoignage.statut = 'actif'
    temoignage.save()
    return redirect('temoignage_list')


def temoignage_desactiver(request, id):
    """Passe le statut à 'archive' — disparaît de l'accueil"""
    temoignage = get_object_or_404(Temoignage, id=id)
    temoignage.statut = 'archive'
    temoignage.save()
    return redirect('temoignage_list')


def temoignage_delete(request, id):
    """Suppression définitive avec page de confirmation"""
    temoignage = get_object_or_404(Temoignage, id=id)
    if request.method == 'POST':
        temoignage.delete()
        return redirect('temoignage_list')
    return render_with_active(
        request,
        'core/temoignage_confirm_delete.html',
        {'temoignage': temoignage},
        'temoignages'
    )

# ----------------------- 16-ETO NY VIEWS HO AN'NY SERVICES & CONTACT:---------------------

def services(request):
    """Page détaillée des services"""
    return render_with_active(request, 'core/services.html', {}, 'services')

def contact(request):
    """Page de contact"""
    return render_with_active(request, 'core/contact.html', {}, 'contact')


# ----------------------- 17-ETO NY VIEWS HO AN'NY MESSAGES:---------------------


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        form.fields['username'].label = 'Email'
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # ⚠️ AJOUTER MESSAGE DE BIENVENUE
            messages.success(request, f'Bienvenue {user.username} !')
            
            if user.is_staff:
                return redirect('accueil')
            return redirect('client_portal')
        else:
            # ⚠️ AJOUTER MESSAGE D'ERREUR
            messages.error(request, 'Email ou mot de passe incorrect. Veuillez réessayer.')
    else:
        form = AuthenticationForm()
        form.fields['username'].label = 'Email'
    
    return render_with_active(request, 'core/login.html', {'form': form}, 'login')


def logout_view(request):
    # ⚠️ AJOUTER MESSAGE AVANT DECONNEXION
    messages.success(request, 'Vous avez été déconnecté avec succès.')
    logout(request)
    return redirect('accueil')


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Client.objects.create(
                user=user,
                nom=form.cleaned_data['nom'],
                email=user.email,
                telephone=''
            )
            # ⚠️ AJOUTER MESSAGE DE BIENVENUE
            messages.success(request, 'Compte créé avec succès ! Connectez-vous maintenant.')
            login(request, user)
            return redirect('client_portal')
        else:
            # ⚠️ AFFICHER LES ERREURS DU FORMULAIRE
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = CustomUserCreationForm()
    
    return render_with_active(request, 'core/register.html', {'form': form}, 'register')

# ----------------------- 18-ETO NY VIEWS HO AN'NY TOUS LES TEMOIGNAGES:---------------------

def tous_temoignages(request):
    """Affiche tous les témoignages validés (statut='actif')"""
    temoignages = Temoignage.objects.filter(statut='actif').order_by('-date')
    return render_with_active(request, 'core/tous_temoignages.html', {
        'temoignages': temoignages,
        'temoignages_count': temoignages.count(),
    }, 'tous_temoignages')