"""
测试脚本 - 自动测试所有角色
"""

from main import load_character, find_best_combination, print_result, print_all_combinations
import yaml

def test_all_characters():
    """测试所有配置的角色"""
    with open('characters.yml', 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    character_names = list(data['characters'].keys())

    print("=== 自动测试所有角色 ===\n")

    for name in character_names:
        print(f"正在计算 {name} 的最优装备方案...\n")

        character = load_character(name)
        best_result, all_results = find_best_combination(character, verbose=True)

        # 输出所有方案对比
        print_all_combinations(character, all_results)

        # 输出最优方案详情
        print_result(character, best_result)

        print("\n" + "="*80 + "\n")

if __name__ == '__main__':
    test_all_characters()
