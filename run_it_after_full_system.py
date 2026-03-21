import os
import time

os.system('pkill -f "python web/app.py"')
os.system('nohup python web/app.py > flask.log 2>&1 &')
time.sleep(4)
os.system('cat flask.log')
