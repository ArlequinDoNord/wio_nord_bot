# -*- coding: utf-8 -*-
import subprocess, os
o = r'G:\PyBOT\Projects\wio_nord_bot'
env = dict(os.environ)
env['GIT_SSH_COMMAND'] = 'C:/Windows/System32/OpenSSH/ssh.exe'

script = r'''
import asyncio
from collections import defaultdict

async def go():
    import database.db as db
    from database.db import get_all_users
    from utils.combat_model import pilot_combat_stats

    users = await get_all_users()
    gears = []
    for u in users:
        try:
            st = await pilot_combat_stats(u['user_id'])
        except Exception:
            continue
        if not st:
            continue
        eq = await db.get_equipment(u['user_id'])
        has_gear = any(k in ('weapon', 'body', 'head', 'hands') for k in eq)
        if not has_gear:
            continue
        lo, hi = st.get('base_dmg') or (0, 0)
        w = st.get('weapon_damage') or 0
        w_lo, w_hi = (w if isinstance(w, tuple) else (w, w)) if w else (0, 0)
        gears.append({
            'uid': u['user_id'], 'hp': int(st.get('hp_max') or 0),
            'lo': lo + w_lo, 'hi': hi + w_hi,
            'armor': int(st.get('armor') or 0),
            'dodge': float(st.get('dodge') or 0),
        })

    def dist(key):
        vals = sorted(int(r[key]) for r in gears)
        n = len(vals)
        return f"med={vals[n//2]} p25={vals[max(0,n//4)]} p75={vals[min(n-1,3*n//4)]} min={vals[0]} max={vals[-1]}"

    print('GEARED PILOTS:', len(gears))
    print('DMG lo:', dist('lo'))
    print('DMG hi:', dist('hi'))
    print('HP:', dist('hp'))
    print('ARMOR:', dist('armor'))

    def rounds_range(dlo, dhi, en_hp, en_armor, dodge_pct=0.0):
        eff_lo = max(0, dlo - en_armor)
        eff_hi = max(0, dhi - en_armor)
        if eff_hi <= 0:
            return None
        # учёт уклонения врага: эффективный DPS*100/(100-dodge)
        k = 100.0 / max(1.0, 100.0 - dodge_pct)
        t_lo = -(-int(en_hp * k) // max(1, eff_hi))
        t_hi = -(-int(en_hp * k) // max(1, eff_lo)) if eff_lo else None
        return t_lo, t_hi

    enemies = {
        'Пугало 25/4/1/10':   {'hp':25,'atk':4,'armor':1,'dodge':10},
        'Дитя Яблони 27/3/0/9': {'hp':27,'atk':3,'armor':0,'dodge':9},
        'Ворон 16/3/0/20':    {'hp':16,'atk':3,'armor':0,'dodge':20},
        'Призрак 24/3/0/15':  {'hp':24,'atk':3,'armor':0,'dodge':15},
        'Босс Тыква 90/6/3/5':{'hp':90,'atk':6,'armor':3,'dodge':5},
    }
    print()
    for name, e in enemies.items():
        ks = []
        for r in gears:
            t = rounds_range(r['lo'], r['hi'], e['hp'], e['armor'], e['dodge'])
            if t:
                ks.append(t[0])
        if ks:
            ks.sort()
            n = len(ks)
            print(f"{name}: kill ходов (типичный удар делается hi) med={ks[n//2]} p90={ks[min(n-1,9*n//10)]} min={ks[0]} max={ks[-1]}")
        else:
            print(f"{name}: никто не может пробить")

    # Выживаемость: за сколько ходов враг убивает снаряжённого игрока
    print()
    for name, e in enemies.items():
        rr = []
        for r in gears:
            eff = max(1, e['atk'] - r['armor'])
            rr.append(-(-r['hp'] // eff))
        rr.sort()
        n = len(rr)
        print(f"{name}: игрок погибнет за ходов med={rr[n//2]} p25={rr[max(0,n//4)]} max={rr[-1]}")
    await db.close_db()

asyncio.run(go())
'''

cmd = (['C:/Windows/System32/OpenSSH/ssh.exe', '-o', 'BatchMode=yes',
        'arlequin@89.19.210.194',
        'docker exec -i -w /app wio_nord_bot-wio_nord_bot-1 python -u -'])
p = subprocess.run(cmd, input=script.encode('utf-8'), capture_output=True, env=env, timeout=180)
open(o + r'\_sal.txt', 'w', encoding='utf-8').write(p.stdout.decode('utf-8', 'replace'))
if p.returncode:
    open(o + r'\_sal.txt', 'a', encoding='utf-8').write('\nERR:\n' + p.stderr.decode('utf-8', 'replace')[-800:])
