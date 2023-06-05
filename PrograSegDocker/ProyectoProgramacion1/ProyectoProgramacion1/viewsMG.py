from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from datetime import datetime, timedelta
from bd import models 
from datetime import timezone

from django.contrib.auth import logout
from django.shortcuts import redirect


import random
import string
import time
import requests
import crypt
import os
import base64


def get_client_ip(request) -> ip:
    """
    Obtiene la direccion IP del usuario
    
    Keyword Arguments:
    request --
    return: ip
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def mandar_inicio(request) -> HttpResponse:
    """
    Vista de inicio con una cookie asignada

    Keyword Arguments:
    request -- 
    returns: HttpResponse 
    """
    respuesta = HttpResponse('Hola mundo, este es una pagina en produccion aun')
    respuesta.set_cookie('saludo','hola', max_age=None, samesite='Strict', secure=True,
                        httponly=True)
    return respuesta

def logout_view(request) -> redirect:
    """
    Regresa a la pagina de inicio
    
    Keyword Arguments:
    request --
    returns: redirect
    """
    logout(request)
    request.session.flush()
    messages.info(request, "Saliste exitosamente")
    return redirect('autenticacion/')

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
    """
    Determina si las credenciales existen
    
    Keyword Arguments:
    usuario: Nombre del usuario
    contra: Contraseña del usuario
    returns: bool
    """
    try:
        usuarios = models.LoginAdmin.objects.get(Nombre=usuario, Password=contra)
        return True
    except:
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
    #request.method == 'POST':
        errores = []
        usuario = request.POST.get('nombre','').strip()
        contra = request.POST.get('password','').strip()

        if puede_intentar_loguearse(request):
            if not usuario.strip() or not contra.strip():
                errores.append('No se ingreso usuario o contraseña')
                return render(request,template,{'errores':errores})

            if not credenciales(usuario,contra):
                errores.append('Usuario o Contraseña invalidos')
                return render(request,template,{'errores':errores})
            return redirect('/inicio/')
            #else:
            #    return render(request, template)
        else:
            return render(request, template, {'errores': ['Ya no tienes intentos, espera unos minutos']})
       

def validar_usuarios(nombre,correo,id_telegram,contraseña,contraseña2,ip_server) -> errores:
    """
    Valida que los campos del formulario no esten vacios
    
    Keyword Arguments:
    nombre: Nombre del usuario que ingresa
    correo: Correo del usuario que ingresa
    id_telegram: ID del usuario que ingresa
    contraseña: Contraseña del usuario que ingresa
    contraseña2: Segunda contraseña que ingresa el usuario
    ip_server: Direccion IP del servidor del usuario que ingresa
    
    return: errores
    """
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


def formulario_usuarios(request) -> render(request):
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
            enviar_otp(request, id_telegram)
            request.session['registrado'] = True
            return redirect('/verificar/')


def otp_time(request) -> HttpResponse:
    """
    Realiza la generacion del Codigo OTP, lo almacena en la sesion y contabiliza el tiempo
    hasta 3 minutos para cerrar el proceso de registro.

    Keyword Arguments:
    request: request, página de verificacion OTP
    returns: HttpResponse
    """
    t = 'verificar.html'
    errores = []
    otp = ''.join(random.choices(string.digits, k=6))
    request.session['opt'] = otp
    tiempo_inicio = time.time()
    tiempo_limite = tiempo_inicio + 180
    #chat_id = [] ##Tomarlo desde la base de datos
    
    enviar_otp(otp)
    while True:
        tiempo_actual = time.time()
        tiempo_restante = tiempo_limite - tiempo_actual

        if tiempo_restante <= 0:
            errores.append('El codigo OTP ha expirado')
            return render(request,t,{'errores':errores})
        


def enviar_otp(request, id_telegram) -> bool:
    """
    Envia el codigo OPT, verifica el chat_id del usuario y
    lo envia a travez del BOT de telegram del ID del usuario

    Keyword Arguments:
    otp: codigo OPT para enviar
    chat_id: str, ID del chat de telegram del usuario
    returns: bool, ¿¿¿Hace falta cambiar???

    """
    ##un for con el utlimo Tomas el chat id de la base de datos 
    #t = 'verificar.html'
    chat_id = id_telegram
    print("URL",chat_id)
    TOKEN = "6186600289:AAHuTujstEwq93x7oR8zmAjsoWLw1AjyeHY"
    #chat_id = chat_id
    otp = ''.join(random.choices(string.digits, k=6))
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={otp}" 
    requests.post(url)
    ## hacer otro for a la base de datos para verificar el chat_id 
    ## del usuario y compararlo con el OTP y darle return a la funcion
    ## con el chat_id
    tiempo_exp = datetime.now(timezone.utc) + timedelta(minutes=3)
    print(tiempo_exp)
    otp_bd = models.OTP(id_telegram=chat_id,otp=otp,tiempo_exp=tiempo_exp)
    otp_bd.save()
    return chat_id 
    




def verificar_codigo_otp_real(request) -> HttpResponse:
    """
    Verifica el código OTP almacenado en la sesión del navegador.

    Keyword Arguments:
    request: HttpRequest, solicitud HTTP
    returns: HttpResponse
    """
    #chat_id = enviar_otp(request)
    #print("chat_id =",chat_id)
    #otp = request.session.get('otp')

    ### hacer una bandera con el contador de las peticiones POST
    ### si pasa de uno borrar el token de inicio de sesion
    registrado = request.session.get('registrado', False)
    if not registrado:
        return redirect('/registro/')
    t = "verificar.html"
    if request.method == 'GET':
        return render(request,t)
    else:
        chat_id_bd = request.POST.get('id_telegram','').strip()
        codigo_otp = request.POST.get('codigo_otp','').strip()
        print("OTP form=",codigo_otp)
        print("CHATID=",chat_id_bd)
        for codigo_t in models.OTP.objects.all():
            id_tel = codigo_t.id_telegram
            print("id_telegram for =",id_tel)
            otp = codigo_t.otp
            print("codigo_otp for =",otp)
            if chat_id_bd == id_tel and codigo_otp == otp:
                print("Chat ID funciona")
                ultimo_id = models.OTP.objects.latest('id_telegram')
                ultimo_otp = models.OTP.objects.latest('otp')
                ultimo_id.delete()
                ultimo_otp.delete()
                return redirect('/inicio/')
         #else:
            #   errores = []
            #    errores.append('El codigo es erroneo')
                #render(request,t,{'errores':errores})
    return HttpResponse("Token erroneo")

## un if que verifique la fecha de tiempo de expiración del token,
## la base de datos debe de tener un campo de fecha de expiración
## del token
## tener una funcion ejecutandose que permita borrar tokens que han

## pasado el tiempo de 3 minutos.


## hacer un json o un javascript similar al del semestre pasado
## que haga peticiones constantes a una URL que llame a la funcion
## de verificacion de tiempo de los OTP

def tiempo_otp(request) -> request:
    """
    Borra los OTP con más de 3 minutos de tiempo

    Keyword Arguments:
    request --
    return: HttpResponse
    """
    tiempo_actual = datetime.now()
    for tiempo in models.OTP.objects.all():
        tiempo_exp = tiempo.tiempo_exp
        id_telegram = tiempo.id_telegram
        otp = tiempo.otp
        if tiempo_actual > tiempo_exp:
            otp.delete()
            id_telegram.delete()
            tiempo_exp.delete()
    return HttpResponse("Token expirado")






def verificar_codigo_otp(request) -> HttpResponse:
    """
    Verifica el código OTP almacenado en la sesión del navegador.

    Keyword Arguments:
    request: HttpRequest, solicitud HTTP
    returns: HttpResponse
    """
    #chat_id = enviar_otp(request)
    #print("chat_id =",chat_id)
    #otp = request.session.get('otp')

    ### hacer una bandera con el contador de las peticiones POST
    ### si pasa de uno borrar el token de inicio de sesion
    registrado = request.session.get('registrado', False)
    if not registrado:
        return redirect('/registro/')
    t = "verificar.html"
    if request.method == 'GET':
        return render(request,t)
    else:
        chat_id_bd = request.POST.get('id_telegram','').strip()
        codigo_otp = request.POST.get('codigo_otp','').strip()
        print("OTP form=",codigo_otp)
        print("CHATID=",chat_id_bd)
        tiempo_actual = datetime.now(timezone.utc) 
        for codigo_t in models.OTP.objects.all():
            id_tel = codigo_t.id_telegram
            tiempo_exp = codigo_t.tiempo_exp
            print("id_telegram for =",id_tel)
            otp = codigo_t.otp
            print("codigo_otp for =",otp)
            if tiempo_actual > tiempo_exp:
                #id_expirado = models.OTP.objects.filter('id_telegram'=id_telegram)
                #otp_expirado = models.OTP.objects.filter('otp'=otp)
                #time_expirado = models.OTP.objects.filter('tiempo_exp'=)
                registros_expirados = models.OTP.objects.filter(id_telegram=id_tel, otp=otp, tiempo_exp=tiempo_exp)
                print(registros_expirados)
                registros_expirados.delete()
                #id_expirado.delete()
                #otp_expirado.delete()
                #time_expirado.delete()
                return HttpResponse("OTP expirado")
            elif chat_id_bd == id_tel and codigo_otp == otp:
                print("Chat ID funciona")
                if codigo_otp == codigo_t.otp:
                    return redirect('/inicio')

                else:
                    errores = []
                    errores.append('El codigo es erroneo')
                    return render(request,t,{'errores':errores})

def encriptar_password(secreto) -> string:
    """Cifra una cadena de contraseña con SHA256 y utilizando salt

    Args:
        secreto (String): Contraseña a cifrar

    Returns:
        String: Contraseña cifrada
    """
    salt = base64.b64encode(os.urandom(16)).decode('UTF-8')
    cifrado = crypt.crypt(secreto, '$6' + salt )
    return cifrado




