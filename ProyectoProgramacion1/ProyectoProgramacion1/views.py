from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from datetime import datetime
from bd import models 
from datetime import timezone

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



def credenciales(usuario,contra):
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
        numero = request.POST.get('numero','').strip()
        contraseña = request.POST.get('contraseña','').strip()
        contraseña2 = request.POST.get('contraseña2','').strip()
        errores = validar_usuarios(nombre,correo,numero,contraseña,contraseña2)

        if errores:
            c = {'errores': errores}
            return render(request, t, c)
        else:
            n_usuario = models.Usuario(nombre=nombre,
                                        correo=correo,
                                       numero=numero,
                                       contraseña=contraseña)
            n_usuario.save()
            #redirige a la verificacion del OTP
            return redirect('/verificar/')




def opt_time(request): -> HttpResponse
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
    request.session['opt'] = opt
    tiempo_inicio = time.time()
    tiempo_limite = tiempo_inicio + 180
    chat_id = [] ##Tomarlo desde la base de datos
    
    enviar_otp(otp, chat_id)
    while True:
        tiempo_actual = time.time()
        tiempo_restante = tiempo_limite - tiempo_actual

        if tiempo_restante <= 0:
            erroes.append('El codigo OTP ha expirado')
            return render(request,t,{'erroes':errores})


def enviar_otp(opt, chat_id):
    """
    Envia el codigo OPT, verifica el chat_id del usuario y
    lo envia a travez del BOT de telegram del ID del usuario

    Keyword Arguments:
    otp: codigo OPT para enviar
    chat_id: str, ID del chat de telegram del usuario
    returns: bool, ¿¿¿Hace falta cambiar???

    """
    TOKEN = "6186600289:AAHuTujstEwq93x7oR8zmAjsoWLw1AjyeHY"
    chat_id = chat_id
    opt = opt
    # mi chat_id "1863011260"
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage
    payload = {
        "chat_id": chat_id
        "text": opt
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return True
    else:
    return False


def verificar_codigo_otp(request):
    """
    Verifica el código OTP almacenado en la sesión del navegador.

    Keyword Arguments:
    request: HttpRequest, solicitud HTTP
    returns: HttpResponse
    """
    codigo_otp = request.GET.get('codigo_otp','')
    errores =  []

    if 'otp' in request.session:
        otp = request.session['otp']

        if codigo_otp == otp:
            # El código OTP es válido
            del request.session['otp']
            return redirect('/inicio/')

    # El código OTP es inválido
    else:
        erroes.append('El codigo OTP ha expirado')
        return render(request,t,{'erroes':errores})




