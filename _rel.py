# -*- coding: utf-8 -*-
import subprocess, os
o = r'G:\PyBOT\Projects\wio_nord_bot'
os.chdir(o)
def run(*cmd, **kw):
    return subprocess.run(cmd, capture_output=True, timeout=kw.pop('timeout', 280), **kw)

run('git', 'add', '-A')
r = run('git', 'commit', '-m',
        'feat(event): Ф1.2 — выход после 25 комнат, босс-лимит 2 за заход, релиз 0.39.11')
r2 = run('git', 'tag', 'v0.39.11')
env = dict(os.environ)
env['GIT_SSH_COMMAND'] = 'C:/Windows/System32/OpenSSH/ssh.exe'
p1 = run('git', 'push', 'server', 'main', '--tags', env=env, timeout=280)
p2 = run('git', 'push', 'origin', 'main', '--tags', timeout=280)
st = run('git', 'status', '--short')
r3 = run('C:/Windows/System32/OpenSSH/ssh.exe', '-o', 'BatchMode=yes',
         'arlequin@89.19.210.194',
         'echo "import config; print(\'remote VERSION:\', config.VERSION); print(\'LAB:\', config.FIRE_LAB_ENABLED)" | docker exec -i wio_nord_bot-wio_nord_bot-1 python -u -',
         env=env, timeout=150)
open(o + r'\_rel.txt', 'w', encoding='utf-8').write(
    (r2.raw is not None and "" or "") + r2.stderr.decode('utf-8','replace') if False else
    (r2.raw is not None and "" or "") + ( ""
    ) + (p1.stderr.decode('utf-8','replace')[-140:] + "\nORG:" + p2.stderr.decode('utf-8','replace')[-100:]
    + "\nSTATUS:'" + st.stdout.decode('utf-8','replace')
    + "'\nREMOTE:\n" + r3.stdout.decode('utf-8','replace')))
