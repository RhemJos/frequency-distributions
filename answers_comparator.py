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
        self.existing_questions = []
        self.csv_output_file = output_file
        self.log_file = output_file.replace('.csv', '_log.txt')
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write(f"Differences log for {self.file}\n")
            f.write("="*30 + "\n")

    def register_differences(self, ballot__id, questions):
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"Ballot ID: {ballot__id}\n")
            f.write(f"-> Questions with differences: {', '.join(questions)}\n")
            f.write("\n")

    def register_total_fields(self, total_fields):
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"=> Total fields compared: {len(total_fields)}\n")
            f.write(f"=> Fields compared: {', '.join(total_fields)}\n")
            f.write("\n")

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

    def get_existing_questions(self):
        seen = set()
        for _, row in self.data_file.iterrows():
            answers = json.loads(row['answers'])
            for key in answers.keys():
                if key not in seen:
                    self.existing_questions.append(key)
                    seen.add(key)
                # else:
                    # print(f"Descartado: {key}")
        # print("Preguntas detectadas:", self.existing_questions)

    def custom_field_order(self):
        dominio = []
        unidad = []
        grado = []
        contador = []
        questions = []
        other = []

        # question_pattern = re.compile(r'^\d+(\.\d+)?_')
        pregunta_pattern = re.compile(r'^(\d+)(?:\.(\d+))?$')

        for q in self.existing_questions:
            if q.startswith('dominio'):
                dominio.append(q)
            elif q.startswith('unidad_educativa'):
                unidad.append(q)
            elif q.startswith('grado'):
                grado.append(q)
            elif q.startswith('contador'):
                contador.append(q)
            else:
                match = pregunta_pattern.match(q)
                if match:
                    num1 = int(match.group(1))
                    num2 = int(match.group(2)) if match.group(2) else -1
                    questions.append(((num1, num2), q))
                else:
                    other.append(q)

        
        ordered_questions = [q for _, q in sorted(questions, key=lambda x: (x[0][0], x[0][1]))]

        ordered = (
            ['id'] +
            sorted(dominio) +
            sorted(unidad) +
            sorted(grado) +
            sorted(contador) +
            ordered_questions +
            sorted(other) +
            ["total_differences", "percentage_differences"]
        )
        return ordered

    def compare(self):
        self.get_existing_questions()
        fieldnames = self.custom_field_order()

        for _, row in self.data_file.iterrows():
            id_ = row['id']
            answers = json.loads(row['answers'])
            ai_answers = json.loads(row['ai_answers'])
            new_row = {'id': id_}
            diff_count = 0
            total_fields = 0
            questions_with_diffs = []

            for question in self.existing_questions:
                ai_val = ai_answers.get(question, {})
                hu_val = answers.get(question, {})
                is_diff = 0

                # Comparar qty_text
                ai_qty = ai_val.get("qty_text")
                hu_qty = hu_val.get("qty_text")
                if ai_qty != hu_qty:
                    is_diff = 1
                    questions_with_diffs.append(question + "-qty_text")
                    # questions_with_diffs.append(ai_qty)
                    # questions_with_diffs.append(hu_qty)

                # Comparar choices (como conjuntos, usando [] si falta)
                ai_choices = ai_val.get("choices")
                hu_choices = hu_val.get("choices")
                ai_choices = ai_choices if isinstance(ai_choices, list) else []
                hu_choices = hu_choices if isinstance(hu_choices, list) else []
                if set(ai_choices) != set(hu_choices):
                    is_diff = 1
                    questions_with_diffs.append(question + "-choices")
                    # questions_with_diffs.append(ai_choices)
                    # questions_with_diffs.append(hu_choices)

                # Comparar other
                ai_other = ai_val.get("other")
                hu_other = hu_val.get("other")
                if ai_other != hu_other:
                    is_diff = 1
                    questions_with_diffs.append(question + "-other")
                    # questions_with_diffs.append(ai_other)
                    # questions_with_diffs.append(hu_other)

                new_row[question] = is_diff
                diff_count += is_diff
                total_fields += 1

            new_row["total_differences"] = diff_count
            new_row["percentage_differences"] = round(100 * diff_count / total_fields, 2) if total_fields else 0
            self.results.append(new_row)
            self.register_differences(id_, questions_with_diffs)
            self.register_total_fields(self.existing_questions)

        with open(self.csv_output_file, 'w', newline='', encoding='utf-8') as csv_output_file:
            writer = csv.DictWriter(csv_output_file, fieldnames=fieldnames, delimiter=';')
            writer.writeheader()
            writer.writerows(self.results)


    def old_compare(self):
        self.get_existing_columns()
        fieldnames = ['id'] + self.existing_columns + ["total_differences", "percentage_differences"]
        fieldnames = self.custom_field_order()

        for _, row in self.data_file.iterrows():
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
                writer = csv.DictWriter(csv_output_file, fieldnames=fieldnames, delimiter=';')
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
