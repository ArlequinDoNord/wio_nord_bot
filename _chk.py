# -*- coding: utf-8 -*-
import subprocess, os
o = r'G:\PyBOT\Projects\wio_nord_bot'
SSH = 'C:/Windows/System32/OpenSSH/ssh.exe'
code = (
"import sqlite3\n"
"c = sqlite3.connect('/app/data/nordmark.db')\n"
"for t in ('fire_lab_sessions','fire_lab_entries','fire_lab_tier','user_fire_fish','firelab_enemies'):\n"
"    cols = [r[1] for r in c.execute('PRAGMA table_info(%s)' % t)]\n"
"    print(t, cols)\n"
)
r = subprocess.run([SSH, '-o', 'BatchMode=yes', 'arlequin@89.19.210.194',
    'docker exec -i wio_nord_bot-wio_nord_bot-1 python -u -'],
    input=code.encode('utf-8'), capture_output=True, timeout=170)
open(os.path.join(o, '_chk3.txt'), 'w', encoding='utf-8').write((r.stdout + r.stderr).decode('utf-8', 'replace') or 'NONE')
print("done")
