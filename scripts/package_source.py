"""Build a source-only archive; no model, audio, environment, Git or cache data."""
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
FILES = {"README.md", "LICENSE", "SECURITY.md", "CHANGELOG.md", "cog.yaml",
         "requirements.txt", "predict.py", ".gitignore", ".dockerignore", ".gitattributes"}
FOLDERS = {"src", "scripts", "tests", "docs", "examples", ".github"}
SUFFIXES = {".py", ".md", ".json", ".yml", ".yaml", ".txt"}


def source_files(root=ROOT):
    for name in sorted(FILES):
        yield root / name
    yield root / "rvc_models" / "README.md"
    for folder in sorted(FOLDERS):
        for path in sorted((root / folder).rglob("*")):
            relative = path.relative_to(root)
            if path.is_file() and path.suffix in SUFFIXES and not any(
                part.startswith(".") or part in ("__pycache__", "audio")
                for part in relative.parts[1:]
            ):
                yield path


def main():
    output = ROOT / "dist" / "rvc-v3-source.zip"
    output.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as bundle:
        for path in source_files():
            bundle.write(path, "rvc-v3/" + path.relative_to(ROOT).as_posix())
    print(f"Created {output} ({output.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
