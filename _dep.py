# -*- coding: utf-8 -*-
"""Деплой v0.41.3: коммит, тег, два пуша, проверка прода."""
import subprocess, os
o = r'G:\PyBOT\Projects\wio_nord_bot'
os.chdir(o)
env = dict(os.environ)
env['GIT_SSH_COMMAND'] = 'C:/Windows/System32/OpenSSH/ssh.exe'
env['PYTHONIOENCODING'] = 'utf-8'

def run(*cmd, timeout=280):
    r = subprocess.run(cmd, capture_output=True, env=env, timeout=timeout)
    return (r.stdout + r.stderr).decode('utf-8', 'replace')

def tail(s, n=180):
    return s[-n:]

out = []
out.append("COMMIT: " + tail(run('git', 'add', '-A')))
out.append("COMMIT: " + tail(run('git', 'commit', '-m',
    'feat(firelab): v0.41.3 — картинки праздника (менеджер + раздел врагов), '
    'рыбы переименованы и скрыты, туристический сувенир, Сундук убран')))
out.append("TAG: " + tail(run('git', 'tag', 'v0.41.3')))
out.append("SRV: " + tail(run('git', 'push', 'server', 'main', '--tags')))
out.append("ORG: " + tail(run('git', 'push', 'origin', 'main', '--tags'), 140))
out.append("STATUS: '" + run('git', 'status', '--short') + "'")
r7 = run('C:/Windows/System32/OpenSSH/ssh.exe', '-o', 'BatchMode=yes',
         'arlequin@89.19.210.194',
         'echo "import config; print(\'remote VERSION:\', config.VERSION); '
         'print(\'LAB:\', config.FIRE_LAB_ENABLED)" | '
         'docker exec -i wio_nord_bot-wio_nord_bot-1 python -u -', timeout=150)
out.append("REMOTE:\n" + r7[-150:])
open(os.path.join(o, '_dep.txt'), 'w', encoding='utf-8').write("\n".join(out))
print("done")
