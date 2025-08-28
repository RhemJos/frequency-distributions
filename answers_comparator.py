import pandas as pd
import json
import csv
# from deepdiff import DeepDiff

class AnswersComparator:
    def __init__(self, file):
        self.fields = ["qty_text", "choices", "other"]
        self.file = file
        self.data_file = pd.read_csv(self.file)
        self.results = []
        self.existing_columns = []

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

    def compare(self):
        self.get_existing_columns()
        fieldnames = ['id'] + self.existing_columns + ["total_differences", "percentage_differences"]


        for _, row in self.data_file[:3].iterrows():
            id_ = row['id']
            answers = json.loads(row['answers'])
            ai_answers = json.loads(row['ai_answers'])
            new_row = {'id': id_}
            diff_count = 0
            total_fields = 0

            # all_keys = set(ai_answers.keys()) | set(answers.keys())

            # for key in sorted(all_keys, key=lambda x: (len(x.split('.')), x)):
            # for key in answers.keys():
                # ai_val = ai_answers.get(key, {})
                # hu_val = answers.get(key, {})
                # for field in self.fields:
                #     col_name = f"{key}_{field}"
                #     if col_name not in self.existing_columns:
                #         continue
                #     if field == "choices":
                #         ai_choices = ai_val.get("choices") or []
                #         hu_choices = hu_val.get("choices") or []
                #         is_diff = 0 if set(ai_choices) == set(hu_choices) else 1
                #     else:
                #         ai_field = ai_val.get(field)
                #         hu_field = hu_val.get(field)
                #         is_diff = 0 if ai_field == hu_field else 1
                #     new_row[col_name] = is_diff
                #     diff_count += is_diff
                #     total_fields += 1

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

            # fieldnames = ['id']
            # for key in answers.keys():
            #     for field in self.fields:
            #         fieldnames.append(f"{key}_{field}")
            # fieldnames += ["total_differences", "percentage_differences"]

            csvfile = 'results.csv'
            with open(csvfile, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.results)

                # ai_data = {
                #     "choices": ai_val.get("choices", []),
                #     "qty_text": ai_val.get("qty_text"),
                #     "other": ai_val.get("other")
                # }
                # hu_data = {
                #     "choices": hu_val.get("choices", []),
                #     "qty_text": hu_val.get("qty_text"),
                #     "other": hu_val.get("other")
                # }
                # print(key)
                # print(ai_data)
                # print(hu_data)

            
        

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
    comparator = AnswersComparator(csv_path)
    comparator.compare()
    print("DONE")
