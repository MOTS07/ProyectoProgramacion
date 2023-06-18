from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from datetime import datetime, timedelta
from bd import models 
from datetime import timezone

import re
import random
import string
import time
import requests
import crypt
import os
import base64


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def mandar_inicio(request) -> HttpResponse:
    """
    Vista de inicio.

    Keyword Arguments:
    request -- 
    returns: HttpResponse 
    """
    logueado = request.session.get('registrado')
    if not logueado:
       return redirect('/registro/')
    return HttpResponse('Hola mundo')

def recuperar_info_ip(ip:str) -> models.Intentos:
    """
    Recupera información asociada a una ip, si la ip no existe se regresa una tupla vacía.

    Keyword Arguments:
    ip str ip V4
    returns: models.Intentos
    """
    try:
        registro = models.Intentos.objects.get(ip=ip)
        return  registro 
    except:
        return None



def fecha_en_intervalo(fecha_ultimo_intento:datetime, ahora:datetime, tiempo_limite:int) -> bool:
    """
    Determina si fecha_ultimo_intento está dentro del intervalo de tiempo definido por tiempo_limite.
    
    Keyword Arguments:
    fecha_ultimo_intento:datetime del registro del último intento almacenado
    ahora:datetime fecha actual del sistema                -- 
    tiempo_limite:int segundo del intervalo de tiempo             -- 
    returns: bool True si está en el intervalo 
    """
    diferencia_segundos = (ahora - fecha_ultimo_intento).seconds
    if diferencia_segundos < tiempo_limite:
        return True
    return False


def modificar_registro(registro:models.Intentos, ahora: datetime, intentos=1) -> None:
    """
    Restablece un registro de intentos con valores por defecto.

    Keyword Arguments:
    registro:models.Intentos --
    ahora:datetime hora actual del sistema
    returns: None 
    """
    registro.intentos = intentos
    registro.fecha_ultimo_intento = ahora
    registro.save()

def puede_intentar_loguearse(request, tiempo_limite=60, intentos_maximos=3) -> bool:
    """
    Determina si el cliente cuenta con intentos disponibles para loguearse.

    Keyword Arguments:
    request -- 
    returns: bool 
    """
    ip = get_client_ip(request)
    ahora = datetime.now(timezone.utc)
    registro = recuperar_info_ip(ip)
    if not registro:
        nuevo_registro = models.Intentos()
        nuevo_registro.ip = ip
        modificar_registro(nuevo_registro, ahora)
        return True
    else:
        intentos = registro.intentos
        fecha_ultimo_intento = registro.fecha_ultimo_intento
        if not fecha_en_intervalo(fecha_ultimo_intento, ahora, tiempo_limite):
            modificar_registro(registro, ahora)
         
            return True
        else:
            if intentos < intentos_maximos:
                modificar_registro(registro, ahora, intentos+1)
                return True
            else:
                modificar_registro(registro, ahora, intentos_maximos)
                return False



def credenciales(usuario,contra) -> bool:
    """Regresa verdadero si se encuentra un usuario en la BD
    con el usuario y contraseña pasados como argumento

    Args:
        usuario (string): Campo de usuario en el formulario de login
        contra (string): Contraseña en texto plano en el formulario de login

    Returns:
        bool: True si se encuentra el usuario
    """
    try:
        #usuario = models.RegistroAdmin.objects.get(nombre=usuario)
        usuario = models.RegistroAdmin.objects.get(nombre=usuario)
        #El usuario existe, ahora comparar contraseñas
        partes = usuario.contraseña.split('$')
        salt = '$' + partes[1] + '$' + partes[2]
        contra_cifrada = crypt.crypt(contra, salt)
        if contra_cifrada == usuario.contraseña:
            return True
        else:
            return False
    except Exception as error:
        print(error)
        return False




def identificar_usuario(request) -> HttpResponse:
    """
    Vista para autenticar usuarios.

    Keyword Arguments:
    request -- 
    returns: HttpResponse 
    """

    template = 'login.html'
    if request.method == 'GET':
        return render(request, template)
    else:
        errores = []
        usuario = request.POST.get('nombre','').strip()
        contra = request.POST.get('password','').strip()
        id_telegram = request.POST.get('id_telegram','').strip()

        if puede_intentar_loguearse(request):
            if not usuario.strip() or not contra.strip():
                errores.append('No se ingreso usuario o contraseña')
                return render(request,template,{'errores':errores})

            if validar_chat_id(request,id_telegram) == False:
                errores.append('Chat ID erroneo')
                return render(request,template,{'errores':errores})

            if not credenciales(usuario,contra):
                errores.append('Usuario o Contraseña invalidos')
                return render(request,template,{'errores':errores})
            enviar_otp(request,id_telegram) #Envia el OTP para la autenticion de dos pasos
            request.session['registrado'] = True
            return redirect('/verificar/')
        else:
            return render(request, template, {'errores': ['Ya no tienes intentos, espera unos minutos']})



def validar_usuarios(nombre,correo,id_telegram,contraseña,contraseña2,ip_server):
    errores = []
    if not nombre:
        errores.append('El nombre está vacío')
    if not correo:
        errores.append('El correo esta vacío')
    if not id_telegram.isnumeric():
        errores.append('El ID esta vacío')
    if not contraseña:
        errores.append('La contraseña esta vacia')
    if not contraseña2:
        errores.append('La contraseña esta vacia')
    if not ip_server:
        errores.append('La direccion IP está vacía')
    if contraseña != contraseña2:
        errores.append('Las contraseñas no son iguales')
    return errores


def formulario_usuarios(request):
    """
    Realiza el registro de los usuarios

    Keyword Arguments:
    request: request, página del formulario de usuarios
    returns: render(request)
    """
    t='registro.html'
    if request.method == 'GET':
        return render(request, t)
    
    else:
        nombre = request.POST.get('nombre','').strip()
        correo = request.POST.get('correo','').strip()
        id_telegram = request.POST.get('id_telegram','').strip()
        contraseña = request.POST.get('contraseña','').strip()
        contraseña2 = request.POST.get('contraseña2','').strip()
        ip_server = request.POST.get('ip_server','').strip()
        errores = validar_usuarios(nombre,correo,id_telegram,contraseña,contraseña2,ip_server)

        if errores:
            c = {'errores': errores}
            return render(request, t, c)
        else:
            n_usuario = models.RegistroAdmin(nombre=nombre,
                                             correo=correo,
                                             id_telegram=id_telegram,
                                             contraseña=encriptar_password(contraseña),
                                             ip_server=ip_server)
            n_usuario.save()
            return redirect('/monitoreo/')



def enviar_otp(request,id_telegram):
    """
    Envia el codigo OPT, verifica el chat_id del usuario y
    lo envia a travez del BOT de telegram del ID del usuario

    Keyword Arguments:
    otp: codigo OPT para enviar
    chat_id: str, ID del chat de telegram del usuario
    returns: chat_id, lo utiliza la funcion de verificar_codigo_otp

    """
    chat_id = id_telegram
    print("URL",chat_id)
    TOKEN = "6186600289:AAHuTujstEwq93x7oR8zmAjsoWLw1AjyeHY"
    otp = ''.join(random.choices(string.digits, k=6))
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={otp}" 
    requests.post(url)
    tiempo_exp = datetime.now(timezone.utc) + timedelta(minutes=3)
    print(tiempo_exp)
    otp_bd = models.OTP(id_telegram=chat_id,otp=otp,tiempo_exp=tiempo_exp)
    otp_bd.save()
    #Guarda la Ip en la session, funciona para conectarse al SSH
    ip_server(request,chat_id)
    request.session['id_tel'] = chat_id
    return True

def ip_server(request,chat_id):
    for ip in models.RegistroAdmin.objects.all():
        id_telegram= ip.id_telegram
        ip_server= ip.ip_server
        if chat_id==id_telegram:
            request.session['IP_server']=ip_server


def verificar_codigo_otp(request):
    """
    Verifica el código OTP almacenado en la base de datos

    Keyword Arguments:
    request: HttpRequest
    returns: HttpResponse
    """
    registrado = request.session.get('registrado')
    if not registrado:
       return redirect('/autenticacion/')

    chat_id_bd = request.session.get('id_tel')
    print(chat_id_bd)
    contador = 0

    t = "verificar.html"
    if request.method == 'GET':
        return render(request,t)
    else:
        #chat_id_bd = request.POST.get('id_telegram','').strip()
        codigo_otp = request.POST.get('codigo_otp','').strip()
        contador = 1
        tiempo_actual = datetime.now(timezone.utc)

        if validar_chat_id(request, chat_id_bd) == True:
            for codigo_t in models.OTP.objects.all():
                tiempo_exp = codigo_t.tiempo_exp
                otp = codigo_t.otp
                telegram_id = codigo_t.id_telegram

                if tiempo_actual > tiempo_exp:
                    registros_expirados = models.OTP.objects.filter(id_telegram=telegram_id, otp=otp, tiempo_exp=tiempo_exp)
                    registros_expirados.delete()
                    return HttpResponse("OTP expirado 1")

                elif telegram_id == chat_id_bd and codigo_otp == otp:
                    models.OTP.objects.filter(id_telegram=telegram_id).delete()
                    #models.OTP.objects.filter(otp=codigo_otp).delete()
                    #models.OTP.objects.filter(id_telegram=chat_id_bd).delete()
                    request.session['logueado'] = True
                    return redirect('/monitoreo/')

                elif contador > 0:
                    models.OTP.objects.filter(id_telegram=chat_id_bd).delete()
                    return HttpResponse("Token Erroneo")

        elif validar_chat_id(request,chat_id_bd) == False:
            models.OTP.objects.filter(id_telegram=chat_id_bd).delete()
            return HttpResponse("Chat ID erroneo")

    return HttpResponse("Token erroneo o ID erroneo, fin del Proceso de registro")

         

def validar_chat_id(request,chat_id):
    """
    Valida el Chat id de la base de datos RegistroAdmin

    Keyword Arguments:
    chat_id : Id de telegram tomado de la funcion verificar_codigo_otp
    returns: Regresa un bool, True y False
    """
    chat_id = chat_id
    exists = models.RegistroAdmin.objects.filter(id_telegram=chat_id).exists()
    print(exists)
    return exists
    
   

def encriptar_password(secreto) -> string:
    """Cifra una cadena de contraseña con SHA256 y utilizando salt

    Args:
        secreto (String): Contraseña a cifrar

    Returns:
        String: Contraseña cifrada
    """
    salt = base64.b64encode(os.urandom(16)).decode('UTF-8')
    cifrado = crypt.crypt(secreto, '$6$' + salt)
    return cifrado



def redireccionar(request):
    logueado = request.session.get('logueado')
    if not logueado:
        return redirect('/autenticacion/')
    ip_server = request.session.get('IP_server')
    url = 'http://' + ip_server + ':6767'
    return redirect(url)



def estado_servidor(request):
    logueado = request.session.get('logueado')
    if not logueado:
        return redirect('/autenticacion/')
    t='monitoreo.html'
    d={'list':models.RegistroAdmin.objects.all()}
    return render(request,t,d)


def cerrar_sesion(request):
    request.session['logueado'] = False
    request.session.flush()
    return redirect('/autenticacion/')



def serializar_server(usuario,servidores, asociado):
    resultado = []
    servidores_usuario = []
    for admin in asociado:
        if usuario == admin.nombre_registro_admin:
            ip_servidor = admin.ip_servidor
            servidores_usuario.append(ip_servidor)

    for servidor in servidores:
        if servidor.ip in servidores_usuario:
            d_server = {'Admin':usuario,'IP':servidor.ip,'Hostname':servidor.server_name}
            resultado.append(d_server)
    return resultado

def recuperar_server(request):
    """
    Agrega los datos del servidor en la URL monitorizacion.

    Keyword Arguments:
    request --
    returns: JsonResponse
    """
    usuario = request.session.get('user')
    logueado = request.session.get('logueado')
    if not logueado:
        return redirect('/autenticacion/')
    servidores = models.Servidores.objects.all()
    asociado = models.Asociado.objects.all()
    return JsonResponse(serializar_server(usuario,servidores,asociado), safe=False)





