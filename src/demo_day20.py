from analytics.peer_report import PeerReport

report = PeerReport()

df = report.load_data()

print(df.head())

report.create_workbook(df)

report.close()

print("\n===================================")
print(" Day 20 Completed Successfully")
print("===================================")
