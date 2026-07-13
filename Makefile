load:
	python src/etl/loader.py

test:
	pytest tests/

dashboard:
	streamlit run src/dashboard/app.py

report:
	python src/reports/report.py

api:
	python src/api/app.py

clean:
	python -c "import shutil, pathlib; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('__pycache__')]"