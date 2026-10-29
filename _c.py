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
          'feat(firelab): Фаза 5 — дроп-карточки врагов Лабиринта (Пугало/Дитя/'
          'Ворон/Хуб/Босс по весам ТЗ, шанс x Тир Огненного эха, выдача при '
          'победе блоком «Добыча»), РПУ и свиток трости в сиде; smoke 179')
open(r'G:\PyBOT\Projects\wio_nord_bot\_o.txt', 'w', encoding='utf-8').write(out)
