import subprocess, os
o = r'G:\PyBOT\Projects\wio_nord_bot'
os.chdir(o)
env = dict(os.environ)
env['PYTHONIOENCODING'] = 'utf-8'
def run(*cmd):
    r = subprocess.run(cmd, capture_output=True, env=env)
    return (r.stdout + r.stderr).decode('utf-8', 'replace')
run('git', 'add', '-A')
out = run('git', 'commit', '-m',
          'feat(firelab): пирог — затухающая регенерация 50% на 3 хода (движок '
          'items.regen, работает и в Лабиринте); Колодец в админ-меню рыбалки '
          '(рыбы праздника в water_fish, веса правятся админом); правило '
          'AGENTS: новые враги/ивенты — сразу разделы в админке')
open(r'G:\PyBOT\Projects\wio_nord_bot\_o.txt', 'w', encoding='utf-8').write(out)
