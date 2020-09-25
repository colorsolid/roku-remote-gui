#!/usr/bin/python3.6 python3
from    roku import Roku
import  time


roku = Roku('192.168.1.107')

app = next((a for a in roku.apps if 'plex' in a.name.lower()), None)
if app:
    app.launch()
    time.sleep(20)
    for i in range(100):
        roku.volume_down()
    for i in range(14):
        roku.volume_up()
    roku.down()
    time.sleep(2)
    roku.select()
    time.sleep(2)
    roku.up()
    time.sleep(1)
    roku.up()
    time.sleep(1)
    roku.right()
    time.sleep(1)
    roku.right()
    time.sleep(1)
    roku.select()
    time.sleep(1)
    roku.down()
    time.sleep(1)
    roku.select()
    time.sleep(1)
    roku.right()
    time.sleep(1)
    roku.select()
