"""ProyectoProgramacion1 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from ProyectoProgramacion1 import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('autenticacion/',views.identificar_usuario),
    path('inicio/',views.mandar_inicio),
    path('registro/',views.formulario_usuarios),
    path('verificar/',views.verificar_codigo_otp),
    path('server/',views.redireccionar),
    path('monitoreo/',views.estado_servidor),
    path('monitorizacion/', views.recuperar_server),
    path('logout/', views.cerrar_sesion),
    path('logout_admin/', views.logoutAdmin),
    path('loginAdmin/', views.registro_admin),
    path('dashboard_admin/', views.dashboard_admins),
    path('dashboard_server/', views.dashboard_servers),
    path('registro_server/', views.formulario_servidores),
    path('editar_usuario/', views.editar_usuario),
    path('eliminar_usuario/<id>', views.eliminarUsuario, name="eliminarUsuario"),
    path('editar_usuario/<id>', views.editar_usuario, name="editarUsuario"),
    path('eliminar_server/<id>', views.eliminarServer, name="eliminarServer"),
    path('editar_server/<id>', views.editarServer, name="editarServer"),
    path('asociar-servidor/', views.asociar_servidor, name='asociar_servidor'),
]
