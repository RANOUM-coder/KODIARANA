from django.db import models
from django.contrib.auth.models import User

# Miisa 12 ny CLASS MODELS ito ato, ireto avy izy ireo : client, moto, reparation, pieces, commande,
# client, client poral, auth, panier//LignePanier, paiement reparation ary farany profil, témoinages.

# --------------- 1-MODELE HO AN'NY CLIENT -------------------

class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    nom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    adresse = models.CharField(max_length=255, blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom


# --------------- 2-MODELE HO AN'NY MOTO -------------------

class Moto(models.Model):
    Client = models.ForeignKey(Client, on_delete=models.CASCADE)
    marque = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.marque} {self.model}"

# --------------- 3-MODELE HO AN'NY PIECE -------------------

class Piece(models.Model):
    CATEGORIE_CHOICES = [
        ('pneu', '🛞 Pneus'),
        ('frein', '🛑 Freinage'),
        ('suspension', '🔧 Suspensions'),
        ('jante', '⚙️ Jantes & roues'),
        ('electrique', '🔋 Électrique'),
        ('moteur', '🔧 Moteur'),
        ('transmission', '⛓️ Transmission'),
        ('carrosserie', '🎨 Carrosserie'),
        ('autre', '📦 Autre'),
    ]

    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    image = models.ImageField(upload_to='pieces/', blank=True, null=True)
    categorie = models.CharField(
        max_length=20,
        choices=CATEGORIE_CHOICES,
        default='autre'
    )
    date_creation = models.DateTimeField(auto_now_add=True)

# --------------- 4-MODELE HO AN'NY REPARATION -------------------

class Reparation(models.Model):
    moto = models.ForeignKey(Moto, on_delete=models.CASCADE)
    description = models.TextField()
    pieces = models.ManyToManyField(Piece, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    montant_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    montant_paye = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    statut_paiement = models.CharField(max_length=20, choices=[
        ('non_paye', 'Non payé'),
        ('partiellement_paye', 'Partiellement payé'),
        ('paye', 'Payé'),
    ], default='non_paye')
    STATUT_CHOICES = [
    ('rendez_vous', 'Rendez-vous'),
    ('en attente',  'En attente'),
    ('en cours',    'En cours'),
    ('terminee',    'Terminée'),
    ]
    statut = models.CharField(max_length=50, choices=STATUT_CHOICES, default='en attente')
    date_rendezvous = models.DateTimeField(blank=True, null=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"Réparation - {self.moto}"
    
    def reste_a_payer(self):
        return self.montant_total - self.montant_paye
    
    def mettre_a_jour_statut_paiement(self):
        if self.montant_paye == 0:
            self.statut_paiement = 'non_paye'
        elif self.montant_paye < self.montant_total:
            self.statut_paiement = 'partiellement_paye'
        else:
            self.statut_paiement = 'paye'
        self.save()
    

# --------------- 5-MODELE HO AN'NY COMMANDE -------------------

class Commande(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=50, default='en attente')
    montant_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    montant_paye = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    statut_paiement = models.CharField(max_length=20, choices=[
        ('non_paye', 'Non payé'),
        ('partiellement_paye', 'Partiellement payé'),
        ('paye', 'Payé'),
    ], default='non_paye')

    def __str__(self):
        return f"Commande {self.id} - {self.client}"
    
    def calculer_total(self):
        total = 0
        for ligne in self.lignecommande_set.all():
            total += ligne.piece.prix * ligne.quantite
        return total
    
    def mettre_a_jour_total(self):
        self.montant_total = self.calculer_total()
        self.save()
    

    def reste_a_payer(self):
        return self.montant_total - self.montant_paye
    
    def mettre_a_jour_statut_paiement(self):
        if self.montant_paye == 0:
            self.statut_paiement = 'non_paye'
        elif self.montant_paye < self.montant_total:
            self.statut_paiement = 'partiellement_paye'
        else:
            self.statut_paiement = 'paye'
        self.save()
    


# --------------- 6-MODELE HO AN'NY PAIEMENT -------------------

class Paiement(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    methode = models.CharField(max_length=20, choices=[
        ('especes', 'Espèces'),
        ('carte', 'Carte bancaire'),
        ('virement', 'Virement bancaire'),
        ('cheque', 'Chèque'),
    ], default='especes')
    reference = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Paiement {self.montant} Ar - {self.commande}"


# --------------- 7-MODELE HO AN'NY LIGNE COMMANDE-------------------

class LigneCommande(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE)
    piece = models.ForeignKey(Piece, on_delete=models.CASCADE)
    quantite = models.IntegerField()

    def __str__(self):
        return f"{self.piece} x {self.quantite}"
    
    def montant_total(self):
        return self.piece.prix * self.quantite



# --------------- 8-MODELE HO AN'NY PAIMENT REPARATION -------------------

class PaiementReparation(models.Model):
    reparation = models.ForeignKey(Reparation, on_delete=models.CASCADE, related_name='paiements')
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    methode = models.CharField(max_length=20, choices=[
        ('especes', 'Espèces'),
        ('carte', 'Carte bancaire'),
        ('virement', 'Virement bancaire'),
        ('cheque', 'Chèque'),
    ], default='especes')
    reference = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Paiement réparation {self.montant} Ar - {self.reparation}"



# --------------- 9-MODELE HO AN'NY PANIER -------------------

class Panier(models.Model):
    utilisateur = models.OneToOneField(User, on_delete=models.CASCADE, related_name='panier')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Panier - {self.utilisateur.username}"
    
    def total(self):
        return sum(item.montant_total() for item in self.lignepanier_set.all())
    
    def total_items(self):
        return sum(item.quantite for item in self.lignepanier_set.all())


# --------------- 10-MODELE HO AN'NY LIGNE PANIER -------------------

class LignePanier(models.Model):
    panier = models.ForeignKey(Panier, on_delete=models.CASCADE)
    piece = models.ForeignKey(Piece, on_delete=models.CASCADE)
    quantite = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.piece} x {self.quantite}"
    
    def montant_total(self):
        return self.piece.prix * self.quantite



# --------------- 11-MODELE HO AN'NY PROFIL -------------------

class Profil(models.Model):
    utilisateur = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profil')
    photo_profil = models.ImageField(upload_to='profils/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    adresse = models.CharField(max_length=255, blank=True, null=True)
    date_modification = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profil - {self.utilisateur.username}"

# --------------- 12-MODELE HO AN'NY TEMOIGNAGE -------------------

class Temoignage(models.Model):
    auteur = models.CharField(max_length=120)
    texte = models.TextField()
    note = models.IntegerField(default=5) 
    photo = models.ImageField(upload_to='temoignages/', blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=20, choices=[
        ('en_attente', 'En attente'),
        ('actif',      'Actif'),
        ('archive',    'Archivé'),
    ], default='en_attente')

    def __str__(self):
        return f"{self.auteur} — {self.note}★"
    
    def etoiles(self):
        """Retourne une liste pour boucler les étoiles dans le template"""
        return range(self.note)
    
    def etoiles_vides(self):
        return range(5 - self.note)