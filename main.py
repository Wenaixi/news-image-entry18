"""把仓库根目录的 entry.png 复制到输出目录的 entry.png。

输出目录由环境变量 MAKEFUN_OUTPUT_DIR 指定，未设置时使用 /output。
程序不访问网络，输出完全由仓库内的 entry.png 决定，因此两次运行逐字节相同。
"""

import hashlib
import os
import shutil
import sys
from pathlib import Path

SOURCE = Path(__file__).resolve().parent / "entry.png"
DEFAULT_OUTPUT_DIR = "/output"


def resolve_output_dir() -> Path:
    """返回输出目录，优先使用 MAKEFUN_OUTPUT_DIR。"""
    return Path(os.environ.get("MAKEFUN_OUTPUT_DIR") or DEFAULT_OUTPUT_DIR)


def sha256_of(path: Path) -> str:
    """计算文件的 sha256 摘要。"""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 16), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    output_dir = resolve_output_dir()
    output_dir.mkdir(parents=True, exist_ok=True)
    destination = output_dir / "entry.png"

    # 目标已存在时先删除，保证每次写入都是一份全新的文件。
    if destination.exists():
        destination.unlink()

    shutil.copyfile(SOURCE, destination)
    print(f"sha256={sha256_of(destination)}", file=sys.stderr)


if __name__ == "__main__":
    main()
