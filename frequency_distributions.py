import pandas as pd
import os
import matplotlib.pyplot as plt
import re


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

    def comparator_charts(self):
        os.makedirs(self.output_dir, exist_ok=True)
        # totals = self.data_file[self.data_file.columns[1:]].sum()
        cols = self.data_file.columns[1:]
        totals = self.data_file[cols[:-1]].sum()
        percentage_avg = self.data_file[cols[-1]].mean()
        totals[cols[-1]] = percentage_avg

        plt.figure(figsize=(max(12, len(totals) // 3), 8))  # Ajusta el ancho según la cantidad de columnas
        bars = plt.bar(totals.index, totals.values, color='green', alpha=0.7)
        plt.title('Frecuencia de diferencias por campo')
        plt.xlabel("Campo")
        plt.ylabel("Total de diferencias")
        plt.xticks(rotation=90, fontsize=8)
        plt.tight_layout()
        for bar, col, value in zip(bars, totals.index, totals.values):
            if "percentage" in col:
                label = f"{round(value, 2)}%"
            else:
                label = str(int(value))
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), label,
                    ha='center', va='bottom', fontsize=7)

        plt.savefig(os.path.join(self.output_dir, "diferencias_totales_por_campo.png"))
        print(f"Guardado: Gráfico único de diferencias en '{self.output_dir}'")
        plt.close()



        # for column in self.data_file.columns[1:]:
        #     frequency = self.data_file[column].value_counts(dropna=True)
        #     if len(frequency) == 0 or frequency.sum() == 0:
        #         continue
        #     try:
        #         sorted_index = sorted(frequency.index, key=lambda x: float(x))
        #         frequency = frequency.loc[sorted_index]
        #     except Exception:
        #         frequency = frequency.sort_index()

        #     plt.figure(figsize=(10, 6))
        #     bars = plt.bar(frequency.index.astype(str), frequency.values, color='green', alpha=0.7)
        #     plt.title(f'Distribución de Frecuencias: {column}')
        #     plt.xlabel("Respuesta")
        #     plt.ylabel("Frecuencia")

        #     for bar, value in zip(bars, frequency.values):
        #         plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), str(value),
        #                 ha='center', va='bottom', fontsize=8)

        #     plt.savefig(os.path.join(self.output_dir, f"{column}_freq.png"))
        #     print(f"Guardado: Gráfico de {column}")
        #     plt.close()

        # print(f"Gráficos guardados en la carpeta '{self.output_dir}'")

    def get_groups(self):
        group_ranges = [
            (1, 11),
            (12, 22),
            (23, 33),
            (34, 44),
            (45, 56),
            (57, 69),
            (70, 80),
            (81, 86),
            (87, 90),
            (91, 102),
            (103, 114),
            (115, 124),
            (125, 129)
        ]
        
        special_fields = ['dominio', 'unidad_educativa', 'grado', 'contador']

        groups = []
        columns = list(self.data_file.columns)
        if 'id' in columns:
            columns.remove('id')

        special_cols = [col for col in columns if any(col.startswith(f"{sp}_") for sp in special_fields)]

        for start, end in group_ranges:
            group_cols = []
            for col in columns:
                match = re.match(r'^(\d+)(\.\d+)?_', col)
                if match:
                    q_num = int(match.group(1))
                    if start <= q_num <= end:
                        group_cols.append(col)
            if start == 1:
                group_cols = special_cols + group_cols
            groups.append((f"{start}-{end}", group_cols))
        return groups

    def comparator_charts_by_group(self):
        os.makedirs(self.output_dir, exist_ok=True)
        groups = self.get_groups()
        for group_name, group_cols in groups:
            if not group_cols:
                continue
            totals = self.data_file[group_cols].sum()
            plt.figure(figsize=(max(12, len(totals) // 3), 8))
            bars = plt.bar(totals.index, totals.values, color='green', alpha=0.7)
            plt.title(f'Frecuencia de diferencias: preguntas {group_name}')
            plt.xlabel("Campo")
            plt.ylabel("Total de diferencias")
            plt.xticks(rotation=90, fontsize=8)
            plt.tight_layout()
            for bar, value in zip(bars, totals.values):
                plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), str(int(value)),
                         ha='center', va='bottom', fontsize=7)
            plt.savefig(os.path.join(self.output_dir, f"diferencias_{group_name}.png"))
            plt.close()
            print(f"Guardado: Gráfico de grupo {group_name} en '{self.output_dir}'")

    def comparator_charts_by_group_total(self):
        os.makedirs(self.output_dir, exist_ok=True)
        groups = self.get_groups()
        group_totals = []
        group_labels = []
        for idx, (group_name, group_cols) in enumerate(groups, 1):
            if not group_cols:
                continue
            total = self.data_file[group_cols].sum().sum()
            group_totals.append(total)
            group_labels.append(f"Página_{idx}")  
        plt.figure(figsize=(max(12, len(group_totals) * 2), 8))
        bars = plt.bar(group_labels, group_totals, color='green', alpha=0.9)
        plt.title('Total de diferencias por grupo')
        plt.xlabel("Grupo")
        plt.ylabel("Total de diferencias")
        plt.xticks(rotation=45, fontsize=10)
        plt.tight_layout()
        for bar, value in zip(bars, group_totals):
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), str(int(value)),
                    ha='center', va='bottom', fontsize=10)
        plt.savefig(os.path.join(self.output_dir, "diferencias_por_grupo.png"))
        plt.close()
        print(f"Guardado: Gráfico total por grupo en '{self.output_dir}'")

    # def comparator_charts_by_group_total(self):
    #     os.makedirs(self.output_dir, exist_ok=True)
    #     groups = self.get_groups()
    #     group_totals = []
    #     group_labels = []
    #     for group_name, group_cols in groups:
    #         if not group_cols:
    #             continue
    #         total = self.data_file[group_cols].sum().sum()
    #         group_totals.append(total)
    #         group_labels.append(group_name)
    #     plt.figure(figsize=(max(12, len(group_totals) * 2), 8))
    #     bars = plt.bar(group_labels, group_totals, color='green', alpha=0.6)
    #     plt.title('Total de diferencias por grupo')
    #     plt.xlabel("Grupo")
    #     plt.ylabel("Total de diferencias")
    #     plt.xticks(rotation=45, fontsize=10)
    #     plt.tight_layout()
    #     for bar, value in zip(bars, group_totals):
    #         plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), str(int(value)),
    #                  ha='center', va='bottom', fontsize=10)
    #     plt.savefig(os.path.join(self.output_dir, "diferencias_por_grupo.png"))
    #     plt.close()
    #     print(f"Guardado: Gráfico total por grupo en '{self.output_dir}'")

    def comparator_charts_totals(self):
        os.makedirs(self.output_dir, exist_ok=True)
        cols = self.data_file.columns[-2:]
        # totals = self.data_file[cols].sum()
        totals = self.data_file[cols[:-1]].sum()
        percentage_avg = self.data_file[cols[-1]].mean()
        totals[cols[-1]] = percentage_avg
        plt.figure(figsize=(6, 6))
        bars = plt.bar(totals.index, totals.values, color='green', alpha=0.3)
        plt.title('Totales generales de diferencias')
        plt.xlabel("Campo")
        plt.ylabel("Total")
        plt.tight_layout()
        for bar, col, value in zip(bars, totals.index, totals.values):
            if "percentage" in col:
                label = f"{round(value, 2)}%"
            else:
                label = str(round(value, 2))
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), label,
                    ha='center', va='bottom', fontsize=10)
        plt.savefig(os.path.join(self.output_dir, "totales_generales.png"))
        plt.close()
        print(f"Guardado: Gráfico de totales generales en '{self.output_dir}'")


    def safe_filename(self, name):
        return re.sub(r'[^a-zA-Z0-9_\-\.]', '_', name)


if __name__ == "__main__":
    csv_path = "boletas_d10.csv"
    Freq = FrequencyDistribution(csv_path)
    Freq.generate_charts()
    Freq_1 = FrequencyDistribution(csv_path, sample_size=100, output_dir="frequency_charts_sample")
    Freq_1.generate_charts()
