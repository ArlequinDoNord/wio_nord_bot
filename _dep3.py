# -*- coding: utf-8 -*-
"""Деплой v0.41.1: коммит, тег, два пуша, проверка прода."""
import subprocess, os
o = r'G:\PyBOT\Projects\wio_nord_bot'
os.chdir(o)
env = dict(os.environ)
env['GIT_SSH_COMMAND'] = 'C:/Windows/System32/OpenSSH/ssh.exe'
env['PYTHONIOENCODING'] = 'utf-8'

def run(*cmd, timeout=280):
    r = subprocess.run(cmd, capture_output=True, env=env, timeout=timeout)
    return (r.stdout + r.stderr).decode('utf-8', 'replace')

def tail(s, n=200):
    return s[-n:]

out = []
out.append("COMMIT: " + tail(run('git', 'add', '-A')))
out.append("COMMIT: " + tail(run('git', 'commit', '-m',
    'feat(firelab): Фаза 3 — особые комнаты (Колодец+рыбалка/Древо/Сундук), '
    'счётчики визитов, финиш 25 -> Тир+1; сид предметов; релиз')))
print("\n".join(out))
out.clear()
out.append("TAG: " + tail(run('git', 'tag', 'v0.41.1')))
out.append("SRV: " + tail(run('git', 'push', 'server', 'main', '--tags')))
out.append("ORG: " + tail(run('git', 'push', 'origin', 'main', '--tags'), 160))
out.append("STATUS: '" + run('git', 'status', '--short') + "'")
r7 = run('C:/Windows/System32/OpenSSH/ssh.exe', '-o', 'BatchMode=yes',
         'arlequin@89.19.210.194',
         'echo "import config; print(\'remote VERSION:\', config.VERSION); '
         'print(\'LAB:\', config.FIRE_LAB_ENABLED)" | '
         'docker exec -i wio_nord_bot-wio_nord_bot-1 python -u -', timeout=150)
out.append("REMOTE:\n" + r7[-150:])
open(os.path.join(o, '_dep2.txt'), 'w', encoding='utf-8').write("\n".join(out))
print("\n".join(out))
