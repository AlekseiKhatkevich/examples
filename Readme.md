How to install examples project.

if you dont use PIPENV you might need to install it:
-----  pip install pipenv -----


- git clone project on your local machine


-----------------------------------
if you use Pycharm:

- right click  and 'open folder as a pycharm project'

then in Pycharm terminal:

in terminal:
- pipenv update
- python manage.py runserver
- open in browser http://127.0.0.1:8000

---------------------------------
Directly from console (without Pycharm)
- cd to project directory
- pipenv --python 3.8
- pipenv shell
- pipenv update
- python manage.py runserver
- open in browser http://127.0.0.1:8000


redis url in this project by default "redis://127.0.0.1:6379/1"
if you need to change it, you can do it in "examples/settings.py" at the end of the file in CACHES/LOCATION

If you ran into error during pipenv update:

if you use Windows , you might(not necessarily but possible) need to change in Pipfile :
lxml = "*"  to  lxml = {path = "./lxml-4.4.1-cp38-cp38-win32.whl"}
or any suitable build from  https://www.lfd.uci.edu/~gohlke/pythonlibs/#lxml
and run pipenv update one more time
