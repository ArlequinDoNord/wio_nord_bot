# -*- coding: utf-8 -*-
import subprocess, os
o = r'G:\PyBOT\Projects\wio_nord_bot'
os.chdir(o)
def run(*cmd, **kw):
    return subprocess.run(cmd, capture_output=True, timeout=kw.pop('timeout', 280), **kw)

def out_str(r, n=120):
    return (r.stdout.decode('utf-8', 'replace') + r.stderr.decode('utf-8', 'replace'))[-n:]

r1 = run('git', 'add', '-A')
r2 = run('git', 'commit', '-m',
         'feat(event): Фаза 2 — боёвка Огненного Лабиринта (5 врагов с эффектами), Огненное эхо (Тир 1-5), релиз 0.40.0')
r3 = run('git', 'tag', 'v0.40.0')
env = dict(os.environ)
env['GIT_SSH_COMMAND'] = 'C:/Windows/System32/OpenSSH/ssh.exe'
r4 = run('git', 'push', 'server', 'main', '--tags', env=env, timeout=280)
r5 = run('git', 'push', 'origin', 'main', '--tags', timeout=280)
r6 = run('git', 'status', '--short')
r7 = run('C:/Windows/System32/OpenSSH/ssh.exe', '-o', 'BatchMode=yes',
         'arlequin@89.19.210.194',
         'echo "import config; print(\'remote VERSION:\', config.VERSION); print(\'LAB:\', config.FIRE_LAB_ENABLED)" | docker exec -i wio_nord_bot-wio_nord_bot-1 python -u -',
         env=env, timeout=150)
res = out_str(r3, 130) + "\nSRV: " + out_str(r4, 140) + "\nORG: " + out_str(r5, 100) + \
      "\nSTATUS: '" + r6.stdout.decode('utf-8', 'replace') + "'" + \
      "\nREMOTE:\n" + r7.stdout.decode('utf-8', 'replace')
open(o + r'\_r.txt', 'w', encoding='utf-8').write(res)
