import os
import glob
from frequency_distributions import FrequencyDistribution
from answers_comparator import AnswersComparator


class DataProcessor:
    def __init__(self, samples_folder="samples", processed_folder="processed_csv"):
        self.samples_folder = samples_folder
        self.processed_folder = processed_folder
        os.makedirs(self.processed_folder, exist_ok=True)

    def get_csv_files(self):
        return glob.glob(os.path.join(self.samples_folder, "*.csv"))
    
    def process_all(self):
        csv_files = self.get_csv_files()
        for csv_path in csv_files:
            base_name = os.path.splitext(os.path.basename(csv_path))[0]
            processed_csv = os.path.join(self.processed_folder, f"{base_name}_processed.csv")

            comparator = AnswersComparator(csv_path, processed_csv)
            comparator.compare()

            freq_folder = f"frequency_charts_{base_name}"
            freq = FrequencyDistribution(processed_csv, output_dir=freq_folder)
            freq.comparator_charts()  # Gráfico completo
            freq.comparator_charts_answers()
            freq.comparator_charts_by_group()  #
            freq.comparator_charts_by_group_total()
            freq.comparator_charts_totals()

        print("Procesamiento por lotes completado.")

if __name__ == "__main__":
    batch = DataProcessor()
    batch.process_all()