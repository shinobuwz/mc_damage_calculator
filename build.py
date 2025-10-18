"""
打包脚本 - 使用 PyInstaller 将程序打包为可执行文件

使用方法：
    python build.py

生成的文件：
    dist/伤害计算器.exe - 独立的可执行文件
    dist/伤害计算器/ - 包含所有依赖的文件夹
"""

import os
import sys
import shutil
import subprocess


def clean_build_files():
    """清理之前的构建文件"""
    print("清理旧的构建文件...")
    dirs_to_remove = ['build', 'dist', '__pycache__']
    files_to_remove = ['*.spec']

    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"  已删除: {dir_name}/")

    import glob
    for pattern in files_to_remove:
        for file in glob.glob(pattern):
            os.remove(file)
            print(f"  已删除: {file}")


def build_ui_exe():
    """打包图形界面版本"""
    print("\n" + "="*60)
    print("开始打包图形界面版本...")
    print("="*60 + "\n")

    # PyInstaller 参数
    cmd = [
        'pyinstaller',
        '--name=伤害计算器',           # 程序名称
        '--onefile',                   # 打包成单个文件
        '--windowed',                  # 无控制台窗口（GUI程序）
        '--clean',                     # 清理临时文件
        '--noconfirm',                 # 覆盖输出目录
        '--add-data=characters.yml;.', # 包含配置文件
        # '--icon=icon.ico',           # 图标（如果有的话）
        'ui.py'
    ]

    # 执行打包
    result = subprocess.run(cmd, shell=True)

    if result.returncode == 0:
        print("\n" + "="*60)
        print("✓ 图形界面版本打包成功！")
        print("="*60)
        print(f"\n可执行文件位置: dist\\伤害计算器.exe")
        return True
    else:
        print("\n" + "="*60)
        print("✗ 打包失败，请检查错误信息")
        print("="*60)
        return False


def build_console_exe():
    """打包命令行版本（可选）"""
    print("\n" + "="*60)
    print("开始打包命令行版本...")
    print("="*60 + "\n")

    # PyInstaller 参数
    cmd = [
        'pyinstaller',
        '--name=伤害计算器-命令行',
        '--onefile',
        '--console',                   # 显示控制台窗口
        '--clean',
        '--noconfirm',
        '--add-data=characters.yml;.',
        'main.py'
    ]

    # 执行打包
    result = subprocess.run(cmd, shell=True)

    if result.returncode == 0:
        print("\n" + "="*60)
        print("✓ 命令行版本打包成功！")
        print("="*60)
        print(f"\n可执行文件位置: dist\\伤害计算器-命令行.exe")
        return True
    else:
        print("\n" + "="*60)
        print("✗ 打包失败，请检查错误信息")
        print("="*60)
        return False


def create_readme():
    """在 dist 目录创建说明文件"""
    readme_content = """伤害计算器 - 使用说明
================================

这是一个游戏角色伤害期望值计算器。

使用方法：
1. 双击运行 "伤害计算器.exe"
2. 在界面中选择现有角色或自定义新角色
3. 点击"计算最优方案"查看结果
4. 可以保存自定义角色到配置文件

配置文件：
- characters.yml：角色配置文件（可手动编辑）

装备组合：
程序会自动计算三种装备组合方案：
- 44111: 2件4类 + 3件1类
- 43311: 1件4类 + 2件3类 + 2件1类
- 43111: 1件4类 + 1件3类 + 3件1类

输出结果：
- 所有方案对比
- 最优方案详细配置
- 完整的伤害计算过程

注意事项：
- 首次运行会在当前目录创建 characters.yml 配置文件
- 保存的角色配置会写入到 characters.yml
- 建议备份配置文件以防丢失

如有问题，请参考完整文档或反馈问题。
"""

    dist_dir = 'dist'
    if os.path.exists(dist_dir):
        readme_path = os.path.join(dist_dir, '使用说明.txt')
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print(f"\n已创建: {readme_path}")

        # 复制配置文件示例
        if os.path.exists('characters.yml'):
            shutil.copy('characters.yml', os.path.join(dist_dir, 'characters.yml'))
            print(f"已复制: characters.yml -> dist/characters.yml")


def main():
    """主函数"""
    print("\n" + "="*60)
    print("伤害计算器 - 打包脚本")
    print("="*60)

    # 检查是否安装了 PyInstaller
    try:
        import PyInstaller
    except ImportError:
        print("\n错误: 未安装 PyInstaller")
        print("请运行: pip install pyinstaller")
        return

    # 询问打包选项
    print("\n请选择打包方式：")
    print("  1. 仅打包图形界面版本（推荐）")
    print("  2. 仅打包命令行版本")
    print("  3. 同时打包两个版本")

    choice = input("\n请输入选项 (1/2/3，默认为1): ").strip() or "1"

    # 清理旧文件
    clean_build_files()

    success = False

    # 执行打包
    if choice == "1":
        success = build_ui_exe()
    elif choice == "2":
        success = build_console_exe()
    elif choice == "3":
        success1 = build_ui_exe()
        success2 = build_console_exe()
        success = success1 and success2
    else:
        print("\n无效的选项，默认打包图形界面版本")
        success = build_ui_exe()

    # 创建说明文件
    if success:
        create_readme()

        print("\n" + "="*60)
        print("打包完成！")
        print("="*60)
        print("\n生成的文件在 dist/ 目录下")
        print("\n可以将 dist/ 目录下的以下文件分发给用户：")
        print("  - 伤害计算器.exe")
        print("  - characters.yml (配置文件)")
        print("  - 使用说明.txt")
        print("\n提示：第一次运行时，如果当前目录没有 characters.yml，")
        print("      程序可能无法加载角色，需要手动复制配置文件。")


if __name__ == '__main__':
    main()
