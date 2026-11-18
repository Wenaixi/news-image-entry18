# 项目记忆库

## 目标

为 make.fun 比赛 `news-image-20261118` 交付一个可复现的仓库：程序把 `entry.png`（2026-11-18 世界新闻头版图）写入输出目录，供看图 AI 评委成对比较。

## 交付约束

- Python 3.13，仅标准库，禁止网络访问。
- 两次运行输出必须逐字节相同。
- 输出 PNG/JPEG，不超过 1 MiB，最长边不超过 1024。
- 仓库需含 MIT 许可证、README、`.makefun/owner.json`。

## 结构

| 文件 | 职责 |
| --- | --- |
| `entry.png` | 参赛图片，1024x1024，113785 字节 |
| `main.py` | 把仓库内 `entry.png` 复制到 `MAKEFUN_OUTPUT_DIR`（默认 `/output`） |
| `verify.py` | 连跑两次、逐字节比对并校验 PNG 头与尺寸，打印 PASS/FAIL 与 sha256 |

## 关键决策

- `main.py` 只做字节级复制，不重新编码图片，确定性天然由源文件保证。
- 复制前若目标已存在则先删除，避免残留旧文件。
- 输出文件的 sha256 打印到 stderr，不污染 stdout。
- `verify.py` 的临时目录建在仓库内，用普通 `mkdir` 而非 `tempfile.mkdtemp`。
- `README.md` 必须与比赛模板逐字节一致，不得改动 badge 链接。

## 本机环境注意

- 本机 Python 为 3.12.8；代码只使用两版本通用的标准库写法。
- 系统临时目录不可写；`0o700` 私有目录会让子进程无法在其下建目录。
- PowerShell 管道会重编码二进制输出，核对 blob 须用 `git cat-file -s` / `git ls-tree`。

## 验证

```sh
python verify.py
```

期望输出 `PASS` 与 `sha256=ae41aad87830660a6ea0ee5e275bb8ff2b0401016f3660a29111cbf5e59bc16f`。
