"""Контракты на поставку на рынке игроков (только граждане).

Правила (решения владельца 2026-11-20):
- Заказчик выставляет товар: количество от MIN_QTY до лимита, цена за единицу не ниже
  казённой (item.sell_price). Налог TAX_PERCENT% от суммы контракта — платит заказчик
  один раз при выставлении. Сумма и налог списываются сразу (эскроу).
- Лимит количества: MAX_QTY_BASE. После UNLOCK_AT_MAX штатно закрытых контрактов
  на MAX_QTY_BASE — до MAX_QTY_UNLOCKED. Считает заказчик.
- Закрытие целиком: исполнитель отдаёт всё количество, получает сумму контракта.
  Налога исполнитель не платит. Штатное закрытие — успешная сделка заказчика.
- Отмена заказчиком:
  * до SWITCH_AFTER_SUCCESSES успешных сделок — эскроу возвращается, налог остаётся в казне (вариант А);
  * с SWITCH_AFTER_SUCCESSES успешных — возвращается всё, кроме CANCEL_TAX_SHARE от налога (вариант Б);
    часть налога из казны возвращается заказчику.
- Срок — месяц (DURATION_DAYS). Истёкший контракт: эскроу возвращается полностью, налог остаётся (вариант А).
"""

from database.db import (
    add_inventory_item, add_nordmarks, add_treasury, get_db, get_inventory_item,
    get_item, get_user, remove_inventory_item, remove_nordmarks,
)

MIN_QTY = 20
MAX_QTY_BASE = 50
MAX_QTY_UNLOCKED = 100
UNLOCK_AT_MAX = 5
TAX_PERCENT = 12
SWITCH_AFTER_SUCCESSES = 5
CANCEL_TAX_SHARE = 0.25
DURATION_DAYS = 30


def quote(item_sell_price: int, qty: int, unit_price: int) -> dict:
    """Расчёт контракта: минимальная сумма, сумма, налог, итог для заказчика."""
    min_unit = int(item_sell_price or 0)
    total = int(qty) * int(unit_price)
    tax = total * TAX_PERCENT // 100
    return {
        "min_unit": min_unit,
        "min_total": int(qty) * min_unit,
        "min_pay": int(qty) * min_unit + int(qty) * min_unit * TAX_PERCENT // 100,
        "total": total,
        "tax": tax,
        "pay": total + tax,
    }


async def _count(sql: str, params: tuple) -> int:
    conn = await get_db()
    cur = await conn.execute(sql, params)
    row = await cur.fetchone()
    return int(row["n"] or 0)


async def success_count(buyer_id: int) -> int:
    return await _count(
        "SELECT COUNT(*) AS n FROM market_contracts WHERE buyer_id = ? AND status = 'closed'",
        (buyer_id,))


async def max_qty_for(buyer_id: int) -> int:
    at_max = await _count(
        "SELECT COUNT(*) AS n FROM market_contracts WHERE buyer_id = ? AND status = 'closed' AND qty >= ?",
        (buyer_id, MAX_QTY_BASE))
    return MAX_QTY_UNLOCKED if at_max >= UNLOCK_AT_MAX else MAX_QTY_BASE


async def _is_citizen(user_id: int) -> bool:
    from database.db import citizen_user_ids
    return user_id in await citizen_user_ids()


async def create_contract(buyer_id: int, item_id: int, qty: int, unit_price: int) -> tuple:
    """Выставляет контракт. Возвращает (ok, id или текст ошибки)."""
    if not await _is_citizen(buyer_id):
        return False, "Контракты доступны только гражданам."
    item = await get_item(item_id)
    if not item:
        return False, "Предмет не найден."
    if qty < MIN_QTY:
        return False, f"Минимум в контракте {MIN_QTY} шт."
    limit = await max_qty_for(buyer_id)
    if qty > limit:
        return False, f"Сейчас максимум в контракте {limit} шт."
    q = quote(item["sell_price"], qty, unit_price)
    if unit_price < q["min_unit"]:
        return False, f"Цена не ниже казённой: {q['min_unit']} НМ за шт."
    user = await get_user(buyer_id)
    if not user or int(user["nordmarks"] or 0) < q["pay"]:
        return False, f"Нужно {q['pay']} НМ (сумма {q['total']} + налог {q['tax']})."

    await remove_nordmarks(buyer_id, q["pay"], "market_contract",
                           f"Контракт: {item['name']} ×{qty} по {unit_price} НМ")
    await add_treasury(q["tax"], f"Налог с контракта: {item['name']} ×{qty}")
    conn = await get_db()
    cur = await conn.execute(
        "INSERT INTO market_contracts (buyer_id, item_id, qty, unit_price, total, tax, status, expires_at) "
        "VALUES (?, ?, ?, ?, ?, ?, 'open', datetime('now', ?))",
        (buyer_id, item_id, qty, unit_price, q["total"], q["tax"], f"+{DURATION_DAYS} days"))
    await conn.commit()
    return True, cur.lastrowid


async def _get(contract_id: int):
    conn = await get_db()
    cur = await conn.execute(
        "SELECT mc.*, i.name AS item_name FROM market_contracts mc "
        "JOIN items i ON i.id = mc.item_id WHERE mc.id = ?", (contract_id,))
    return await cur.fetchone()


async def close_contract(supplier_id: int, contract_id: int) -> tuple:
    """Исполнитель закрывает контракт целиком. Возвращает (ok, текст)."""
    if not await _is_citizen(supplier_id):
        return False, "Контракты доступны только гражданам."
    c = await _get(contract_id)
    if not c or c["status"] != "open":
        return False, "Контракт уже закрыт, отменён или истёк."
    if c["buyer_id"] == supplier_id:
        return False, "Нельзя закрыть свой контракт."
    inv = await get_inventory_item(supplier_id, c["item_id"])
    if not inv or int(inv["quantity"] or 0) < c["qty"]:
        return False, f"Нужно {c['qty']} шт. «{c['item_name']}» в инвентаре."

    await remove_inventory_item(supplier_id, c["item_id"], c["qty"])
    await add_nordmarks(supplier_id, c["total"], "market_contract_payout",
                        f"Контракт #{contract_id}: {c['item_name']} ×{c['qty']}")
    await add_inventory_item(c["buyer_id"], c["item_id"], c["qty"])
    conn = await get_db()
    await conn.execute(
        "UPDATE market_contracts SET status = 'closed', supplier_id = ?, closed_at = datetime('now') "
        "WHERE id = ?", (supplier_id, contract_id))
    await conn.commit()
    return True, f"Поставлено {c['qty']} шт. «{c['item_name']}», получено {c['total']} НМ."


async def cancel_contract(buyer_id: int, contract_id: int) -> tuple:
    """Отмена заказчиком. Возвращает (ok, сумма возврата или текст ошибки)."""
    c = await _get(contract_id)
    if not c or c["buyer_id"] != buyer_id or c["status"] != "open":
        return False, "Контракт нельзя отменить."
    successes = await success_count(buyer_id)
    if successes < SWITCH_AFTER_SUCCESSES:
        refund = c["total"]
    else:
        fee = int(c["tax"] * CANCEL_TAX_SHARE)
        returned_tax = c["tax"] - fee
        refund = c["total"] + returned_tax
        if returned_tax > 0:
            await add_treasury(-returned_tax, f"Возврат части налога по контракту #{contract_id}")
    await add_nordmarks(buyer_id, refund, "market_contract_refund",
                        f"Отмена контракта #{contract_id}")
    conn = await get_db()
    await conn.execute("UPDATE market_contracts SET status = 'cancelled' WHERE id = ?", (contract_id,))
    await conn.commit()
    return True, refund


async def expire_contracts() -> int:
    """Снимает истёкшие контракты: эскроу возвращается, налог остаётся (вариант А)."""
    conn = await get_db()
    cur = await conn.execute(
        "SELECT id, buyer_id, total FROM market_contracts "
        "WHERE status = 'open' AND expires_at < datetime('now')")
    rows = await cur.fetchall()
    for r in rows:
        await add_nordmarks(r["buyer_id"], r["total"], "market_contract_refund",
                            f"Истёк контракт #{r['id']}")
        await conn.execute("UPDATE market_contracts SET status = 'expired' WHERE id = ?", (r["id"],))
    await conn.commit()
    return len(rows)


async def list_open(viewer_id: int) -> list:
    """Открытые контракты для гражданина."""
    if not await _is_citizen(viewer_id):
        return []
    conn = await get_db()
    cur = await conn.execute(
        "SELECT mc.*, i.name AS item_name FROM market_contracts mc "
        "JOIN items i ON i.id = mc.item_id WHERE mc.status = 'open' AND mc.expires_at >= datetime('now') "
        "ORDER BY mc.id")
    return await cur.fetchall()
