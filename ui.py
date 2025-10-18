"""
伤害计算器 - 图形界面版本
使用 tkinter 实现简单的 GUI
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import yaml
from main import Character, find_best_combination, calculate_stats, calculate_damage


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
        main_frame.columnconfigure(1, weight=1)

        # ===== 左侧：角色配置区 =====
        config_frame = ttk.LabelFrame(main_frame, text="角色配置", padding="10")
        config_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N), pady=(0, 10))

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
        ttk.Label(config_frame, text="基础暴击率:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.crit_rate_var = tk.StringVar(value="0.05")
        ttk.Entry(config_frame, textvariable=self.crit_rate_var, width=20).grid(row=row, column=1, sticky=tk.W, pady=5)
        ttk.Label(config_frame, text="(例: 0.05 = 5%)").grid(row=row, column=2, sticky=tk.W)

        row += 1
        ttk.Label(config_frame, text="基础暴击伤害:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.crit_dmg_var = tk.StringVar(value="0.50")
        ttk.Entry(config_frame, textvariable=self.crit_dmg_var, width=20).grid(row=row, column=1, sticky=tk.W, pady=5)
        ttk.Label(config_frame, text="(例: 0.50 = 50%)").grid(row=row, column=2, sticky=tk.W)

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
            self.crit_rate_var.set(str(char_data.get('base_crit_rate', 0.05)))
            self.crit_dmg_var.set(str(char_data.get('base_crit_dmg', 0.50)))
            self.dmg_bonus_var.set(str(char_data.get('base_dmg_bonus', 0.0)))
            self.skill_mult_var.set(str(char_data.get('skill_multiplier', 2.5)))

    def get_character(self):
        """从表单获取角色对象"""
        try:
            return Character(
                name=self.name_var.get(),
                base_type=self.type_var.get(),
                base_value=float(self.base_value_var.get()),
                base_crit_rate=float(self.crit_rate_var.get()),
                base_crit_dmg=float(self.crit_dmg_var.get()),
                base_dmg_bonus=float(self.dmg_bonus_var.get()),
                skill_multiplier=float(self.skill_mult_var.get())
            )
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
