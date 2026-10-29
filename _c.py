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
          'feat(clan): Древо Пламенного Круговорота — клановое расширение tree: '
          'гейт 7 Ламп у членов, 🧘 медитация +20 ОД у Древа каждому члену '
          '(доп. к домашней Лампе), 🌿 Эссенция Памяти раз в 30 дней (глава '
          'собирает в инвентарь/на склад, продажа 500 НМ); smoke 178')
open(r'G:\PyBOT\Projects\wio_nord_bot\_o.txt', 'w', encoding='utf-8').write(out)
print(run('git', 'log', '--oneline', '-2'))
print("STATUS:", run('git', 'status', '--short')[:200])
