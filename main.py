import os
from src.loader import TribalLoader
from src.visualizer import TribalVisualizer


def main():
    # Obtener ruta absoluta
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, "data")

    # Crear el loader
    loader = TribalLoader(data_dir)

    # Cargar Excel
    df = loader.load_excel()
    if df is not None:
        print("\nColumnas disponibles:")
        for col in df.columns:
            print(f"- {col}")

        # Crear visualizador
        viz = TribalVisualizer(df)

        # Ejemplo de uso (ajusta las columnas según tus datos)
        # viz.create_line_plot('fecha', 'valor', 'Tendencia temporal')
        # viz.create_bar_plot('categoria', 'cantidad', 'Distribución por categoría')
        # viz.create_scatter_plot('x', 'y', 'color', 'Relación entre variables')

        # Estadísticas descriptivas
        print("\nEstadísticas descriptivas:")
        print(viz.generate_summary_stats())

    else:
        print("No se encontró ningún archivo Excel")


if __name__ == "__main__":
    main()