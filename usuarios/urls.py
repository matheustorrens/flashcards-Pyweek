from django.urls import path
from . import views # O ponto nas importações do Python significa que ele importará arquivos da pasta em que está a importação

urlpatterns = [
    path('cadastro/', views.cadastro, name="cadastro"),
    path('logar/', views.logar, name="login"),
    path('logout/', views.logout, name="logout"),

]