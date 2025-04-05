from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from .forms import UsuarioForm
import requests
import xml.etree.ElementTree as ET
from .models import Usuario
from django.core.cache import cache

class Cadastro(View):
    template_name = 'cadastro.html'
    form_class = UsuarioForm

    def get(self, request):
        return render(request, self.template_name, {'form': self.form_class()})

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            codinome = self._get_codinome(form.cleaned_data['grupo'])
            obj = form.save(commit=False)
            obj.codinome = codinome
            obj.save()
            #return HttpResponse('Cadastro realizado com sucesso.')
        
        return render(request, self.template_name, {'form': form})
    
    def _get_codinome(self, grupo):
        if grupo == 'V':
            if not cache.get('vingadores'):  
                response = requests.get('https://raw.githubusercontent.com/uolhost/test-backEnd-Java/master/referencias/vingadores.json').json()
                cache.set('vingadores', response)

            codinomes = [i['codinome'] for i in cache.get('vingadores')['vingadores']]
        elif grupo == 'LJ':
            if not cache.get('liga_justica'):
                response = requests.get('https://raw.githubusercontent.com/uolhost/test-backEnd-Java/master/referencias/liga_da_justica.xml').content
                cache.set('liga_justica', response)
            
            root = ET.fromstring(cache.get('liga_justica'))
            codinomes_element = root.find('codinomes')
            codinomes = [codinome.text for codinome in codinomes_element.findall('codinome')]

        codinomes_usados = Usuario.objects.values_list('codinome', flat=True)

        codinomes_disponiveis = set(codinomes) - set(codinomes_usados)

        if not codinomes_disponiveis:
            return
        return list(codinomes_disponiveis)[0]

class Visualizar(View):
    template_name = "visualizar.html"

    def get(self, request):
        usuarios = Usuario.objects.all()
        return render(request, self.template_name, {'usuarios': usuarios})