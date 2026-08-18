from screener.engine import ScreenerEngine
from screener.exporter import ScreenerExporter

engine = ScreenerEngine()

results = {}

for preset in engine.config:

    results[preset] = engine.apply_filters(preset)

exporter = ScreenerExporter()

exporter.export(results)
