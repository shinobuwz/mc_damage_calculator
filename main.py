"""
最优伤害词条计算器

伤害计算公式：
(base * (1 + x% + base_multiplier) + y) * (1 + 伤害加成z%) * (1 + 暴击率 * (总爆伤 - 1)) * 技能倍率

说明：
- base: 基础攻击力或基础生命值
- x%: 攻击百分比或生命百分比（来自装备）
- base_multiplier: 基础倍率加成（来自角色天赋、命座等，与x%同乘区相加）
- y: 固定攻击或固定生命
- z%: 伤害加成百分比
- 总爆伤: 总暴击伤害（如150% = 1.5），期望计算时用 (总爆伤 - 1)
- 技能倍率: 角色技能的伤害倍率
"""

import yaml
from dataclasses import dataclass
from typing import List, Dict
from itertools import product


@dataclass
class Equipment:
    """装备类"""
    category: str  # 装备类别 A/B/C
    main_stat_type: str  # 主词条类型
    main_stat_value: float  # 主词条数值
    sub_stat_type: str  # 副词条类型
    sub_stat_value: float  # 副词条数值

    def __repr__(self):
        return f"{self.category}类-主:{self.main_stat_type}{self.main_stat_value}+副:{self.sub_stat_type}{self.sub_stat_value}"


@dataclass
class Character:
    """角色类"""
    name: str
    base_type: str  # 'attack' 或 'hp'
    base_value: float  # 基础攻击力或生命值
    base_multiplier: float  # 基础倍率加成（与装备%同乘区）
    base_crit_rate: float  # 基础暴击率
    base_crit_dmg: float  # 总暴击伤害（如1.5表示150%）
    base_dmg_bonus: float  # 基础伤害加成
    skill_multiplier: float  # 技能倍率


@dataclass
class Stats:
    """属性汇总"""
    base_value: float  # 基础数值(攻击或生命)
    flat_attack: float  # 固定攻击
    percent_attack: float  # 攻击百分比
    flat_hp: float  # 固定生命
    percent_hp: float  # 生命百分比
    crit_rate: float  # 暴击率
    crit_dmg: float  # 总暴击伤害
    dmg_bonus: float  # 伤害加成


# 定义所有装备类型
EQUIPMENT_TYPES = {
    '4': [
        Equipment('4', '爆伤', 0.44, '固定攻击', 150),
        Equipment('4', '暴击', 0.22, '固定攻击', 150),
    ],
    '3': [
        Equipment('3', '生命%', 0.30, '固定攻击', 100),
        Equipment('3', '攻击%', 0.30, '固定攻击', 100),
        Equipment('3', '伤害加成', 0.30, '固定攻击', 100),
    ],
    '1': [
        Equipment('1', '生命%', 0.228, '固定生命', 2280),
        Equipment('1', '攻击%', 0.18, '固定生命', 2280),
    ]
}


def load_character(character_name: str) -> Character:
    """从配置文件加载角色数据"""
    with open('characters.yml', 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    char_data = data['characters'].get(character_name)
    if not char_data:
        raise ValueError(f"角色 {character_name} 未找到")

    return Character(
        name=character_name,
        base_type=char_data['base_type'],
        base_value=char_data['base_value'],
        base_multiplier=char_data.get('base_multiplier', 0.0),  # 默认0%
        base_crit_rate=char_data['base_crit_rate'],
        base_crit_dmg=char_data['base_crit_dmg'],
        base_dmg_bonus=char_data['base_dmg_bonus'],
        skill_multiplier=char_data.get('skill_multiplier', 1.0)  # 默认倍率为1.0
    )


def calculate_stats(character: Character, equipments: List[Equipment]) -> Stats:
    """计算装备后的总属性"""
    stats = Stats(
        base_value=character.base_value,
        flat_attack=0,
        percent_attack=0,
        flat_hp=0,
        percent_hp=0,
        crit_rate=character.base_crit_rate,
        crit_dmg=character.base_crit_dmg,
        dmg_bonus=character.base_dmg_bonus
    )

    for eq in equipments:
        # 主词条
        if eq.main_stat_type == '暴击':
            stats.crit_rate += eq.main_stat_value
        elif eq.main_stat_type == '爆伤':
            stats.crit_dmg += eq.main_stat_value
        elif eq.main_stat_type == '攻击%':
            stats.percent_attack += eq.main_stat_value
        elif eq.main_stat_type == '生命%':
            stats.percent_hp += eq.main_stat_value
        elif eq.main_stat_type == '伤害加成':
            stats.dmg_bonus += eq.main_stat_value

        # 副词条
        if eq.sub_stat_type == '固定攻击':
            stats.flat_attack += eq.sub_stat_value
        elif eq.sub_stat_type == '固定生命':
            stats.flat_hp += eq.sub_stat_value

    # 添加来自词条的固定值
    if hasattr(character, 'affix_stats'):
        stats.flat_attack += character.affix_stats.get('flat_atk', {}).get('total', 0)
        stats.flat_hp += character.affix_stats.get('flat_hp', {}).get('total', 0)

    return stats


def calculate_damage(character: Character, stats: Stats) -> float:
    """
    计算期望伤害
    公式：(base * (1 + x% + base_multiplier) + y) * (1 + 伤害加成z%) * (1 + 暴击率 * (总爆伤 - 1)) * 技能倍率

    base_multiplier 与装备百分比属于同一乘区，相加计算
    总爆伤：输入的是总暴击伤害（如150% = 1.5），期望计算时用 (总爆伤 - 1)
    """
    # 根据角色类型确定 base, x%, y
    if character.base_type == 'attack':
        base = stats.base_value  # 基础攻击
        x_percent = stats.percent_attack  # 攻击%（来自装备）
        y = stats.flat_attack  # 固定攻击
    else:  # hp
        base = stats.base_value  # 基础生命
        x_percent = stats.percent_hp  # 生命%（来自装备）
        y = stats.flat_hp  # 固定生命

    # 第一部分：(base * (1 + x% + base_multiplier) + y)
    # 注意：base_multiplier 与 x% 属于同一乘区，相加计算
    part1 = base * (1 + x_percent + character.base_multiplier) + y

    # 第二部分：* (1 + 伤害加成z%)
    part2 = 1 + stats.dmg_bonus

    # 第三部分：* (1 + 暴击率 * (总爆伤 - 1))
    # 期望伤害：普通伤害 * (1 - 暴击率) + 暴击伤害 * 暴击率
    # = 普通伤害 * (1 - 暴击率) + 普通伤害 * 总爆伤 * 暴击率
    # = 普通伤害 * (1 - 暴击率 + 总爆伤 * 暴击率)
    # = 普通伤害 * (1 + 暴击率 * (总爆伤 - 1))
    crit_rate = min(stats.crit_rate, 1.0)  # 暴击率上限100%
    part3 = 1 + crit_rate * (stats.crit_dmg - 1)

    # 第四部分：* 技能倍率
    part4 = character.skill_multiplier

    damage = part1 * part2 * part3 * part4
    return damage


def calculate_next_affix_gain(character: Character, stats: Stats, affix_avg_values: dict) -> dict:
    """
    计算每种词条增加一个平均值时的收益率

    Args:
        character: 角色对象
        stats: 当前属性
        affix_avg_values: 词条平均值字典，格式: {"crit_rate": 0.093, "crit_dmg": 0.186, ...}

    Returns:
        各词条的收益率字典
    """
    from copy import deepcopy

    current_damage = calculate_damage(character, stats)
    gains = {}

    # 测试各种词条
    affix_tests = [
        ("暴击", "crit_rate", lambda s, v: setattr(s, 'crit_rate', s.crit_rate + v)),
        ("爆伤", "crit_dmg", lambda s, v: setattr(s, 'crit_dmg', s.crit_dmg + v)),
        ("伤害加成", "dmg_bonus", lambda s, v: setattr(s, 'dmg_bonus', s.dmg_bonus + v)),
    ]

    # 根据角色类型添加百分比和固定值测试
    if character.base_type == 'attack':
        affix_tests.extend([
            ("攻击百分比", "percent", lambda s, v: setattr(s, 'percent_attack', s.percent_attack + v)),
            ("攻击固定值", "flat_atk", lambda s, v: setattr(s, 'flat_attack', s.flat_attack + v)),
        ])
    else:
        affix_tests.extend([
            ("生命百分比", "percent", lambda s, v: setattr(s, 'percent_hp', s.percent_hp + v)),
            ("生命固定值", "flat_hp", lambda s, v: setattr(s, 'flat_hp', s.flat_hp + v)),
        ])

    for label, key, modifier in affix_tests:
        if key not in affix_avg_values:
            continue

        # 创建临时stats副本
        temp_stats = deepcopy(stats)
        avg_value = affix_avg_values[key]

        # 应用修改
        modifier(temp_stats, avg_value)

        # 计算新伤害
        new_damage = calculate_damage(character, temp_stats)

        # 计算收益率
        gain_rate = (new_damage - current_damage) / current_damage * 100
        gains[label] = {
            "avg_value": avg_value,
            "damage_increase": new_damage - current_damage,
            "gain_rate": gain_rate
        }

    return gains


def find_best_combination(character: Character, verbose: bool = False):
    """
    找到最优装备组合

    Args:
        character: 角色对象
        verbose: 是否输出所有方案的详细信息
    """
    combinations = [
        ('44111', 2, 0, 3),
        ('43311', 1, 2, 2),
        ('43111', 1, 1, 3)
    ]

    best_result = None
    best_damage = 0
    all_results = []  # 存储所有方案的结果

    for combo_name, eq4_count, eq3_count, eq1_count in combinations:
        # 生成该组合下所有可能的装备搭配
        eq4_options = list(product(EQUIPMENT_TYPES['4'], repeat=eq4_count)) if eq4_count > 0 else [[]]
        eq3_options = list(product(EQUIPMENT_TYPES['3'], repeat=eq3_count)) if eq3_count > 0 else [[]]
        eq1_options = list(product(EQUIPMENT_TYPES['1'], repeat=eq1_count)) if eq1_count > 0 else [[]]

        combo_best_damage = 0
        combo_best_result = None

        for eq4s, eq3s, eq1s in product(eq4_options, eq3_options, eq1_options):
            # 组合所有装备
            equipments = list(eq4s) + list(eq3s) + list(eq1s)

            # 计算属性和伤害
            stats = calculate_stats(character, equipments)
            damage = calculate_damage(character, stats)

            if damage > combo_best_damage:
                combo_best_damage = damage
                combo_best_result = {
                    'combination': combo_name,
                    'equipments': equipments,
                    'stats': stats,
                    'damage': damage
                }

            if damage > best_damage:
                best_damage = damage
                best_result = {
                    'combination': combo_name,
                    'equipments': equipments,
                    'stats': stats,
                    'damage': damage
                }

        # 记录每种组合类型的最佳方案
        if combo_best_result:
            all_results.append(combo_best_result)

    if verbose:
        return best_result, all_results
    else:
        return best_result


def print_all_combinations(character: Character, all_results: List[Dict]):
    """输出所有组合方案的对比"""
    print(f"\n{'='*60}")
    print(f"所有装备组合方案对比")
    print(f"{'='*60}\n")

    # 按伤害排序
    sorted_results = sorted(all_results, key=lambda x: x['damage'], reverse=True)

    for i, result in enumerate(sorted_results, 1):
        stats = result['stats']
        combo_name = result['combination']
        damage = result['damage']

        # 计算基础数值
        if character.base_type == 'attack':
            base_dmg = stats.base_value * (1 + stats.percent_attack) + stats.flat_attack
            base_type_name = "攻击力"
        else:
            base_dmg = stats.base_value * (1 + stats.percent_hp) + stats.flat_hp
            base_type_name = "生命值"

        crit_multiplier = 1 + (min(stats.crit_rate, 1.0) * stats.crit_dmg)

        # 输出每个方案的摘要
        print(f"方案{i}: {combo_name}")
        print(f"  {base_type_name}: {base_dmg:.0f}  |  暴击率: {stats.crit_rate*100:.1f}%  |  爆伤: {stats.crit_dmg*100:.0f}%  |  伤害加成: {stats.dmg_bonus*100:.0f}%")
        print(f"  期望暴击倍率: {crit_multiplier:.3f}x")
        print(f"  期望伤害: {damage:.2f}")

        if i == 1:
            print(f"  ★ 最优方案")
        else:
            diff = (sorted_results[0]['damage'] - damage) / damage * 100
            print(f"  (比最优方案低 {diff:.2f}%)")

        print()

    print(f"{'='*60}\n")


def print_result(character: Character, result: Dict):
    """输出结果"""
    print(f"\n{'='*60}")
    print(f"角色：{character.name}")
    print(f"类型：{'攻击型' if character.base_type == 'attack' else '生命型'}")
    print(f"基础数值：{character.base_value}")
    print(f"技能倍率：{character.skill_multiplier * 100:.1f}%")
    print(f"{'='*60}")

    print(f"\n最优装备组合：{result['combination']}")
    print(f"\n装备详情：")
    for i, eq in enumerate(result['equipments'], 1):
        print(f"  {i}. {eq}")

    stats = result['stats']
    print(f"\n总属性：")
    print(f"  暴击率: {stats.crit_rate*100:.2f}%")
    print(f"  暴击伤害: {stats.crit_dmg*100:.2f}%")
    print(f"  伤害加成: {stats.dmg_bonus*100:.2f}%")
    if character.base_type == 'attack':
        final_attack = stats.base_value * (1 + stats.percent_attack) + stats.flat_attack
        print(f"  攻击力: {final_attack:.2f}")
        print(f"    (基础{stats.base_value} * {(1+stats.percent_attack)*100:.1f}% + {stats.flat_attack}固定)")
    else:
        final_hp = stats.base_value * (1 + stats.percent_hp) + stats.flat_hp
        print(f"  生命值: {final_hp:.2f}")
        print(f"    (基础{stats.base_value} * {(1+stats.percent_hp)*100:.1f}% + {stats.flat_hp}固定)")

    # 计算伤害组成部分用于展示
    if character.base_type == 'attack':
        base_dmg = stats.base_value * (1 + stats.percent_attack) + stats.flat_attack
    else:
        base_dmg = stats.base_value * (1 + stats.percent_hp) + stats.flat_hp

    crit_multiplier = 1 + (min(stats.crit_rate, 1.0) * stats.crit_dmg)
    dmg_bonus_multiplier = 1 + stats.dmg_bonus

    print(f"\n伤害计算详情：")
    print(f"  基础数值部分: {base_dmg:.2f}")
    print(f"  伤害加成倍率: {dmg_bonus_multiplier:.2f}x")
    print(f"  期望暴击倍率: {crit_multiplier:.2f}x")
    print(f"  技能倍率: {character.skill_multiplier:.2f}x")
    print(f"  期望伤害 = {base_dmg:.2f} × {dmg_bonus_multiplier:.2f} × {crit_multiplier:.2f} × {character.skill_multiplier:.2f}")
    print(f"  期望伤害：{result['damage']:.2f}")
    print(f"{'='*60}\n")


def main():
    """主函数"""
    print("=== 最优伤害词条计算器 ===\n")

    # 加载配置文件中的所有角色
    with open('characters.yml', 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    character_names = list(data['characters'].keys())

    print("可用角色：")
    for i, name in enumerate(character_names, 1):
        print(f"  {i}. {name}")

    # 选择角色
    choice = input("\n请输入角色编号（或直接输入角色名称）: ").strip()

    if choice.isdigit() and 1 <= int(choice) <= len(character_names):
        character_name = character_names[int(choice) - 1]
    else:
        character_name = choice

    try:
        # 加载角色
        character = load_character(character_name)

        print(f"\n正在计算 {character.name} 的最优装备方案...")

        # 查找最优组合（verbose模式）
        best_result, all_results = find_best_combination(character, verbose=True)

        # 先输出所有方案对比
        print_all_combinations(character, all_results)

        # 再输出最优方案的详细信息
        print_result(character, best_result)

    except Exception as e:
        print(f"\n错误: {e}")


if __name__ == '__main__':
    main()