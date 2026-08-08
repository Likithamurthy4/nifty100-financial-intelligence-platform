from nlp.parser import AnalysisParser

parser = AnalysisParser()

df = parser.export()

print(df.head())

parser.close()

print()

print("Day 29 Completed.")