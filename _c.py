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
          'feat(firelab): убрать Сундук сокровищ — его лут уже в дропах врагов '
          '(сено/ветки/леденец/рецепты); броски комнаты: Древо-Кол.->Босс->враг; '
          'картинки-менеджер без сундука; смоки 173/175 обновлены')
open(r'G:\PyBOT\Projects\wio_nord_bot\_o.txt', 'w', encoding='utf-8').write(out)
