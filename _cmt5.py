import subprocess, os
o = r'G:\PyBOT\Projects\wio_nord_bot'
os.chdir(o)
def run(*cmd):
    r = subprocess.run(cmd, capture_output=True)
    return (r.stdout + r.stderr).decode('utf-8', 'replace')[-300:]
print(run('git', 'add', '-A'))
print(run('git', 'commit', '-m',
          'feat(finance): история транзакций пилота для супер-админа '
          '(меню «финансы» → «История пилота», пагинация, контрагенты; smoke 174)'))
print(run('git', 'status', '--short'))
