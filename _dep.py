# -*- coding: utf-8 -*-
import subprocess, os
o = r'G:\PyBOT\Projects\wio_nord_bot'
os.chdir(o)
env = dict(os.environ)
env['GIT_SSH_COMMAND'] = 'C:/Windows/System32/OpenSSH/ssh.exe'
env['PYTHONIOENCODING'] = 'utf-8'

def run(*cmd, timeout=280):
    r = subprocess.run(cmd, capture_output=True, env=env, timeout=timeout)
    return (r.stdout + r.stderr).decode('utf-8', 'replace')

out = []
out.append("ADD: " + run('git', 'add', '-A'))
out.append("COMMIT: " + run('git', 'commit', '-m',
    'feat(firelab): v0.41.5 — рецепт «Предания предков» (рыбный пирог: +60 HP, '
    'регенерация 4 хода, баф уворота +5%/сутки), выдача рецепта за ачивку «Рыбак древних», '
    'скрыт флагом праздника; движок regen_turns и dodge_buff; смоук 176 обновлён'))
out.append("TAG: " + run('git', 'tag', 'v0.41.5'))
out.append("SRV: " + run('git', 'push', 'server', 'main', '--tags'))
out.append("ORG: " + run('git', 'push', 'origin', 'main', '--tags'))
out.append("STATUS: '" + run('git', 'status', '--short') + "'")
r7 = run('C:/Windows/System32/OpenSSH/ssh.exe', '-o', 'BatchMode=yes',
         'arlequin@89.19.210.194',
         'echo "import config; print(\'remote VERSION:\', config.VERSION); '
         'print(\'LAB:\', config.FIRE_LAB_ENABLED)" | '
         'docker exec -i wio_nord_bot-wio_nord_bot-1 python -u -', timeout=150)
out.append("REMOTE:\n" + r7[-300:])
open(os.path.join(o, '_dep.txt'), 'w', encoding='utf-8').write("\n".join(out))
print("done")
