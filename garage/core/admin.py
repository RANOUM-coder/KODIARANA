from django.contrib import admin
from .models import Client, Moto, Piece, Reparation, Commande, LigneCommande, Paiement
from .models import Client, Moto, Piece, Reparation, Commande, LigneCommande, Paiement, Temoignage

# Inline pour LigneCommande
class LigneCommandeInline(admin.TabularInline):
    model = LigneCommande
    extra = 1
 # Un Inline permet d'afficher et modifier des objets liés directement dans la page d'un autre objet. Ici, quand le gérant ouvre une Commande, il voit directement les lignes de cette commande (quelle pièce, quelle quantité) sans aller sur une autre page. extra = 1 signifie qu'une ligne vide est affichée par défaut pour en ajouter une nouvelle facilement. TabularInline affiche les lignes en format tableau horizontal (plus compact).


# Inline pour Paiement
class PaiementInline(admin.TabularInline):
    model = Paiement
    extra = 0
    readonly_fields = ['date']

   
    # Même principe : les paiements d'une commande s'affichent directement dans la page de la commande. extra = 0 → aucune ligne vide par défaut (on n'attend pas forcément un paiement immédiat). readonly_fields = ['date'] → la date est automatique (auto_now_add), donc on la rend non modifiable pour éviter les manipulations.

# Admin Commande avec inline amélioré 
class CommandeAdmin(admin.ModelAdmin):
    inlines = [LigneCommandeInline, PaiementInline]
    list_display = ['id', 'client', 'date', 'statut', 'montant_total', 'montant_paye', 'statut_paiement']
    list_filter = ['statut', 'statut_paiement', 'date']
    

# Admin Reparation amélioré aussi
class ReparationAdmin(admin.ModelAdmin):
    filter_horizontal = ('pieces',)
    # La relation entre Reparation et Piece est ManyToMany (une réparation peut utiliser plusieurs pièces). Par défaut, Django affiche cela comme une liste déroulante multiple peu pratique. filter_horizontal remplace ça par deux boîtes côte à côte avec des boutons pour déplacer les pièces de "disponibles" vers "sélectionnées" → beaucoup plus ergonomique.

class TemoignageAdmin(admin.ModelAdmin):
    list_display = ['auteur', 'note', 'statut', 'date']
    list_filter  = ['statut', 'note']

admin.site.register(Temoignage, TemoignageAdmin)

# Register
admin.site.register(Client)
admin.site.register(Moto)
admin.site.register(Piece)
admin.site.register(Reparation, ReparationAdmin)
admin.site.register(Commande, CommandeAdmin)
admin.site.register(Paiement)
# Chaque modèle est enregistré dans l'admin. Ceux avec une classe Admin personnalisée (Reparation, Commande) bénéficient des améliorations. Les autres (Client, Moto, Piece, Paiement) utilisent la configuration par défaut de Django — fonctionnelle mais basique.