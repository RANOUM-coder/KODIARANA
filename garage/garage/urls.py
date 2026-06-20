from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
# from django.views.defaults import page_not_found

# Vue personnalisée pour les erreurs 404 (page non trouvée)
def custom_404(request, exception):
    return redirect('accueil')

# Vue personnalisée pour les erreurs 500 (erreur serveur)
def custom_500(request):
    return redirect('accueil')

# Vue personnalisée pour les erreurs 403 (accès interdit)
def custom_403(request, exception):
    return redirect('accueil')

# Vue personnalisée pour les erreurs 400 (requête incorrecte)
def custom_400(request, exception):
    return redirect('accueil')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [
    path('<path:invalid_path>', lambda request, invalid_path: redirect('accueil')),
]

# ⚠️ FAMPITANDREMANA : Ces handlers doivent être au niveau global du projet
# Ils ne se mettent pas dans urlpatterns, mais en dehors