"""Строка про опыт за обычную активность для ответов игроку.

Начисление и лимиты — в database.db.grant_activity_xp. Здесь только текст:
«+N XP» после удачного действия и однократное «лимит усвоения опыта» за сутки.
"""


async def activity_xp_line(user_id: int, amount: int) -> str:
    from database.db import grant_activity_xp
    from utils.localization import t

    res = await grant_activity_xp(user_id, amount)
    lines = []
    if res['granted']:
        lines.append(t("activity_xp.gain", n=res['granted']))
    if res['limit_hit']:
        lines.append(t("activity_xp.limit"))
    return "".join(f"\n{line}" for line in lines)
