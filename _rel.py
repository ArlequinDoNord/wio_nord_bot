# -*- coding: utf-8 -*-
import subprocess, os
o = r'G:\PyBOT\Projects\wio_nord_bot'
os.chdir(o)
env = dict(os.environ)
env['GIT_SSH_COMMAND'] = 'C:/Windows/System32/OpenSSH/ssh.exe'
env['PYTHONIOENCODING'] = 'utf-8'
SSH = 'C:/Windows/System32/OpenSSH/ssh.exe'

def run(*cmd, timeout=900, inp=None):
    r = subprocess.run(cmd, capture_output=True, env=env, timeout=timeout, input=inp)
    return (r.stdout + r.stderr).decode('utf-8', 'replace')

out = []
out.append("ADD: " + run('git', 'add', '-A'))
out.append("COMMIT: " + run('git', 'commit', '-m',
    'feat: v0.41.8 — старт праздника «Дни Пламенного Круговорота»: FIRE_LAB_ENABLED=True '
    '(кнопка Лабиринта, праздничные картинки локаций и города); смоуки 172/176 под флаг'))
out.append("TAG: " + run('git', 'tag', 'v0.41.8'))
out.append("SRV: " + run('git', 'push', 'server', 'main', '--tags'))
out.append("ORG: " + run('git', 'push', 'origin', 'main', '--tags'))
out.append("STATUS: '" + run('git', 'status', '--short') + "'")
open(os.path.join(o, '_rel.txt'), 'w', encoding='utf-8').write("\n".join(out))
print("done")
