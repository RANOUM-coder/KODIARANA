from django.shortcuts import redirect

def custom_404_view(request, exception=None):
    """Redirige vers l'accueil quand la page n'existe pas"""
    return redirect('accueil')

def custom_500_view(request):
    """Redirige vers l'accueil en cas d'erreur serveur"""
    return redirect('accueil')

def custom_403_view(request, exception=None):
    """Redirige vers l'accueil en cas d'accès interdit"""
    return redirect('accueil')

def custom_400_view(request, exception=None):
    """Redirige vers l'accueil en cas de requête incorrecte"""
    return redirect('accueil')