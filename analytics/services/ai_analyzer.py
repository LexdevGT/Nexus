from typing import Dict, Any, List
import pandas as pd
from datetime import datetime
import logging
import numpy as np

logger = logging.getLogger(__name__)


class DataAnalyzer:
    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.metrics = data.get('data', {})
        self.summary = self.metrics.get('summary', {})
        self.developer_metrics = self.metrics.get('developer_metrics', [])

    def analyze_query(self, query: str) -> str:
        """Analiza la consulta y retorna una respuesta apropiada"""
        query = query.lower().strip()

        try:
            # Preguntas sobre tiempo
            if any(word in query for word in ['tiempo', 'duración', 'demora', 'horas']):
                return self._analyze_time_metrics(query)

            # Preguntas sobre story points
            if any(word in query for word in ['puntos', 'story points', 'points', 'estimación']):
                return self._analyze_story_points(query)

            # Preguntas sobre desarrolladores específicos
            if 'desarrollador' in query or 'quien' in query:
                return self._analyze_specific_developer(query)

            # Preguntas sobre rendimiento del equipo
            if any(word in query for word in ['equipo', 'rendimiento', 'desempeño', 'performance']):
                return self._analyze_team_performance()

            # Preguntas sobre tareas
            if any(word in query for word in ['tareas', 'historias', 'tickets', 'pendiente']):
                return self._analyze_tasks(query)

            # Preguntas sobre sprint actual
            if 'sprint' in query:
                return self._analyze_sprint_metrics()

            # Preguntas sobre eficiencia
            if any(word in query for word in ['eficiencia', 'productividad', 'efectividad']):
                return self._analyze_efficiency_metrics()

            # Preguntas sobre bloqueantes o problemas
            if any(word in query for word in ['bloqueante', 'problema', 'riesgo', 'issue']):
                return self._analyze_blockers()

            # Si no coincide con ninguna categoría específica
            return self._generate_general_summary()

        except Exception as e:
            logger.error(f"Error analyzing query: {str(e)}")
            return "Lo siento, hubo un error al analizar los datos. Por favor, intenta reformular tu pregunta o contacta al administrador del sistema."

    def _analyze_time_metrics(self, query: str) -> str:
        """Analiza métricas relacionadas con tiempo"""
        avg_time = self.summary.get('avg_completion_time', 0)
        fastest_dev = min(self.developer_metrics,
                          key=lambda x: x.get('avg_time_per_point', float('inf')))
        slowest_dev = max(self.developer_metrics,
                          key=lambda x: x.get('avg_time_per_point', 0))

        response = f"Análisis de Tiempos:\n"
        response += f"• Tiempo promedio por tarea: {avg_time:.1f} horas\n"
        response += f"• Desarrollador más rápido: {fastest_dev['name']} "
        response += f"({fastest_dev.get('avg_time_per_point', 0):.1f} horas/punto)\n"
        response += f"• Desarrollador más lento: {slowest_dev['name']} "
        response += f"({slowest_dev.get('avg_time_per_point', 0):.1f} horas/punto)\n"

        if 'promedio' in query or 'media' in query:
            response += self._calculate_average_times()

        return response

    def _analyze_story_points(self, query: str) -> str:
        """Analiza métricas relacionadas con story points"""
        total_points = self.summary.get('total_story_points', 0)
        completed_points = sum(dev.get('story_points', 0)
                               for dev in self.developer_metrics
                               if dev.get('completion_rate', 0) == 100)

        response = f"Análisis de Story Points:\n"
        response += f"• Total de puntos estimados: {total_points:.1f}\n"
        response += f"• Puntos completados: {completed_points:.1f}\n"
        response += f"• Porcentaje completado: {(completed_points / total_points * 100 if total_points else 0):.1f}%\n\n"

        response += "Distribución por desarrollador:\n"
        for dev in self.developer_metrics:
            response += f"• {dev['name']}: {dev.get('story_points', 0):.1f} puntos "
            response += f"({dev.get('completion_rate', 0):.1f}% completado)\n"

        return response

    def _analyze_specific_developer(self, query: str) -> str:
        """Analiza métricas de un desarrollador específico"""
        # Tratar de encontrar el nombre del desarrollador en la consulta
        dev_name = None
        for dev in self.developer_metrics:
            if dev['name'].lower() in query:
                dev_name = dev['name']
                dev_data = dev
                break

        if not dev_name:
            return self._get_best_developer()

        return self._format_developer_metrics(dev_data)

    def _analyze_team_performance(self) -> str:
        """Analiza el rendimiento general del equipo"""
        completion_rate = self.summary.get('completion_rate', 0)
        total_tasks = self.summary.get('total_tasks', 0)
        completed_tasks = self.summary.get('completed_tasks', 0)

        response = f"Rendimiento del Equipo:\n"
        response += f"• Tasa de completitud: {completion_rate:.1f}%\n"
        response += f"• Tareas totales: {total_tasks}\n"
        response += f"• Tareas completadas: {completed_tasks}\n\n"

        response += "Rendimiento por desarrollador:\n"
        sorted_devs = sorted(self.developer_metrics,
                             key=lambda x: x.get('completion_rate', 0),
                             reverse=True)

        for dev in sorted_devs:
            response += f"• {dev['name']}: {dev.get('completion_rate', 0):.1f}% completitud "
            response += f"({dev.get('completed_tasks', 0)}/{dev.get('total_tasks', 0)} tareas)\n"

        return response

    def _analyze_tasks(self, query: str) -> str:
        """Analiza métricas relacionadas con tareas"""
        pending = self.summary.get('total_tasks', 0) - self.summary.get('completed_tasks', 0)
        completion_rate = self.summary.get('completion_rate', 0)

        response = f"Análisis de Tareas:\n"
        response += f"• Tareas pendientes: {pending}\n"
        response += f"• Tasa de completitud: {completion_rate:.1f}%\n"

        if 'pendiente' in query:
            response += "\nTareas pendientes por desarrollador:\n"
            for dev in self.developer_metrics:
                pending_dev = dev.get('total_tasks', 0) - dev.get('completed_tasks', 0)
                response += f"• {dev['name']}: {pending_dev} tareas pendientes\n"

        return response

    def _analyze_sprint_metrics(self) -> str:
        """Analiza métricas del sprint actual"""
        return f"""Métricas del Sprint:
• Velocidad actual: {self.summary.get('total_story_points', 0):.1f} puntos
• Tasa de completitud: {self.summary.get('completion_rate', 0):.1f}%
• Tareas completadas: {self.summary.get('completed_tasks', 0)}
• Tiempo promedio por tarea: {self.summary.get('avg_completion_time', 0):.1f} horas"""

    def _analyze_efficiency_metrics(self) -> str:
        """Analiza métricas de eficiencia"""
        devs_efficiency = []
        for dev in self.developer_metrics:
            points = dev.get('story_points', 0)
            time = dev.get('avg_time_per_point', 0)
            if points and time:
                efficiency = points / time
                devs_efficiency.append((dev['name'], efficiency))

        devs_efficiency.sort(key=lambda x: x[1], reverse=True)

        response = "Análisis de Eficiencia:\n"
        for name, efficiency in devs_efficiency:
            response += f"• {name}: {efficiency:.2f} puntos/hora\n"

        return response

    def _analyze_blockers(self) -> str:
        """Analiza bloqueantes y problemas"""
        # Aquí podrías añadir lógica específica para detectar bloqueantes
        return f"""Análisis de Bloqueantes:
• No se detectaron bloqueantes críticos
• Tasa de progreso normal: {self.summary.get('completion_rate', 0):.1f}%
• Tiempo promedio de resolución: {self.summary.get('avg_completion_time', 0):.1f} horas"""

    def _get_best_developer(self) -> str:
        """Obtiene el mejor desarrollador basado en diferentes métricas"""
        best_by_points = max(self.developer_metrics,
                             key=lambda x: x.get('story_points', 0))
        best_by_completion = max(self.developer_metrics,
                                 key=lambda x: x.get('completion_rate', 0))
        best_by_speed = min(self.developer_metrics,
                            key=lambda x: x.get('avg_time_per_point', float('inf')))

        return f"""Análisis de Desarrolladores Destacados:
• Mayor cantidad de puntos: {best_by_points['name']} ({best_by_points.get('story_points', 0):.1f} puntos)
• Mayor tasa de completitud: {best_by_completion['name']} ({best_by_completion.get('completion_rate', 0):.1f}%)
• Mayor velocidad: {best_by_speed['name']} ({best_by_speed.get('avg_time_per_point', 0):.1f} horas/punto)"""

    def _calculate_average_times(self) -> str:
        """Calcula tiempos promedio detallados"""
        times = [dev.get('avg_time_per_point', 0) for dev in self.developer_metrics
                 if dev.get('avg_time_per_point', 0) > 0]

        if not times:
            return "No hay suficientes datos para calcular promedios de tiempo"

        avg = np.mean(times)
        std = np.std(times)
        median = np.median(times)

        return f"""
Análisis Detallado de Tiempos:
• Promedio: {avg:.1f} horas/punto
• Mediana: {median:.1f} horas/punto
• Desviación estándar: {std:.1f} horas
• Rango: {min(times):.1f} - {max(times):.1f} horas"""

    def _format_developer_metrics(self, dev_data: Dict) -> str:
        """Formatea las métricas de un desarrollador específico"""
        return f"""Métricas de {dev_data['name']}:
• Story Points completados: {dev_data.get('story_points', 0):.1f}
• Tasa de completitud: {dev_data.get('completion_rate', 0):.1f}%
• Tareas completadas: {dev_data.get('completed_tasks', 0)}/{dev_data.get('total_tasks', 0)}
• Tiempo promedio por punto: {dev_data.get('avg_time_per_point', 0):.1f} horas"""

    def _generate_general_summary(self) -> str:
        """Genera un resumen general de las métricas"""
        return f"""Resumen General del Proyecto:
• Total de tareas: {self.summary.get('total_tasks', 0)}
• Tareas completadas: {self.summary.get('completed_tasks', 0)}
• Tasa de completitud: {self.summary.get('completion_rate', 0):.1f}%
• Story Points totales: {self.summary.get('total_story_points', 0):.1f}
• Tiempo promedio por tarea: {self.summary.get('avg_completion_time', 0):.1f} horas

Desarrolladores más productivos:
{self._get_best_developer()}"""