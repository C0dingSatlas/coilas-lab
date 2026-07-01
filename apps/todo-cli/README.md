# todo-cli

一个用 Python 编写的命令行待办事项工具，用于练习 CLI 输入解析、业务逻辑分层、
JSON 数据持久化和模块设计。

## 环境要求

- Python 3.9 或更高版本
- 不需要安装第三方依赖

## 安装

首次使用时，在项目目录中执行一次：

```powershell
python -m pip install --user -e .
```

`-e` 表示开发模式安装。修改当前项目源码后，不需要重新安装。

安装完成后，可以离开项目目录，在任意位置运行 `todo`。

如果 PowerShell 提示无法识别 `todo`，先执行：

```powershell
python -c "import sysconfig; print(sysconfig.get_path('scripts', scheme='nt_user'))"
```

将输出的目录加入 Windows 用户 `PATH`，然后重新打开终端。

## 使用方法

```powershell
todo add "学习 Python"
todo list
todo done 1
todo delete 1
```

查看帮助：

```powershell
todo --help
todo add --help
```

## 命令说明

| 命令 | 示例 | 作用 |
| --- | --- | --- |
| `add` | `todo add "学习 Git"` | 添加任务 |
| `list` | `todo list` | 显示所有任务 |
| `done` | `todo done 1` | 将指定任务标记为完成 |
| `delete` | `todo delete 1` | 删除指定任务 |

## 项目结构

```text
todo-cli/
├── main.py       # 解析命令并输出结果
├── todo.py       # 待办事项的业务规则
├── storage.py    # JSON 文件的读取和保存
├── setup.cfg     # 项目信息和 todo 命令入口
├── setup.py      # 安装入口
└── README.md     # 项目说明
```

调用流程：

```text
todo 命令 → main.py → todo.py → storage.py → 用户数据文件
```

## 数据存放位置

代码可以安装在任意位置，但任务数据属于当前用户。在 Windows 上默认保存在：

```text
%LOCALAPPDATA%\todo-cli\data.json
```

测试或调试时，可以通过 `TODO_DATA_FILE` 环境变量指定其他文件。

如果旧版本的项目目录中已有 `data.json`，新版本会先读取旧数据；首次添加、
完成或删除任务后，数据会自动保存到新的用户数据目录。

## 数据格式

```json
[
  {
    "id": 1,
    "task": "学习 Python",
    "done": false
  }
]
```

新任务 ID 使用“现有最大 ID + 1”生成，删除任务后不会立即复用旧 ID。

## 设计边界

- `main.py` 只负责输入、命令调度和输出。
- `todo.py` 只负责添加、完成和删除任务的业务规则。
- `storage.py` 只负责数据持久化，不包含业务规则。

因此，将来把 JSON 换成 SQLite 时，主要修改存储层即可。
