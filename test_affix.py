"""
测试词条统计功能
"""

from main import Character, calculate_stats, calculate_damage, calculate_next_affix_gain, find_best_combination

# 创建测试角色
character = Character(
    name="测试角色",
    base_type="attack",
    base_value=2000,
    base_multiplier=0.2,
    base_crit_rate=0.05,
    base_crit_dmg=1.50,
    base_dmg_bonus=0.0,
    skill_multiplier=2.5
)

# 添加词条统计
character.affix_stats = {
    "crit_rate": {"count": 4, "avg": 0.093, "total": 0.372},
    "crit_dmg": {"count": 4, "avg": 0.186, "total": 0.744},
    "percent": {"count": 4, "avg": 0.101, "total": 0.404},
    "dmg_bonus": {"count": 4, "avg": 0.101, "total": 0.404},
    "flat_hp": {"count": 4, "avg": 510, "total": 2040},
    "flat_atk": {"count": 4, "avg": 40, "total": 160}
}

# 将词条属性应用到角色
character.base_crit_rate += character.affix_stats["crit_rate"]["total"]
character.base_crit_dmg += character.affix_stats["crit_dmg"]["total"]
character.base_dmg_bonus += character.affix_stats["dmg_bonus"]["total"]
character.base_multiplier += character.affix_stats["percent"]["total"]

print("="*60)
print("测试词条统计和收益率计算")
print("="*60)

# 找到最优组合
best_result, all_results = find_best_combination(character, verbose=True)

stats = best_result['stats']
damage = best_result['damage']

print(f"\n当前配置:")
print(f"  暴击率: {stats.crit_rate*100:.2f}%")
print(f"  暴击伤害: {stats.crit_dmg*100:.2f}%")
print(f"  伤害加成: {stats.dmg_bonus*100:.2f}%")
print(f"  攻击力: {stats.base_value * (1 + stats.percent_attack) + stats.flat_attack:.2f}")
print(f"  期望伤害: {damage:.2f}")

# 计算下一个词条的收益率
affix_avg_values = {key: val['avg'] for key, val in character.affix_stats.items()}
gains = calculate_next_affix_gain(character, stats, affix_avg_values)

print("\n下一个词条收益率分析:")
print("-"*60)
print(f"{'词条类型':<15} {'平均值':<12} {'伤害提升':<15} {'收益率'}")
print("-"*60)

# 按收益率排序
sorted_gains = sorted(gains.items(), key=lambda x: x[1]['gain_rate'], reverse=True)

for label, gain_info in sorted_gains:
    avg_val = gain_info['avg_value']
    dmg_inc = gain_info['damage_increase']
    gain_rate = gain_info['gain_rate']

    # 格式化平均值显示
    if label in ['暴击', '爆伤', '伤害加成', '攻击百分比']:
        avg_str = f"{avg_val*100:.1f}%"
    else:
        avg_str = f"{avg_val:.0f}"

    print(f"{label:<15} {avg_str:<12} {dmg_inc:<15.2f} {gain_rate:>6.2f}%")

print("\n" + "="*60)
best_affix = sorted_gains[0]
print(f"建议优先堆叠: {best_affix[0]} (收益率: {best_affix[1]['gain_rate']:.2f}%)")
print("="*60)
