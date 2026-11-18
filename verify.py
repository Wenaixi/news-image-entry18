"""独立验证 main.py 的输出是否满足比赛要求。

检查项：
1. 连续两次运行 main.py，两次输出逐字节相同；
2. 输出是合法 PNG（校验文件头魔数）；
3. 尺寸为 1024x1024；
4. 文件大小不超过 1 MiB。

全部通过打印 PASS，否则打印 FAIL 并以非零码退出。
"""

import hashlib
import os
import shutil
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MAIN = ROOT / "main.py"
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
MAX_BYTES = 1048576
EXPECTED_SIZE = (1024, 1024)


def run_once(output_dir: Path) -> Path:
    """在指定输出目录运行一次 main.py，返回产出文件路径。"""
    env = dict(os.environ)
    env["MAKEFUN_OUTPUT_DIR"] = str(output_dir)
    subprocess.run(
        [sys.executable, str(MAIN)],
        cwd=str(ROOT),
        env=env,
        check=True,
    )
    produced = output_dir / "entry.png"
    if not produced.is_file():
        raise AssertionError(f"未生成 entry.png：{produced}")
    return produced


def check_png(path: Path) -> None:
    """校验 PNG 魔数、尺寸与文件大小。"""
    data = path.read_bytes()
    if data[:8] != PNG_MAGIC:
        raise AssertionError("PNG 魔数不合法")
    width, height = struct.unpack(">II", data[16:24])
    if (width, height) != EXPECTED_SIZE:
        raise AssertionError(f"尺寸不符：{width}x{height}")
    if len(data) > MAX_BYTES:
        raise AssertionError(f"文件过大：{len(data)} 字节")


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 16), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    # 临时目录放在仓库内，并用普通 mkdir 创建：系统临时目录不可写，
    # 而 0o700 的私有目录在本环境下会让子进程无法在其下建目录。
    workspace = ROOT / f"tmp-verify-{os.urandom(4).hex()}"
    os.mkdir(workspace)
    try:
        first_dir = workspace / "first" / "out"
        second_dir = workspace / "second" / "out"
        a = run_once(first_dir)
        b = run_once(second_dir)

        first_bytes = a.read_bytes()
        second_bytes = b.read_bytes()
        check_png(a)
        check_png(b)

        if first_bytes != second_bytes:
            print("FAIL: 两次输出不一致")
            return 1

        digest = sha256_of(a)
    finally:
        shutil.rmtree(workspace, ignore_errors=True)

    print(f"bytes={len(first_bytes)} size=1024x1024")
    print(f"sha256={digest}")
    print("PASS")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (AssertionError, subprocess.CalledProcessError) as error:
        print(f"FAIL: {error}")
        sys.exit(1)
