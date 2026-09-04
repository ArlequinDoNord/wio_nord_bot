import random


def roll_dice(sides: int = 20) -> int:
    """Бросок кубика (d20 по умолчанию)."""
    return random.randint(1, sides)


def calculate_attack(damage_base: int, modifier: int = 0) -> int:
    """Итоговый урон = базовый урон + модификатор снаряжения + бросок d6."""
    bonus = roll_dice(6)
    return max(1, damage_base + modifier + bonus)


def calculate_enemy_damage(attack_power: int) -> int:
    """Урон от врага = сила атаки + бросок d4."""
    bonus = roll_dice(4)
    return max(1, attack_power + bonus)


def escape_chance(player_hp_percent: float, dice_roll: int = None) -> bool:
    """
    Шанс убежать = 50% + (1 - hp_percent) * 30%.
    Если hp < 50% — легче убежать.
    """
    if dice_roll is None:
        dice_roll = roll_dice(20)
    base_chance = 50 + int((1.0 - player_hp_percent) * 30)
    return dice_roll <= base_chance


def calculate_escape_damage() -> int:
    """Штрафной удар при неудачном побеге."""
    return roll_dice(8)


def get_enemy_attack_text(enemy_name: str, damage: int, player_hp: int) -> str:
    """Текст атаки врага."""
    return f"⚔️ {enemy_name} атакует! −{damage} HP\n❤️ Осталось: {player_hp}/100"


def get_player_attack_text(player_damage: int, enemy_name: str, enemy_hp: int, enemy_max_hp: int) -> str:
    """Текст атаки игрока."""
    bar = _hp_bar(enemy_hp, enemy_max_hp)
    return f"🗡️ Ты наносишь удар! −{player_damage} HP\n{bar}"


def get_enemy_attack_text_boss(boss_name: str, damage: int, player_hp: int) -> str:
    """Текст атаки босса."""
    return f"💀 {boss_name} обрушивает удар! −{damage} HP\n❤️ Осталось: {player_hp}/100"


def _hp_bar(current: int, maximum: int, length: int = 10) -> str:
    """Генерация полоски HP."""
    filled = int(length * current / maximum) if maximum > 0 else 0
    bar = "█" * filled + "░" * (length - filled)
    return f"[{bar}] {current}/{maximum}"


def get_enemy_bar(current: int, maximum: int, length: int = 10) -> str:
    """Полоска HP врага с числом."""
    filled = int(length * current / maximum) if maximum > 0 else 0
    bar = "█" * filled + "░" * (length - filled)
    return f"👾 HP врага: [{bar}] {current}/{maximum}"


def room_type_roll() -> str:
    """
    Определяет тип комнаты:
    - enemy (60%)
    - resource (25%)
    - empty (15%)
    """
    roll = roll_dice(100)
    if roll <= 60:
        return "enemy"
    elif roll <= 85:
        return "resource"
    else:
        return "empty"


def resource_amount(floor: int) -> int:
    """Количество НМ за ресурсную комнату (зависит от этажа)."""
    return random.randint(3, 8) + floor * 2
