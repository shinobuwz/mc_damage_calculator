@echo off
chcp 65001 >nul
echo ============================================================
echo 伤害计算器 - 快速打包脚本
echo ============================================================
echo.

echo 正在打包图形界面版本...
echo.

pyinstaller --name=伤害计算器 ^
    --onefile ^
    --windowed ^
    --clean ^
    --noconfirm ^
    --add-data=characters.yml;. ^
    ui.py

if %errorlevel% equ 0 (
    echo.
    echo ============================================================
    echo 打包成功！
    echo ============================================================
    echo.
    echo 生成的文件位置: dist\伤害计算器.exe
    echo.
    echo 正在复制配置文件...
    copy characters.yml dist\characters.yml >nul
    echo.
    echo 完成！可以在 dist 目录找到可执行文件。
    echo.
) else (
    echo.
    echo ============================================================
    echo 打包失败！请检查错误信息。
    echo ============================================================
    echo.
)

pause
