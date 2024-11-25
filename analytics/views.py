# analytics/views.py
from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import TemplateView
import os
from django.conf import settings
import sys
from pathlib import Path

# Asegurarnos que el directorio raíz está en el path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Imports locales
from analytics.services.ai_analyzer import DataAnalyzer
from analytics.services.data_processor import DataProcessor
from src.loader import TribalLoader


class DashboardView(TemplateView):
    template_name = 'analytics/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Tribal Nexus Analytics'
        return context

print("Data directory:", os.path.join(settings.BASE_DIR, 'data'))
print("Excel files:", os.listdir(os.path.join(settings.BASE_DIR, 'data')))
def get_chart_data(request):
    """Vista para obtener datos para los gráficos"""
    time_filter = request.GET.get('timeFilter', 'all')
    developer = request.GET.get('developer', 'all')

    try:
        # Usar el directorio de datos configurado
        data_dir = os.path.join(settings.BASE_DIR, 'data')
        loader = TribalLoader(data_dir)

        # Obtener datos procesados con filtros
        return JsonResponse(loader.get_processed_data(time_filter, developer))
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })


def analyze_data(request):
    """Vista para el análisis de IA"""
    query = request.GET.get('query', '')
    if not query:
        return JsonResponse({
            'response': 'Por favor, realiza una pregunta específica sobre los datos.'
        })

    try:
        # Cargar y procesar datos
        data_dir = os.path.join(settings.BASE_DIR, 'data')
        loader = TribalLoader(data_dir)
        processed_data = loader.get_processed_data()

        if processed_data['status'] != 'success':
            return JsonResponse({
                'response': 'No hay datos disponibles para analizar'
            })

        # Analizar con IA
        analyzer = DataAnalyzer(processed_data)
        response = analyzer.analyze_query(query)

        return JsonResponse({'response': response})
    except Exception as e:
        return JsonResponse({
            'response': f'Error al analizar los datos: {str(e)}'
        })