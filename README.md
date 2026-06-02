# MorningRush-IELTS

> 来一场酣畅淋漓的雅思背诵！

Windows 桌面悬浮窗雅思词汇练习工具。每天 20 个单词，先学后测，上班前快速刷一波。

## Features

- 先学后测：先浏览所有单词卡片，再统一做选择题
- 错题集：自动记录错词，支持点击查看详情和重新练习
- 智能出题：根据掌握程度加权选词，错题优先出现
- 学习统计：跟踪已学/已掌握/错误次数
- 开机自启：可设置 Windows 开机自动启动
- 系统托盘：最小化到托盘，不占任务栏

## Screenshot

```
┌──────────────────────────────┐
│  IELTS 每日单词          — × │
├──────────────────────────────┤
│                              │
│       雅思词汇练习            │
│    每天 20 个单词 · 先学后测   │
│                              │
│   ┌────┐  ┌────┐  ┌────┐    │
│   │ 42 │  │ 15 │  │  8 │    │
│   │已学 │  │掌握 │  │错题 │    │
│   └────┘  └────┘  └────┘    │
│                              │
│      [ 开始今日学习 ]         │
│      [ 错题集 (8 词) ]       │
│                              │
└──────────────────────────────┘
```

## Install

需要 Python 3.10+ 和 [Pillow](https://python-pillow.org/)。

```bash
git clone https://github.com/YOUR_USERNAME/MorningRush-IELTS.git
cd MorningRush-IELTS
pip install pillow
python main.py
```

## Usage

直接运行：
```bash
python main.py
```

带系统托盘（需安装 pystray）：
```bash
pip install pystray
python main.py
```

设置开机自启：将 `start.bat` 的快捷方式放入 Windows 启动目录（`Win+R` → `shell:startup`）。

## Project Structure

```
MorningRush-IELTS/
├── main.py          # Entry point
├── ui.py            # tkinter GUI
├── quiz.py          # Quiz logic & word selection
├── db.py            # SQLite progress tracking
├── tray.py          # System tray (optional)
├── words.json       # IELTS vocabulary (200+ words)
├── start.bat        # Windows startup script
└── .gitignore
```

## Add More Words

编辑 `words.json`，格式如下：

```json
{
  "word": "example",
  "phonetic": "/ɪɡˈzæmpəl/",
  "meaning": "n. 例子；范例",
  "level": 1
}
```

level: 1=基础, 2=中级, 3=高级

## License

MIT
