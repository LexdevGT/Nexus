from typing import Dict, Any, Optional
import pandas as pd


class TribalAnalyzer:
    """Clase para análisis avanzado de datos y respuesta a consultas"""

    def __init__(self, df: Optional[pd.DataFrame] = None):
        self.df = df

    def set_data(self, df: pd.DataFrame):
        """Actualiza el DataFrame para análisis"""
        self.df = df

    def analyze_query(self, query: str) -> str:
        """Analiza la consulta y genera una respuesta"""
        if self.df is None or self.df.empty:
            return "No hay datos disponibles para analizar."

        query = query.lower()

        # Análisis de productividad general
        if any(word in query for word in ['productividad', 'rendimiento', 'desempeño']):
            return self._analyze_productivity()

        # Análisis de desarrolladores específicos
        if 'desarrollador' in query:
            return self._analyze_developer_performance()

        # Análisis de tiempos
        if any(word in query for word in ['tiempo', 'duración', 'horas']):
            return self._analyze_time_metrics()

        # Análisis de Story Points
        if any(word in query for word in ['puntos', 'story points', 'points']):
            return self._analyze_story_points()

        # Análisis de estado de tareas
        if any(word in query for word in ['estado', 'progreso', 'avance']):
            return self._analyze_task_status()

        return self._generate_general_summary()

    def _analyze_productivity(self) -> str:
        completed_tasks = self.df[self.df['Estado'] == 'Finalizada']
        total_points = completed_tasks['Story Points'].sum()
        avg_time_per_point = (completed_tasks['Tiempo_Horas'].sum() /
                              total_points if total_points > 0 else 0)

        return f"""Análisis de Productividad:
- Total de puntos completados: {total_points:.1f}
- Tiempo promedio por punto: {avg_time_per_point:.1f} horas
- Tareas completadas: {len(completed_tasks)}
- Eficiencia general: {self._calculate_efficiency_score():.1f}%"""

    def _analyze_developer_performance(self) -> str:
        dev_stats = []
        for dev in self.df['Persona asignada'].unique():
            dev_df = self.df[self.df['Persona asignada'] == dev]
            completed = dev_df[dev_df['Estado'] == 'Finalizada']

            stats = {
                'name': dev,
                'total_tasks': len(dev_df),
                'completed': len(completed),
                'points': completed['Story Points'].sum(),
                'time': completed['Tiempo_Horas'].sum()
            }
            dev_stats.append(stats)

        # Ordenar por puntos completados
        dev_stats.sort(key=lambda x: x['points'], reverse=True)

        response = "Análisis por Desarrollador:\n"
        for dev in dev_stats:
            response += f"\n{dev['name']}:\n"
            response += f"- Tareas: {dev['completed']}/{dev['total_tasks']}\n"
            response += f"- Puntos completados: {dev['points']:.1f}\n"
            response += f"- Tiempo total: {dev['time']:.1f} horas\n"

        return response

    def _analyze_time_metrics(self) -> str:
        completed = self.df[self.df['Estado'] == 'Finalizada']
        total_time = completed['Tiempo_Horas'].sum()
        avg_time = completed['Tiempo_Horas'].mean()

        return f"""Análisis de Tiempos:
- Tiempo total invertido: {total_time:.1f} horas
- Tiempo promedio por tarea: {avg_time:.1f} horas
- Tareas más largas: {self._get_longest_tasks()}"""

    def _analyze_story_points(self) -> str:
        completed = self.df[self.df['Estado'] == 'Finalizada']
        total_points = completed['Story Points'].sum()
        points_per_dev = completed.groupby('Persona asignada')['Story Points'].sum()

        return f"""Análisis de Story Points:
- Total de puntos completados: {total_points:.1f}
- Distribución por desarrollador:
{points_per_dev.to_string()}
- Promedio de puntos por tarea: {(total_points / len(completed)):.1f}"""

    def _analyze_task_status(self) -> str:
        status_count = self.df['Estado'].value_counts()
        total = len(self.df)

        response = "Estado de las Tareas:\n"
        for status, count in status_count.items():
            percentage = (count / total) * 100
            response += f"- {status}: {count} ({percentage:.1f}%)\n"

        return response

    def _calculate_efficiency_score(self) -> float:
        """Calcula un puntaje de eficiencia basado en varios factores"""
        completed = self.df[self.df['Estado'] == 'Finalizada']
        if len(completed) == 0:
            return 0

        # Factores a considerar
        completion_rate = len(completed) / len(self.df)
        points_completed = completed['Story Points'].sum()
        time_efficiency = (completed['Story Points'].sum() /
                           completed['Tiempo_Horas'].sum() if completed['Tiempo_Horas'].sum() > 0 else 0)

        # Ponderación de factores
        score = (completion_rate * 0.4 +
                 (points_completed / (points_completed + 10)) * 0.3 +
                 (time_efficiency / (time_efficiency + 1)) * 0.3)

        return score * 100

    def _get_longest_tasks(self, limit: int = 3) -> str:
        longest = self.df.nlargest(limit, 'Tiempo_Horas')

        response = ""
        for _, task in longest.iterrows():
            response += f"\n- {task['Resumen']}: {task['Tiempo_Horas']:.1f}h"

        return response

    def _generate_general_summary(self) -> str:
        total_tasks = len(self.df)
        completed = self.df[self.df['Estado'] == 'Finalizada']
        completion_rate = (len(completed) / total_tasks) * 100 if total_tasks > 0 else 0

        return f"""Resumen General del Proyecto:
- Total de tareas: {total_tasks}
- Tareas completadas: {len(completed)}
- Tasa de completitud: {completion_rate:.1f}%
- Story points totales: {self.df['Story Points'].sum():.1f}
- Tiempo total registrado: {self.df['Tiempo_Horas'].sum():.1f} horas"""