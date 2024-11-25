# src/visualizer.py
import plotly.express as px
import plotly.graph_objects as go
from typing import List

class TribalVisualizer:
    def __init__(self, df):
        self.df = df

    def create_line_plot(self, x_col: str, y_col: str, title: str = None):
        """Crea un gráfico de línea interactivo"""
        fig = px.line(self.df, x=x_col, y=y_col, title=title)
        fig.show()

    def create_bar_plot(self, x_col: str, y_col: str, title: str = None):
        """Crea un gráfico de barras interactivo"""
        fig = px.bar(self.df, x=x_col, y=y_col, title=title)
        fig.show()

    def create_scatter_plot(self, x_col: str, y_col: str, color_col: str = None, title: str = None):
        """Crea un gráfico de dispersión interactivo"""
        fig = px.scatter(self.df, x=x_col, y=y_col, color=color_col, title=title)
        fig.show()

    def create_histogram(self, col: str, title: str = None):
        """Crea un histograma interactivo"""
        fig = px.histogram(self.df, x=col, title=title)
        fig.show()

    def generate_summary_stats(self, columns: List[str] = None):
        """Genera estadísticas descriptivas"""
        if columns is None:
            columns = self.df.select_dtypes(include=['int64', 'float64']).columns
        return self.df[columns].describe()