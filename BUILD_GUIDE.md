# 打包说明文档

## 如何打包成 EXE

### 方法1：使用批处理脚本（最简单）

**Windows 系统：**
```bash
# 双击运行
build.bat
```

这会自动打包图形界面版本，生成 `dist\伤害计算器.exe`

### 方法2：使用 Python 打包脚本

```bash
python build.py
```

会提示选择打包选项：
1. 仅打包图形界面版本（推荐）
2. 仅打包命令行版本
3. 同时打包两个版本

### 方法3：使用 PyInstaller 规格文件

```bash
pyinstaller damage_calculator.spec
```

这使用预配置的规格文件进行打包。

### 方法4：直接使用 PyInstaller 命令

**打包图形界面版本：**
```bash
pyinstaller --name=伤害计算器 --onefile --windowed --clean --noconfirm --add-data=characters.yml;. ui.py
```

**打包命令行版本：**
```bash
pyinstaller --name=伤害计算器-命令行 --onefile --console --clean --noconfirm --add-data=characters.yml;. main.py
```

## PyInstaller 参数说明

- `--name=名称` - 指定生成的 EXE 文件名
- `--onefile` - 打包成单个 EXE 文件
- `--windowed` - GUI 程序，不显示控制台窗口
- `--console` - 命令行程序，显示控制台窗口
- `--clean` - 清理临时文件
- `--noconfirm` - 覆盖输出目录时不询问
- `--add-data=源;目标` - 包含数据文件（Windows 用 `;`，Linux/Mac 用 `:`）
- `--icon=图标.ico` - 指定程序图标

## 生成的文件

打包成功后，在 `dist/` 目录下会生成：
- `伤害计算器.exe` - 主程序
- `characters.yml` - 配置文件（自动复制）

## 分发说明

### 最小分发包

将以下文件打包给用户：
```
伤害计算器/
  ├── 伤害计算器.exe
  ├── characters.yml
  └── 使用说明.txt
```

### 完整分发包

```
伤害计算器/
  ├── 伤害计算器.exe
  ├── characters.yml
  ├── 使用说明.txt
  └── README.md
```

## 自定义图标

如果要添加自定义图标：

1. 准备一个 `.ico` 格式的图标文件（推荐 256x256 像素）
2. 将图标文件命名为 `icon.ico` 放在项目根目录
3. 修改打包命令，添加 `--icon=icon.ico` 参数

**在线图标转换工具：**
- https://www.icoconverter.com/
- https://convertio.co/zh/png-ico/

## 注意事项

### 1. 配置文件路径问题

程序运行时需要 `characters.yml` 配置文件。有两种处理方式：

**方式A：将配置文件打包进 EXE**
- 优点：单文件分发，简单
- 缺点：用户无法编辑配置文件
- 已采用：使用 `--add-data` 参数

**方式B：配置文件外置**
- 优点：用户可以编辑配置
- 缺点：需要分发多个文件
- 实现：首次运行时在当前目录查找或创建配置文件

### 2. 文件大小优化

生成的 EXE 可能较大（20-50MB），这是正常的，因为包含了 Python 解释器和所有依赖库。

优化方法：
- 使用 `--exclude-module` 排除不需要的模块
- 使用 UPX 压缩（PyInstaller 默认启用）
- 使用目录模式而非单文件模式（`--onedir`）

### 3. 杀毒软件误报

PyInstaller 打包的程序可能被某些杀毒软件误报为病毒。

解决方法：
- 将程序添加到杀毒软件白名单
- 使用代码签名证书签名程序
- 向杀毒软件厂商报告误报

### 4. 运行环境

生成的 EXE 文件：
- 仅适用于 Windows 系统
- 不需要安装 Python
- 不需要安装其他依赖
- 可以在任何 Windows 10/11 系统上运行

## 测试流程

打包完成后，建议进行以下测试：

1. **基本功能测试**
   - 双击运行 EXE
   - 检查界面是否正常显示
   - 尝试选择现有角色并计算
   - 尝试自定义角色并计算

2. **配置文件测试**
   - 检查是否能正确读取 `characters.yml`
   - 尝试保存新角色
   - 检查配置文件是否正确更新

3. **不同环境测试**
   - 在干净的 Windows 系统上测试（虚拟机）
   - 在没有安装 Python 的系统上测试
   - 测试不同 Windows 版本（10/11）

4. **错误处理测试**
   - 删除配置文件后运行
   - 输入错误数据
   - 检查错误提示是否友好

## 故障排除

### 问题：打包失败

**检查项：**
- 是否安装了 PyInstaller：`pip list | findstr pyinstaller`
- 是否安装了所有依赖：`pip install -r requirements.txt`
- 检查文件路径是否正确
- 查看详细错误信息

### 问题：运行时找不到配置文件

**解决方案：**
- 确保 `characters.yml` 与 EXE 在同一目录
- 或修改代码使用绝对路径

### 问题：程序闪退

**调试方法：**
```bash
# 使用 console 模式重新打包，查看错误信息
pyinstaller --name=伤害计算器-调试 --onefile --console ui.py
```

运行 `dist\伤害计算器-调试.exe`，控制台会显示错误信息。

## 持续更新

更新程序后重新打包：

1. 修改源代码
2. 清理旧的构建文件（可选）：
   ```bash
   rmdir /s /q build dist
   del *.spec
   ```
3. 重新运行打包脚本
4. 测试新版本
5. 分发给用户

## 版本管理建议

在代码中添加版本号：

```python
# ui.py
VERSION = "1.0.0"

# 在界面标题中显示
self.root.title(f"伤害计算器 v{VERSION}")
```

这样用户可以看到程序版本，方便问题追踪和更新管理。
