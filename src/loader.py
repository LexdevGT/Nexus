# src/loader.py
import pandas as pd
import os
from analytics.services.data_processor import DataProcessor
from typing import Optional, Dict, Any


class TribalLoader:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self._processor = None

    def load_excel(self) -> Optional[pd.DataFrame]:
        """Carga el archivo Excel y retorna el DataFrame"""
        excel_files = [f for f in os.listdir(self.data_dir) if f.endswith('.xlsx')]
        if not excel_files:
            return None

        excel_path = os.path.join(self.data_dir, excel_files[0])
        df = pd.read_excel(excel_path)

        # Inicializar el procesador con los datos cargados
        self._processor = DataProcessor(df)
        return df

    def get_processed_data(self, time_filter: str = None, developer: str = None) -> Dict[str, Any]:
        """Obtiene los datos procesados con filtros aplicados"""
        if self._processor is None:
            self.load_excel()
            if self._processor is None:
                return {'status': 'error', 'message': 'No se pudo cargar el archivo Excel'}

        try:
            filtered_df = self._processor.filter_data(time_filter, developer)
            metrics = self._processor.calculate_metrics(filtered_df)

            return {
                'status': 'success',
                'data': metrics
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }