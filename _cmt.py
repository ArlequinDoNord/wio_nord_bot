# -*- coding: utf-8 -*-
import subprocess, os
o = r'G:\PyBOT\Projects\wio_nord_bot'
os.chdir(o)
env = dict(os.environ)
env['PYTHONIOENCODING'] = 'utf-8'
def run(*cmd):
    r = subprocess.run(cmd, capture_output=True, env=env)
    print((r.stdout + r.stderr).decode('utf-8', 'replace')[:400])
run('git', 'add', '-A')
run('git', 'commit', '-m',
    'feat(firelab): Ф4б — Лампа Круговорота в личном жилье: 🧘 медитация +20 ОД '
    'раз в сутки, 🪵 Пламя Памяти раз в 7 суток (генератор работает всегда, '
    'выдача — только на празднике); smoke 177')
print(run('git', 'log', '--oneline', '-2'))
print("STATUS:", run('git', 'status', '--short'))
