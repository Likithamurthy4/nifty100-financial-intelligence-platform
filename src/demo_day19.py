from analytics.radar import RadarChart

radar = RadarChart()

df = radar.load_data()

print(df.head())

radar.create_charts(df)

radar.close()

print("Day 19 Completed.")
