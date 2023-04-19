if test -d dist; rm -rf dist; end
. venv/bin/activate.fish
python3 -m pip install setuptools wheel twine
python3 setup.py sdist bdist_wheel
twine upload dist/*
deactivate
