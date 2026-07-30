from analytics.peer import PeerAnalytics

peer = PeerAnalytics()

df = peer.load_data()

print(df.head())

result = peer.compute_percentiles(df)

print(result.head())

peer.save(result)

peer.close()

print("Day 18 Completed.")