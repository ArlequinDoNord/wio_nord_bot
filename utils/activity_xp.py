"""Строка про опыт за обычную активность для ответов игроку.

Начисление и лимиты — в database.db.grant_activity_xp. Здесь только текст:
«+N XP» после удачного действия и однократное «лимит усвоения опыта» за сутки.
"""


async def activity_xp_line(user_id: int, amount: int, light: bool = False,
                           senior_amount: int = None) -> str:
    from database.db import grant_activity_xp
    from utils.localization import t

    res = await grant_activity_xp(user_id, amount, light=light, senior_amount=senior_amount)
    lines = []
    if res['granted']:
        lines.append(t("activity_xp.gain", n=res['granted']))
    if res['limit_hit']:
        lines.append(t("activity_xp.limit"))
    return "".join(f"\n{line}" for line in lines)


async def beast_xp_line(user_id: int, beast_key: str) -> str:
    from config import ACTIVITY_XP_BEASTS

    amount, light = ACTIVITY_XP_BEASTS.get(beast_key, (0, False))
    return await activity_xp_line(user_id, amount, light=light)
