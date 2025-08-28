import pandas as pd
import json
import csv
import re

class AnswersComparator:
    def __init__(self, file, output_file='results.csv'):
        self.fields = ["qty_text", "choices", "other"]
        self.file = file
        self.data_file = pd.read_csv(self.file)
        self.results = []
        self.existing_columns = []
        self.csv_output_file = output_file

    def get_existing_columns(self):
        seen = set()
        for _, row in self.data_file.iterrows():
            answers = json.loads(row['answers'])
            ai_answers = json.loads(row['ai_answers'])
            for key in answers.keys():
                ai_val = ai_answers.get(key, {})
                hu_val = answers.get(key, {})
                for field in self.fields:
                    if (field in ai_val and ai_val[field] is not None) or (field in hu_val and hu_val[field] is not None):
                        column = f"{key}_{field}"
                        if column not in seen:
                            self.existing_columns.append(column)
                            seen.add(column)

    def custom_field_order(self):
        dominio_cols = []
        unidad_cols = []
        grado_cols = []
        contador_cols = []
        question_cols = []
        other_cols = []

        question_pattern = re.compile(r'^\d+(\.\d+)?_')

        for col in self.existing_columns:
            if col.startswith('dominio_'):
                dominio_cols.append(col)
            elif col.startswith('unidad_educativa_'):
                unidad_cols.append(col)
            elif col.startswith('grado_'):
                grado_cols.append(col)
            elif col.startswith('contador_'):
                contador_cols.append(col)
            elif question_pattern.match(col):
                qnum = col.split('_')[0]
                try:
                    qnum_float = float(qnum)
                except ValueError:
                    qnum_float = float('inf')
                question_cols.append((qnum_float, qnum, col))
            else:
                other_cols.append(col)

        question_cols_sorted = [col for _, _, col in sorted(question_cols, key=lambda x: (x[0], x[1], x[2]))]

        ordered = (
            ['id'] +
            sorted(dominio_cols) +
            sorted(unidad_cols) +
            sorted(grado_cols) +
            sorted(contador_cols) +
            question_cols_sorted +
            sorted(other_cols) +
            ["total_differences", "percentage_differences"]
        )
        return ordered


    def compare(self):
        self.get_existing_columns()
        fieldnames = ['id'] + self.existing_columns + ["total_differences", "percentage_differences"]
        fieldnames = self.custom_field_order()

        for _, row in self.data_file[:3].iterrows():
            id_ = row['id']
            answers = json.loads(row['answers'])
            ai_answers = json.loads(row['ai_answers'])
            new_row = {'id': id_}
            diff_count = 0
            total_fields = 0

            for column in self.existing_columns:
                key, field = column.rsplit('_', 1)
                ai_val = ai_answers.get(key, {})    
                hu_val = answers.get(key, {})
                if field == "choices":
                    ai_choices = ai_val.get("choices") or []
                    hu_choices = hu_val.get("choices") or []
                    is_diff = 0 if set(ai_choices) == set(hu_choices) else 1
                else:
                    ai_field = ai_val.get(field)
                    hu_field = hu_val.get(field)
                    is_diff = 0 if ai_field == hu_field else 1
                new_row[column] = is_diff
                diff_count += is_diff
                total_fields += 1

            new_row["total_differences"] = diff_count
            new_row["percentage_differences"] = round(100 * diff_count / total_fields, 2) if total_fields else 0
            self.results.append(new_row)

            with open(self.csv_output_file, 'w', newline='', encoding='utf-8') as csv_output_file:
                writer = csv.DictWriter(csv_output_file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.results)       

    def detect_key_differences(self, ai_answers, answers):
            if set(ai_answers.keys()) != set(answers.keys()):
                print("Son diferentes en las claves")
            ai_keys = set(ai_answers.keys())
            hu_keys = set(answers.keys())
           
            only_in_ai = ai_keys - hu_keys
            only_in_hu = hu_keys - ai_keys

            if only_in_ai:
                print(f"Claves solo en ai_answers: {only_in_ai}")
            if only_in_hu:
                print(f"Claves solo en answers: {only_in_hu}")
            # Claves solo en answers: {'31', '88', '89', '90', '98', '86', '103', '87', '21', '85', '129'}


if __name__ == "__main__":
    csv_path = "100 answers.csv"
    comparator = AnswersComparator(csv_path, "results 5.csv")
    comparator.compare()
    print("DONE")
