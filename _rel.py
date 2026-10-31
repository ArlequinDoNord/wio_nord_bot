# -*- coding: utf-8 -*-
import subprocess, os
o = r'G:\PyBOT\Projects\wio_nord_bot'
os.chdir(o)
env = dict(os.environ)
env['GIT_SSH_COMMAND'] = 'C:/Windows/System32/OpenSSH/ssh.exe'
env['PYTHONIOENCODING'] = 'utf-8'

def run(*cmd, timeout=900):
    r = subprocess.run(cmd, capture_output=True, env=env, timeout=timeout)
    return (r.stdout + r.stderr).decode('utf-8', 'replace')

out = []
out.append("ADD: " + run('git', 'add', '-A'))
out.append("COMMIT: " + run('git', 'commit', '-m',
    'fix: v0.41.9 — миграция fire_lab_sessions.last_active_at (вход в лабиринт падал на проде), '
    'TypeError в иерархии клана; смоук 181 дополнен'))
out.append("TAG: " + run('git', 'tag', 'v0.41.9'))
out.append("SRV: " + run('git', 'push', 'server', 'main', '--tags'))
out.append("ORG: " + run('git', 'push', 'origin', 'main', '--tags'))
out.append("STATUS: '" + run('git', 'status', '--short') + "'")
open(os.path.join(o, '_rel.txt'), 'w', encoding='utf-8').write("\n".join(out))
print("done")
