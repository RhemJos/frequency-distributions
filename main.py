import pandas as pd
import json
import csv

def main():
    output_file='./samples/sample_1_100_ballots.csv'
    data_file = pd.read_csv(output_file)
    for _, row in data_file.iterrows():
        answers = json.loads(row['answers'])
        ai_answers = json.loads(row['ai_answers'])
        for key in answers.keys():
            if "46.1.1" in key:
                print(f"46.1.X keys found in ANSWERS - Ballot: {row['id']} ")
        for key in ai_answers.keys():
            if "46.1.1" in key:
                print(f"46.1.X keys found in AI_ANSWERS - Ballot: {row['id']} ")
        

if __name__ == "__main__":
    main()
