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
          'feat(admin): единые маркеры Хранилища во всех категориях: 🔴 «снят с '
          'продажи», пометка 🏪 «можно на рынок», легенда в шапке списка; smoke 139')
open(r'G:\PyBOT\Projects\wio_nord_bot\_o.txt', 'w', encoding='utf-8').write(out)
print(run('git', 'log', '--oneline', '-1'))
