from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages

from .forms import urlForm
from .src.verify import get_results, is_valid_URL, get_file_valid_urls, get_trust_stores, get_keys_algorithms_list, get_keys_length_list, sort_new_certs, sort_old_certs, sort_certs_expire
from .src.certificate import *

lista_urls = []
lista_ids = []
lista_colors = []
lista_browsers = ['Microsoft Edge', 'Google Chrome', 'Mozilla Firefox']
display_button = True
display_warning = False
display_error = False
display_success = False
message_response = ""

microsoft_store, google_store, mozilla_store = get_trust_stores()

def index(request):
  global lista_colors
  global lista_urls
  global lista_ids
  global display_warning
  global display_error
  global display_success
  global message_response
  display_button = True
  if request.method == 'POST':
    form = urlForm(request.POST)
    if form.is_valid():

      # Obteniendo URL como string
      url_string = form.cleaned_data['url']

      # validación de URL
      # valid_url, response = is_valid_URL(url_string)

      # si no es válida y existe la URL
      #if valid_url != True:
      #  # Para mostrar mensajes de error
      #  messages.add_message(request, messages.ERROR, response)


      #get_chain_Certificate_Validator(url_string)
      #properties_ssl(url_string)
      lista_urls.insert(0, url_string)

      lista_ids.insert(0, len(lista_urls))

      # Funcion que verifica el nivel de confianza
      lista_browsers_colors = view_security_level(url_string)
      lista_colors.insert(0, lista_browsers_colors)

      # para mostrar el nivel de confianza con colores
      results = zip(lista_urls, lista_colors, lista_ids)
      context = {'form': form,
                  'lista_browsers':lista_browsers,
                  'results':results,
                  'display': display_button}
      return render(request, 'form.html', context)

  elif request.method == 'GET':
    # mensajes de error, warning o éxito en el procesamiento del archivo
    if display_warning == True:
      messages.add_message(request, messages.WARNING, message_response)
      display_warning = False
    elif display_error == True:
      messages.add_message(request, messages.ERROR, message_response)
      display_error = False
    elif display_success == True:
      messages.add_message(request, messages.SUCCESS, message_response)
      display_success = False

    form = urlForm()
    results = zip(lista_urls, lista_colors, lista_ids)

    # si la lista de URLs esta vacía
    if len(lista_urls) == 0:
      display_button = False
      context = {'form': form, 'display': display_button}
    # si la lista de URLs NO esta vacía
    else:
      display_button = True
      context = {'form': form,
                'lista_browsers':lista_browsers,
                'results':results,
                'display': display_button}
    return render(request, 'form.html', context)

def upload_file(request):
  global lista_ids
  global lista_colors
  global lista_urls
  global display_button
  global display_warning
  global display_error
  global display_success
  global message_response
  if request.method == 'POST':

    # leemos el archivo y lo obtenemos en bytes
    file_urls = request.FILES['file'].readlines()

    # decodificamoes y limpiamos la data
    file_urls = [ url.decode("utf-8").replace('\n','') for url in file_urls ]

    # obtenemos las urls válidas del archivo y sus colores respectivos
    urls, colors, ids = get_file_valid_urls(file_urls)

    # agregamos a las listas resultantes
    lista_urls = urls + lista_urls
    lista_colors = colors + lista_colors
    lista_ids = ids + lista_ids

    # verificamos si todas las URLs del archivo han sido procesadas
    # caso contrario mostramos mensajes de error al usuario
    if len(urls) > 0:
      display_button = True
      if len(file_urls) != len(urls) :
        display_warning = True
        message_response = "Existen URLs no válidas que no han sido procesadas"
      else:
        display_success = True
        message_response = "Todas las URLs han sido procesadas exitosamente"
    else:
      display_error = True
      if len(file_urls) == 0:
        message_response = "No se ha leído ninguna URL"
      else:
        message_response = "Todas las URLs son inválidas"

  return redirect('index')

def clean(request):
  global lista_colors
  global lista_urls
  lista_urls = []
  lista_colors = []
  return redirect('index')

def google_trust_Store(request):
  global google_store
  algs_list = get_keys_algorithms_list(google_store)
  keys_lens = get_keys_length_list(google_store)
  if request.method == 'POST':
    opt = request.POST.get('sort')
    if opt == 'new':
      google_store = sort_new_certs(google_store)
    elif opt == 'old':
      google_store = sort_old_certs(google_store)
    elif opt == 'expire':
      google_store = sort_certs_expire(google_store)
  return render(request, "google_trust_store/google_trust_store.html", {
      'certificates': google_store,
      'count': len(google_store),
      'algs_list': algs_list,
      'keys_lens': keys_lens
  })

def microsoft_trust_Store(request):
  global microsoft_store
  algs_list = get_keys_algorithms_list(microsoft_store)
  keys_lens = get_keys_length_list(microsoft_store)
  if request.method == 'POST':
    opt = request.POST.get('sort')
    if opt == 'new':
      microsoft_store = sort_new_certs(microsoft_store)
    elif opt == 'old':
      microsoft_store = sort_old_certs(microsoft_store)
    elif opt == 'expire':
      microsoft_store = sort_certs_expire(microsoft_store)
  return render(request, "microsoft_trust_store/microsoft_trust_store.html", {
      'certificates': microsoft_store,
      'count': len(microsoft_store),
      'algs_list': algs_list,
      'keys_lens': keys_lens,
      'sort_certs': sort_new_certs
  })

def mozilla_trust_Store(request):
  global mozilla_store
  algs_list = get_keys_algorithms_list(mozilla_store)
  keys_lens = get_keys_length_list(mozilla_store)
  if request.method == 'POST':
    opt = request.POST.get('sort')
    if opt == 'new':
      mozilla_store = sort_new_certs(mozilla_store)
    elif opt == 'old':
      mozilla_store = sort_old_certs(mozilla_store)
    elif opt == 'expire':
      mozilla_store = sort_certs_expire(mozilla_store)
  return render(request, "mozilla_trust_store/mozilla_trust_store.html", {
      'certificates': mozilla_store,
      'count': len(mozilla_store),
      'algs_list': algs_list,
      'keys_lens': keys_lens,
      'sort_certs': sort_new_certs
  })

def certificate_chain(request, id):
  global lista_urls
  if lista_urls:
    url = lista_urls[::-1][id-1]
    print(url, id)
    chain = get_certificate_chain(url)
    chain_dict = generate_dict_chain(chain)
    return render(request, "chain.html", {"chain_dict":chain_dict, 'url':url})
  else:
    return redirect('index')
