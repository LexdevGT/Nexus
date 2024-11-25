from typing import Dict, Any, List
import pandas as pd
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class DataProcessor:
    def __init__(self, df: pd.DataFrame):
        print("DataFrame recibido - Shape:", df.shape)
        self.df = df
        self._preprocess_data()

    def _preprocess_data(self):
        try:
            print("Columnas disponibles:", self.df.columns.tolist())

            # Convertir fechas
            date_columns = ['Creada', 'Actualizada', 'Resuelta']
            for col in date_columns:
                if col in self.df.columns:
                    print(f"Procesando columna {col}")
                    print(f"Muestra de valores {col}:", self.df[col].head())
                    self.df[col] = pd.to_datetime(self.df[col], format='%d/%b/%y %I:%M %p', errors='coerce')

            # Convertir tiempo trabajado
            if 'Tiempo Trabajado' in self.df.columns:
                print("Valores Tiempo Trabajado:", self.df['Tiempo Trabajado'].head())
                self.df['Tiempo_Horas'] = pd.to_numeric(self.df['Tiempo Trabajado'].fillna(0), errors='coerce') / 3600

            # Verificar y procesar Story Points
            story_points_col = 'Campo personalizado (Story Points)'
            if story_points_col in self.df.columns:
                print(f"Valores {story_points_col} antes de conversión:", self.df[story_points_col].head())
                self.df['Story Points'] = pd.to_numeric(self.df[story_points_col], errors='coerce').fillna(0)
                print("Valores Story Points después de conversión:", self.df['Story Points'].head())
            else:
                print(f"No se encontró la columna {story_points_col}")
                self.df['Story Points'] = 0

            # Verificar estado
            if 'Estado' in self.df.columns:
                print("Estados únicos:", self.df['Estado'].unique())

            # Verificar persona asignada
            if 'Persona asignada' in self.df.columns:
                print("Personas asignadas únicas:", self.df['Persona asignada'].unique())

            print("Preprocesamiento completado exitosamente")

        except Exception as e:
            print(f"Error en preprocesamiento: {str(e)}")
            logger.error(f"Error en preprocesamiento: {str(e)}")
            raise

    def filter_data(self, time_filter: str = 'all', developer: str = 'all') -> pd.DataFrame:
        print(f"Aplicando filtros - Time: {time_filter}, Developer: {developer}")
        df_filtered = self.df.copy()

        try:
            # Filtro de tiempo
            if time_filter != 'all':
                cutoff_date = datetime.now()
                if time_filter == 'month':
                    cutoff_date -= timedelta(days=30)
                elif time_filter == 'quarter':
                    cutoff_date -= timedelta(days=90)
                df_filtered = df_filtered[df_filtered['Creada'] >= cutoff_date]

            # Filtro de desarrollador
            if developer != 'all':
                df_filtered = df_filtered[df_filtered['Persona asignada'] == developer]

            print(f"Registros después de filtrar: {len(df_filtered)}")
            return df_filtered
        except Exception as e:
            print(f"Error en filtrado: {str(e)}")
            logger.error(f"Error en filtrado: {str(e)}")
            raise

    def calculate_metrics(self, df_filtered: pd.DataFrame) -> Dict[str, Any]:
        print("Iniciando cálculo de métricas")
        try:
            total_tasks = len(df_filtered)
            completed_tasks = len(df_filtered[df_filtered['Estado'] == 'Finalizada'])
            story_points = df_filtered['Story Points'].sum()

            print(f"Total tasks: {total_tasks}")
            print(f"Completed tasks: {completed_tasks}")
            print(f"Total story points: {story_points}")

            metrics = {
                'summary': {
                    'total_tasks': total_tasks,
                    'completed_tasks': completed_tasks,
                    'completion_rate': round((completed_tasks / total_tasks * 100), 1) if total_tasks > 0 else 0,
                    'total_story_points': round(story_points, 1),
                    'avg_completion_time': round(df_filtered['Tiempo_Horas'].mean(), 1)
                },
                'developer_metrics': self._calculate_developer_metrics(df_filtered),
                'recent_activity': self._get_recent_activity(df_filtered)
            }

            print("Métricas calculadas exitosamente")
            return metrics

        except Exception as e:
            print(f"Error calculando métricas: {str(e)}")
            logger.error(f"Error calculando métricas: {str(e)}")
            raise

    def _calculate_developer_metrics(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        print("Calculando métricas por desarrollador")
        dev_metrics = []

        for dev in df['Persona asignada'].unique():
            dev_df = df[df['Persona asignada'] == dev]
            completed_df = dev_df[dev_df['Estado'] == 'Finalizada']

            dev_points = completed_df['Story Points'].sum()
            dev_time = completed_df['Tiempo_Horas'].sum()

            metrics = {
                'name': dev,
                'total_tasks': len(dev_df),
                'completed_tasks': len(completed_df),
                'completion_rate': round((len(completed_df) / len(dev_df) * 100), 1) if len(dev_df) > 0 else 0,
                'story_points': round(dev_points, 1),
                'avg_time_per_point': round(dev_time / dev_points, 1) if dev_points > 0 else 0
            }

            print(f"Métricas para {dev}:", metrics)
            dev_metrics.append(metrics)

        return dev_metrics

    def _get_recent_activity(self, df: pd.DataFrame, limit: int = 10) -> List[Dict[str, Any]]:
        print("Obteniendo actividad reciente")
        try:
            recent = df.nlargest(limit, 'Actualizada')

            activities = [{
                'summary': row['Resumen'],
                'status': row['Estado'],
                'assignee': row['Persona asignada'],
                'updated': row['Actualizada'].strftime('%d/%m/%Y %H:%M') if pd.notnull(row['Actualizada']) else ''
            } for _, row in recent.iterrows()]

            print(f"Actividades recientes encontradas: {len(activities)}")
            return activities
        except Exception as e:
            print(f"Error obteniendo actividad reciente: {str(e)}")
            logger.error(f"Error obteniendo actividad reciente: {str(e)}")
            return []