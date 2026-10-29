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
          'feat(firelab): картинки праздника — менеджер admin «Картинки '
          'Круговорота» (вход/развилка/колодец/древо/сундук), раздел врагов в '
          'админ-редакторе, рисование фото во всех экранах Лабиринта; переименов '
          'рыб (Латимерия/Арована/Пылающая Душа) + все 24 предмета скрыты из '
          'магазина; smoke 173/175/176/179 фиксы')
open(r'G:\PyBOT\Projects\wio_nord_bot\_o.txt', 'w', encoding='utf-8').write(out)
print(run('git', 'log', '--oneline', '-1'))
