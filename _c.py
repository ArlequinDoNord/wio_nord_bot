import subprocess, os
o = r'G:\PyBOT\Projects\wio_nord_bot'
os.chdir(o)
env = dict(os.environ)
env['PYTHONIOENCODING'] = 'utf-8'
def run(*cmd):
    r = subprocess.run(cmd, capture_output=True, env=env)
    print((r.stdout + r.stderr).decode('utf-8', 'replace')[:500])
    return (r.stdout + r.stderr).decode('utf-8', 'replace')
run('git', 'add', '-A')
out = run('git', 'commit', '-m',
          'feat(firelab): Фаза 4а — 13 предметов (экип с бонусами, Вилы, Трость, '
          'тыква), 2 рецепта, достижение «Чтящий Предков» + Лампа, зелья в '
          'лобое, burn-эффект оружия; smoke 175/176')
open(r'G:\PyBOT\Projects\wio_nord_bot\_out.txt', 'w', encoding='utf-8').write(out)
print(run('git', 'log', '--oneline', '-1'))
