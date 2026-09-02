from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "Mirai_for_ChatGPT.zip"

EXCLUDED_DIRS = {
    "node_modules",
    ".expo",
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".venv",
    "venv",
    "env",
    "dist",
    "build",
    ".next",
    ".turbo",
    "coverage",
}

EXCLUDED_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".gif",
    ".mp4",
    ".mov",
    ".avi",
    ".zip",
    ".tar",
    ".gz",
    ".pyc",
    ".pyo",
}

EXCLUDED_NAMES = {
    ".env",
    ".env.local",
    ".env.production",
    ".env.development",
}

MAX_FILE_SIZE_MB = 5


def should_exclude(path: Path) -> bool:
    # Папки
    if any(part in EXCLUDED_DIRS for part in path.parts):
        return True

    # Секретные файлы
    if path.name in EXCLUDED_NAMES:
        return True

    # Расширения
    if path.suffix.lower() in EXCLUDED_EXTENSIONS:
        return True

    # Сам архив
    if path.resolve() == OUTPUT.resolve():
        return True

    # Слишком большие файлы
    try:
        if path.is_file() and path.stat().st_size > MAX_FILE_SIZE_MB * 1024 * 1024:
            return True
    except OSError:
        return True

    return False


def main():
    print("Собираю архив...")
    print(f"Проект: {ROOT}")
    print()

    files = []

    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue

        if should_exclude(path):
            continue

        files.append(path)

    with zipfile.ZipFile(
        OUTPUT,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as archive:
        for path in files:
            relative = path.relative_to(ROOT)
            archive.write(path, relative)

    size_mb = OUTPUT.stat().st_size / 1024 / 1024

    print("Готово!")
    print()
    print(f"Файлов добавлено: {len(files)}")
    print(f"Размер архива: {size_mb:.2f} MB")
    print()
    print("Архив:")
    print(OUTPUT)


if __name__ == "__main__":
    main()