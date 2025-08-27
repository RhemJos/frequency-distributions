import pandas as pd
import os
import matplotlib.pyplot as plt


class FrequencyDistribution:
    def __init__(self, csv_path, sample_size=None, output_dir="frequency_charts"):
        self.data_file = pd.read_csv(csv_path, sep=';', encoding='latin1', nrows=sample_size) if sample_size else pd.read_csv(csv_path, sep=';', encoding='latin1')
        self.output_dir = output_dir

    def generate_charts(self):
        os.makedirs(self.output_dir, exist_ok=True)
        for column in self.data_file.columns[6:]:
            frequency = self.data_file[column].value_counts(dropna=True)
            if len(frequency) == 0 or frequency.sum() == 0:
                continue
            try:
                sorted_index = sorted(frequency.index, key=lambda x: float(x))
                frequency = frequency.loc[sorted_index]
            except Exception:
                frequency = frequency.sort_index()

            plt.figure(figsize=(10, 6))
            bars = plt.bar(frequency.index.astype(str), frequency.values, color='green', alpha=0.7)
            plt.title(f'Distribución de Frecuencias: {column}')
            plt.xlabel("Respuesta")
            plt.ylabel("Frecuencia")

            for bar, value in zip(bars, frequency.values):
                plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), str(value),
                        ha='center', va='bottom', fontsize=8)

            plt.savefig(os.path.join(self.output_dir, f"{column}_freq.png"))
            print(f"Guardado: Gráfico de {column}")
            plt.close()

        print(f"Gráficos guardados en la carpeta '{self.output_dir}'")        


if __name__ == "__main__":
    csv_path = "boletas_d10.csv"
    Freq = FrequencyDistribution(csv_path)
    Freq.generate_charts()
    Freq_1 = FrequencyDistribution(csv_path, sample_size=100, output_dir="frequency_charts_sample")
    Freq_1.generate_charts()
