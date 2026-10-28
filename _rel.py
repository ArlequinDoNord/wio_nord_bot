# -*- coding: utf-8 -*-
import subprocess, os
o = r'G:\PyBOT\Projects\wio_nord_bot'
os.chdir(o)
def run(*cmd, **kw):
    return subprocess.run(cmd, capture_output=True, timeout=kw.pop('timeout', 280), **kw)

def out_str(r, n=140):
    return (r.stdout.decode('utf-8', 'replace') + r.stderr.decode('utf-8', 'replace'))[-n:]

r1 = run('git', 'add', '-A')
r = run('git', 'commit', '-m',
        'feat(event): Ф1.2 — выход после 25 комнат, босс-лимит 2 за заход, релиз 0.39.11')
rg = run('git', 'tag', 'v0.39.11')
env = dict(os.environ)
env['GIT_SSH_COMMAND'] = 'C:/Windows/System32/OpenSSH/ssh.exe'
r2 = run('git', 'push', 'server', 'main', '--tags', env=env, timeout=280)
r3 = run('git', 'push', 'origin', 'main', '--tags', timeout=280)
lod = run('git', 'log', '--oneline', '-1')
r4 = run('C:/Windows/System32/OpenSSH/ssh.exe', '-o', 'BatchMode=yes',
         'arlequin@89.19.210.194',
         'echo "import config; print(\'remote VERSION:\', config.VERSION); print(\'LAB:\', config.FIRE_LAB_ENABLED)" | docker exec -i wio_nord_bot-wio_nord_bot-1 python -u -',
         env=env, timeout=150)
result = "COMMIT: " + out_str(rg, 200) + "\nLOG: " + out_str(lod, 100) + \
         "\nSRV: " + out_str(r2, 220) + "\nORG: " + out_str(r3, 160) + \
         "\nREMOTE:\n" + r4.stdout.decode('utf-8', 'replace') + r4.stderr.decode('utf-8', 'replace')[-80:]
open(o + r'\_rel.txt', 'w', encoding='utf-8').write(result)
