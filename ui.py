"""
伤害计算器 - 图形界面版本
使用 tkinter 实现简单的 GUI
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import yaml
from main import Character, find_best_combination, calculate_stats, calculate_damage, calculate_next_affix_gain


class DamageCalculatorUI:
    def __init__(self, root):
        self.root = root
        self.root.title("伤害计算器")
        self.root.geometry("900x700")

        # 加载现有角色配置
        self.load_characters()

        # 创建界面
        self.create_widgets()

    def load_characters(self):
        """加载角色配置"""
        try:
            with open('characters.yml', 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            self.characters = data['characters']
        except FileNotFoundError:
            self.characters = {}

    def create_widgets(self):
        """创建UI组件"""
        # 主容器
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置行列权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=0)  # 词条统计列固定宽度

        # ===== 左侧：角色配置区 =====
        config_frame = ttk.LabelFrame(main_frame, text="角色配置", padding="10")
        config_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), padx=(0, 10))

        # 选择模式
        ttk.Label(config_frame, text="配置模式:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.mode_var = tk.StringVar(value="existing")
        ttk.Radiobutton(config_frame, text="使用现有角色", variable=self.mode_var,
                       value="existing", command=self.toggle_mode).grid(row=0, column=1, sticky=tk.W)
        ttk.Radiobutton(config_frame, text="自定义新角色", variable=self.mode_var,
                       value="custom", command=self.toggle_mode).grid(row=0, column=2, sticky=tk.W)

        # 现有角色选择
        ttk.Label(config_frame, text="选择角色:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.character_var = tk.StringVar()
        self.character_combo = ttk.Combobox(config_frame, textvariable=self.character_var,
                                           values=list(self.characters.keys()), width=20)
        self.character_combo.grid(row=1, column=1, columnspan=2, sticky=tk.W, pady=5)
        if self.characters:
            self.character_combo.current(0)
        self.character_combo.bind('<<ComboboxSelected>>', self.on_character_selected)

        # 分隔线
        ttk.Separator(config_frame, orient='horizontal').grid(row=2, column=0, columnspan=3,
                                                              sticky=(tk.W, tk.E), pady=10)

        # 角色属性输入
        row = 3
        ttk.Label(config_frame, text="角色名称:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(config_frame, textvariable=self.name_var, width=20)
        self.name_entry.grid(row=row, column=1, sticky=tk.W, pady=5)

        row += 1
        ttk.Label(config_frame, text="类型:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.type_var = tk.StringVar(value="attack")
        type_frame = ttk.Frame(config_frame)
        type_frame.grid(row=row, column=1, columnspan=2, sticky=tk.W, pady=5)
        ttk.Radiobutton(type_frame, text="攻击型", variable=self.type_var, value="attack").pack(side=tk.LEFT)
        ttk.Radiobutton(type_frame, text="生命型", variable=self.type_var, value="hp").pack(side=tk.LEFT, padx=(10, 0))

        row += 1
        ttk.Label(config_frame, text="基础数值:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.base_value_var = tk.StringVar(value="2000")
        ttk.Entry(config_frame, textvariable=self.base_value_var, width=20).grid(row=row, column=1, sticky=tk.W, pady=5)
        ttk.Label(config_frame, text="(攻击力或生命值)").grid(row=row, column=2, sticky=tk.W)

        row += 1
        ttk.Label(config_frame, text="基础倍率加成:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.base_mult_var = tk.StringVar(value="0.0")
        ttk.Entry(config_frame, textvariable=self.base_mult_var, width=20).grid(row=row, column=1, sticky=tk.W, pady=5)
        ttk.Label(config_frame, text="(例: 0.2 = 20%，与装备%同乘区)").grid(row=row, column=2, sticky=tk.W)

        row += 1
        ttk.Label(config_frame, text="基础暴击率:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.crit_rate_var = tk.StringVar(value="0.05")
        ttk.Entry(config_frame, textvariable=self.crit_rate_var, width=20).grid(row=row, column=1, sticky=tk.W, pady=5)
        ttk.Label(config_frame, text="(例: 0.05 = 5%)").grid(row=row, column=2, sticky=tk.W)

        row += 1
        ttk.Label(config_frame, text="总暴击伤害:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.crit_dmg_var = tk.StringVar(value="1.50")
        ttk.Entry(config_frame, textvariable=self.crit_dmg_var, width=20).grid(row=row, column=1, sticky=tk.W, pady=5)
        ttk.Label(config_frame, text="(例: 1.5 = 150%)").grid(row=row, column=2, sticky=tk.W)

        row += 1
        ttk.Label(config_frame, text="基础伤害加成:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.dmg_bonus_var = tk.StringVar(value="0.0")
        ttk.Entry(config_frame, textvariable=self.dmg_bonus_var, width=20).grid(row=row, column=1, sticky=tk.W, pady=5)
        ttk.Label(config_frame, text="(例: 0.15 = 15%)").grid(row=row, column=2, sticky=tk.W)

        row += 1
        ttk.Label(config_frame, text="技能倍率:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.skill_mult_var = tk.StringVar(value="2.5")
        ttk.Entry(config_frame, textvariable=self.skill_mult_var, width=20).grid(row=row, column=1, sticky=tk.W, pady=5)
        ttk.Label(config_frame, text="(例: 2.5 = 250%)").grid(row=row, column=2, sticky=tk.W)

        # ===== 右侧：词条统计面板 =====
        affix_frame = ttk.LabelFrame(main_frame, text="词条统计", padding="10")
        affix_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N))

        # 创建词条统计表格
        affix_types = [
            ("暴击", "0.093", "crit_rate"),
            ("爆伤", "0.186", "crit_dmg"),
            ("生命/攻击百分比", "0.101", "percent"),
            ("伤害加成", "0.101", "dmg_bonus"),
            ("生命固定值", "510", "flat_hp"),
            ("攻击固定值", "40", "flat_atk")
        ]

        # 表头
        ttk.Label(affix_frame, text="类型", font=("", 9, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Label(affix_frame, text="词条数", font=("", 9, "bold")).grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(affix_frame, text="平均值", font=("", 9, "bold")).grid(row=0, column=2, padx=5, pady=5)

        # 存储词条输入框变量
        self.affix_vars = {}

        # 创建每一行
        for i, (label, default_avg, var_name) in enumerate(affix_types, start=1):
            ttk.Label(affix_frame, text=label).grid(row=i, column=0, sticky=tk.W, padx=5, pady=2)

            # 词条数输入
            count_var = tk.StringVar(value="4")
            ttk.Entry(affix_frame, textvariable=count_var, width=8).grid(row=i, column=1, padx=5, pady=2)

            # 平均值输入
            avg_var = tk.StringVar(value=default_avg)
            ttk.Entry(affix_frame, textvariable=avg_var, width=12).grid(row=i, column=2, padx=5, pady=2)

            # 保存变量
            self.affix_vars[var_name] = {"count": count_var, "avg": avg_var}

        # 按钮区
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="计算最优方案", command=self.calculate,
                  width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="保存为新角色", command=self.save_character,
                  width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="清空结果", command=self.clear_results,
                  width=20).pack(side=tk.LEFT, padx=5)

        # ===== 结果显示区 =====
        result_frame = ttk.LabelFrame(main_frame, text="计算结果", padding="10")
        result_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        main_frame.rowconfigure(2, weight=1)

        self.result_text = scrolledtext.ScrolledText(result_frame, wrap=tk.WORD,
                                                     width=80, height=20, font=("Consolas", 9))
        self.result_text.pack(fill=tk.BOTH, expand=True)

        # 初始化模式
        self.toggle_mode()
        self.on_character_selected(None)

    def toggle_mode(self):
        """切换配置模式"""
        if self.mode_var.get() == "existing":
            # 现有角色模式：禁用输入框，启用下拉框
            self.character_combo['state'] = 'readonly'
            self.name_entry['state'] = 'disabled'
            self.on_character_selected(None)
        else:
            # 自定义模式：启用输入框，禁用下拉框
            self.character_combo['state'] = 'disabled'
            self.name_entry['state'] = 'normal'
            self.name_var.set("自定义角色")

    def on_character_selected(self, event):
        """角色选择事件"""
        if self.mode_var.get() == "existing" and self.character_var.get():
            char_name = self.character_var.get()
            char_data = self.characters.get(char_name, {})

            # 填充表单
            self.name_var.set(char_name)
            self.type_var.set(char_data.get('base_type', 'attack'))
            self.base_value_var.set(str(char_data.get('base_value', 2000)))
            self.base_mult_var.set(str(char_data.get('base_multiplier', 0.0)))
            self.crit_rate_var.set(str(char_data.get('base_crit_rate', 0.05)))
            self.crit_dmg_var.set(str(char_data.get('base_crit_dmg', 1.50)))
            self.dmg_bonus_var.set(str(char_data.get('base_dmg_bonus', 0.0)))
            self.skill_mult_var.set(str(char_data.get('skill_multiplier', 2.5)))

    def get_affix_stats(self):
        """从词条统计获取额外属性"""
        try:
            affix_stats = {}
            for var_name, vars_dict in self.affix_vars.items():
                count = int(vars_dict["count"].get())
                avg = float(vars_dict["avg"].get())
                affix_stats[var_name] = {
                    "count": count,
                    "avg": avg,
                    "total": count * avg
                }
            return affix_stats
        except ValueError as e:
            messagebox.showerror("输入错误", f"词条统计数据格式错误:\n{e}")
            return None

    def get_character(self):
        """从表单获取角色对象"""
        try:
            character = Character(
                name=self.name_var.get(),
                base_type=self.type_var.get(),
                base_value=float(self.base_value_var.get()),
                base_multiplier=float(self.base_mult_var.get()),
                base_crit_rate=float(self.crit_rate_var.get()),
                base_crit_dmg=float(self.crit_dmg_var.get()),
                base_dmg_bonus=float(self.dmg_bonus_var.get()),
                skill_multiplier=float(self.skill_mult_var.get())
            )

            # 获取词条统计并添加到角色属性
            affix_stats = self.get_affix_stats()
            if affix_stats is None:
                return None

            # 将词条属性加到基础属性上
            character.base_crit_rate += affix_stats["crit_rate"]["total"]
            character.base_crit_dmg += affix_stats["crit_dmg"]["total"]
            character.base_dmg_bonus += affix_stats["dmg_bonus"]["total"]

            # 根据角色类型,添加百分比和固定值
            if character.base_type == 'attack':
                character.base_multiplier += affix_stats["percent"]["total"]
                # 固定攻击会在伤害计算时加上
            else:  # hp
                character.base_multiplier += affix_stats["percent"]["total"]
                # 固定生命会在伤害计算时加上

            # 保存词条统计到角色对象,用于后续展示
            character.affix_stats = affix_stats

            return character
        except ValueError as e:
            messagebox.showerror("输入错误", f"请检查输入的数值格式是否正确\n{e}")
            return None

    def calculate(self):
        """执行计算"""
        character = self.get_character()
        if not character:
            return

        # 清空结果
        self.result_text.delete(1.0, tk.END)

        # 显示计算中
        self.result_text.insert(tk.END, f"正在计算 {character.name} 的最优装备方案...\n\n")
        self.root.update()

        try:
            # 计算
            best_result, all_results = find_best_combination(character, verbose=True)

            # 显示所有方案对比
            self.display_all_combinations(character, all_results)

            # 显示最优方案详情
            self.display_result(character, best_result)

        except Exception as e:
            messagebox.showerror("计算错误", f"计算过程中发生错误:\n{e}")

    def display_all_combinations(self, character, all_results):
        """显示所有方案对比"""
        self.result_text.insert(tk.END, "="*70 + "\n")
        self.result_text.insert(tk.END, "所有装备组合方案对比\n")
        self.result_text.insert(tk.END, "="*70 + "\n\n")

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

            # 输出方案摘要
            self.result_text.insert(tk.END, f"方案{i}: {combo_name}\n")
            self.result_text.insert(tk.END, f"  {base_type_name}: {base_dmg:.0f}  |  ")
            self.result_text.insert(tk.END, f"暴击率: {stats.crit_rate*100:.1f}%  |  ")
            self.result_text.insert(tk.END, f"爆伤: {stats.crit_dmg*100:.0f}%  |  ")
            self.result_text.insert(tk.END, f"伤害加成: {stats.dmg_bonus*100:.0f}%\n")
            self.result_text.insert(tk.END, f"  期望暴击倍率: {crit_multiplier:.3f}x\n")
            self.result_text.insert(tk.END, f"  期望伤害: {damage:.2f}\n")

            if i == 1:
                self.result_text.insert(tk.END, "  ★ 最优方案\n")
            else:
                diff = (sorted_results[0]['damage'] - damage) / damage * 100
                self.result_text.insert(tk.END, f"  (比最优方案低 {diff:.2f}%)\n")

            self.result_text.insert(tk.END, "\n")

        self.result_text.insert(tk.END, "="*70 + "\n\n")

    def display_result(self, character, result):
        """显示最优方案详情"""
        self.result_text.insert(tk.END, "="*70 + "\n")
        self.result_text.insert(tk.END, f"角色：{character.name}\n")
        self.result_text.insert(tk.END, f"类型：{'攻击型' if character.base_type == 'attack' else '生命型'}\n")
        self.result_text.insert(tk.END, f"基础数值：{character.base_value}\n")
        self.result_text.insert(tk.END, f"技能倍率：{character.skill_multiplier * 100:.1f}%\n")
        self.result_text.insert(tk.END, "="*70 + "\n\n")

        # 显示词条统计
        if hasattr(character, 'affix_stats'):
            self.result_text.insert(tk.END, "当前词条统计：\n")
            self.result_text.insert(tk.END, f"{'类型':<15} {'词条数':<8} {'平均值':<12} {'总计'}\n")
            self.result_text.insert(tk.END, "-" * 55 + "\n")

            affix_labels = {
                "crit_rate": "暴击",
                "crit_dmg": "爆伤",
                "percent": "生命/攻击百分比" if character.base_type == 'hp' else "生命/攻击百分比",
                "dmg_bonus": "伤害加成",
                "flat_hp": "生命固定值",
                "flat_atk": "攻击固定值"
            }

            for key, label in affix_labels.items():
                if key in character.affix_stats:
                    stats = character.affix_stats[key]
                    count = stats['count']
                    avg = stats['avg']
                    total = stats['total']

                    # 格式化显示
                    if key in ['crit_rate', 'crit_dmg', 'percent', 'dmg_bonus']:
                        avg_str = f"{avg*100:.1f}%"
                        total_str = f"{total*100:.1f}%"
                    else:
                        avg_str = f"{avg:.0f}"
                        total_str = f"{total:.0f}"

                    self.result_text.insert(tk.END, f"{label:<15} {count:<8} {avg_str:<12} {total_str}\n")

            self.result_text.insert(tk.END, "\n")

        self.result_text.insert(tk.END, f"最优装备组合：{result['combination']}\n\n")
        self.result_text.insert(tk.END, "装备详情：\n")
        for i, eq in enumerate(result['equipments'], 1):
            self.result_text.insert(tk.END, f"  {i}. {eq}\n")

        stats = result['stats']
        self.result_text.insert(tk.END, "\n总属性：\n")
        self.result_text.insert(tk.END, f"  暴击率: {stats.crit_rate*100:.2f}%\n")
        self.result_text.insert(tk.END, f"  暴击伤害: {stats.crit_dmg*100:.2f}%\n")
        self.result_text.insert(tk.END, f"  伤害加成: {stats.dmg_bonus*100:.2f}%\n")

        if character.base_type == 'attack':
            final_attack = stats.base_value * (1 + stats.percent_attack) + stats.flat_attack
            self.result_text.insert(tk.END, f"  攻击力: {final_attack:.2f}\n")
            self.result_text.insert(tk.END, f"    (基础{stats.base_value} * {(1+stats.percent_attack)*100:.1f}% + {stats.flat_attack}固定)\n")
        else:
            final_hp = stats.base_value * (1 + stats.percent_hp) + stats.flat_hp
            self.result_text.insert(tk.END, f"  生命值: {final_hp:.2f}\n")
            self.result_text.insert(tk.END, f"    (基础{stats.base_value} * {(1+stats.percent_hp)*100:.1f}% + {stats.flat_hp}固定)\n")

        # 伤害计算详情
        if character.base_type == 'attack':
            base_dmg = stats.base_value * (1 + stats.percent_attack) + stats.flat_attack
        else:
            base_dmg = stats.base_value * (1 + stats.percent_hp) + stats.flat_hp

        crit_multiplier = 1 + (min(stats.crit_rate, 1.0) * stats.crit_dmg)
        dmg_bonus_multiplier = 1 + stats.dmg_bonus

        self.result_text.insert(tk.END, "\n伤害计算详情：\n")
        self.result_text.insert(tk.END, f"  基础数值部分: {base_dmg:.2f}\n")
        self.result_text.insert(tk.END, f"  伤害加成倍率: {dmg_bonus_multiplier:.2f}x\n")
        self.result_text.insert(tk.END, f"  期望暴击倍率: {crit_multiplier:.2f}x\n")
        self.result_text.insert(tk.END, f"  技能倍率: {character.skill_multiplier:.2f}x\n")
        self.result_text.insert(tk.END, f"  期望伤害 = {base_dmg:.2f} × {dmg_bonus_multiplier:.2f} × {crit_multiplier:.2f} × {character.skill_multiplier:.2f}\n")
        self.result_text.insert(tk.END, f"  期望伤害：{result['damage']:.2f}\n")
        self.result_text.insert(tk.END, "="*70 + "\n\n")

        # 计算并显示下一个词条的收益率
        if hasattr(character, 'affix_stats'):
            self.result_text.insert(tk.END, "下一个词条收益率分析：\n")
            self.result_text.insert(tk.END, "-" * 70 + "\n")

            # 准备词条平均值字典
            affix_avg_values = {key: val['avg'] for key, val in character.affix_stats.items()}

            # 计算收益率
            gains = calculate_next_affix_gain(character, stats, affix_avg_values)

            # 按收益率排序
            sorted_gains = sorted(gains.items(), key=lambda x: x[1]['gain_rate'], reverse=True)

            self.result_text.insert(tk.END, f"{'词条类型':<15} {'平均值':<12} {'伤害提升':<15} {'收益率'}\n")
            self.result_text.insert(tk.END, "-" * 70 + "\n")

            for label, gain_info in sorted_gains:
                avg_val = gain_info['avg_value']
                dmg_inc = gain_info['damage_increase']
                gain_rate = gain_info['gain_rate']

                # 格式化平均值显示
                if label in ['暴击', '爆伤', '伤害加成', '攻击百分比', '生命百分比']:
                    avg_str = f"{avg_val*100:.1f}%"
                else:
                    avg_str = f"{avg_val:.0f}"

                self.result_text.insert(tk.END, f"{label:<15} {avg_str:<12} {dmg_inc:<15.2f} {gain_rate:>6.2f}%\n")

            self.result_text.insert(tk.END, "\n")

            # 显示最优词条建议
            if sorted_gains:
                best_affix = sorted_gains[0]
                self.result_text.insert(tk.END, f"建议优先堆叠: {best_affix[0]} (收益率: {best_affix[1]['gain_rate']:.2f}%)\n")
                self.result_text.insert(tk.END, "="*70 + "\n\n")

        # 滚动到顶部
        self.result_text.see(1.0)

    def save_character(self):
        """保存角色到配置文件"""
        character = self.get_character()
        if not character:
            return

        if not character.name or character.name == "自定义角色":
            messagebox.showwarning("保存失败", "请输入有效的角色名称")
            return

        # 检查是否已存在
        if character.name in self.characters:
            if not messagebox.askyesno("确认覆盖", f"角色 {character.name} 已存在，是否覆盖？"):
                return

        # 保存到配置文件
        try:
            self.characters[character.name] = {
                'base_type': character.base_type,
                'base_value': character.base_value,
                'base_multiplier': character.base_multiplier,
                'base_crit_rate': character.base_crit_rate,
                'base_crit_dmg': character.base_crit_dmg,
                'base_dmg_bonus': character.base_dmg_bonus,
                'skill_multiplier': character.skill_multiplier
            }

            with open('characters.yml', 'w', encoding='utf-8') as f:
                yaml.dump({'characters': self.characters}, f, allow_unicode=True, sort_keys=False)

            # 更新下拉框
            self.character_combo['values'] = list(self.characters.keys())

            messagebox.showinfo("保存成功", f"角色 {character.name} 已保存到配置文件")

        except Exception as e:
            messagebox.showerror("保存失败", f"保存角色时发生错误:\n{e}")

    def clear_results(self):
        """清空结果"""
        self.result_text.delete(1.0, tk.END)


def main():
    """启动GUI"""
    root = tk.Tk()
    app = DamageCalculatorUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
