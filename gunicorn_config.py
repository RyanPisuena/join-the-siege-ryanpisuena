bind = "0.0.0.0:5001"
workers = 4
reload = True
reload_engine = "auto"
reload_extra_files = [
    "src/app.py",
    "src/classifier.py"
] 