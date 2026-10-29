# -*- coding: utf-8 -*-
"""Диагностика: сидянные предметы праздника + текущие дропы firelab."""
import sys, os
os.chdir(r'G:\PyBOT\Projects\wio_nord_bot')
sys.path.insert(0, '.')
import config as c  # noqa: E402

FIRE_NAMES = {
    "Призрачный Осетр": c.FIRE_LAB_FISH_OSETR_NAME,
    "Костяная Душа": c.FIRE_LAB_FISH_SOUL_NAME,
    "Пламенный Карп": c.FIRE_LAB_FISH_CARP_NAME,
    "Кусочек тыквенного пирога": c.FIRE_LAB_PIE_NAME,
    "Леденец языков пламени": c.FIRE_LAB_CANDY_NAME,
    "Пучок сена": c.FIRE_LAB_HAY_NAME,
    "Ветка дерева": c.FIRE_LAB_BRANCH_NAME,
    "Рецепт: Тыквенный пирог": c.FIRE_LAB_RECIPE_NAME,
    "Семечко тыквы": c.FIRE_PUMPKIN_SEED_NAME,
    "Тыква": c.FIRE_PUMPKIN_NAME,
    "Перо ворона": c.FIRE_CROW_FEATHER_NAME,
    "Моток железной проволоки": c.FIRE_WIRE_NAME,
    "Сахар": c.FIRE_SUGAR_NAME,
    "Яйца": c.FIRE_EGGS_NAME,
    "Огненный венец": c.FIRE_CROWN_NAME,
    "Плащ Памяти": c.FIRE_CLOAK_NAME,
    "Перчатки стража посевов": c.FIRE_GLOVES_NAME,
    "Вилы": c.FIRE_KEYS_NAME,
    "Обжигающая трость": c.FIRE_CANE_NAME,
    "Лампа Круговорота": c.FIRE_LANTERN_NAME,
    "Пламя Памяти": c.FIRE_AMBER_NAME,
    "Эссенция Памяти": c.FIRE_TREE_CLAN_ESSENCE_NAME,
    "Ручное пламенеющее устройство": c.FIRE_FLAME_DEVICE_NAME,
}

print("=== ПРЕДМЕТЫ ПРАЗДНИКА (сид в коде) ===")
for label, name in FIRE_NAMES.items():
    print(f"  • {name} ({label})")

print("\n=== ТЕКУЩИЕ ДРОПЫ firelab_enemies в коде ===")
for seed in getattr(c, "FIRELAB_ENEMY_SEEDS", ()):
    print(f"  {seed['name']}: drops = {seed['loot']}")
