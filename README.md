# Malody → osu!mania Converter

Convert Malody **Key mode** charts (`.mc`) to **osu!mania** (`.osu`, Mode 3), and optionally pack results into `.osz`.

This repository contains a single-file Python script based on the original converter by Jakads, with tweaks for cross-platform behavior (Windows/Linux/macOS) and safer output filenames.

## Features

- Converts Malody Key mode `.mc` → osu!mania `.osu` (Mode 3)
- Reads key count (4K–9K, etc.) from chart metadata
- Supports multiple BPMs and time signature changes
- Supports SV (scroll speed) effects (exported as inherited timing points)
- Supports per-note hitsounds when present
- Packs converted charts into `.osz` mapsets; includes BG/audio if referenced and found

## Requirements

- Python 3.x
- No third-party dependencies

## Usage

```bash
python3 convert.py /path/to/chart.mc [/path/to/pack.mcz] [/path/to/pack.zip]
```

The script will:

1. Convert supported `.mc` charts to `.osu` next to the `.mc` files.
2. Wait for a key press, then compress into `.osz`.

Notes:

- Directories are ignored.
- Unsupported file types are ignored.
- `.mcz` is treated as a zip container and extracted before conversion.

## Output behavior

### `.osu`

For each converted `.mc`, an `.osu` file is written next to it:

- `some_chart.mc` → `some_chart.osu`

### `.osz`

After conversion, press a key to start packing.

#### If you pass `.mc` files

- All valid `.mc` inputs are packed into **one** `.osz` mapset.
- Output directory: the directory of the **first** `.mc` file.
- Output filename: `<Artist> - <Title>.osz`.

#### If you pass `.mcz` / `.zip` files

- Each package becomes **one** `.osz` mapset.
- Output directory: next to the extracted folder (i.e. the original archive’s directory).
- Output filename: `<package_filename>.osz`.
- The extracted folder is removed after packing.

#### Filename sanitization & collision handling

- Output `.osz` filenames are sanitized for illegal characters.
- If the target `.osz` already exists, the script saves as `name (1).osz`, `name (2).osz`, etc.

## Version check

On startup, the script checks for updates from GitHub. If a newer version is available, it will print a notice. This check requires an internet connection and times out after 5 seconds.

## Notes / limitations

- Only **Key mode** charts are supported (`meta.mode == 0`). Other modes are skipped.
- If background/audio files referenced by the chart are missing, packing continues and prints a warning.
- SV conversion uses Malody scroll values; extreme values may not behave as expected in osu!mania.
- osu!mania effectively interprets SV in the range **0.01x to 10x**; values outside this range are clamped by the client.

## Troubleshooting

### Crash logs

If the script crashes, it writes a log file named `CrashLog_YYYYMMDDHHMMSS.log` in the current working directory, including a traceback and the last file being processed.

## Credits

- Original converter: Jakads
- This fork/modification: Eric Zhao

<details>
<summary>中文说明</summary>

## 简介

将 Malody 的 **Key 模式**谱面（`.mc`）转换为 osu!mania 的 `.osu`（Mode 3），并可在转换完成后打包为 `.osz`。

## 用法

```bash
python3 convert.py /path/to/chart.mc [/path/to/pack.mcz] [/path/to/pack.zip]
```

## 输出规则

- `.osu`：与对应 `.mc` 同目录生成同名 `.osu`。
- `.osz`：转换结束后按任意键开始打包。
  - 传入多个 `.mc`：合并打包为一个 `.osz`，输出到**第一个** `.mc` 所在目录，文件名为 `<Artist> - <Title>.osz`。
  - 传入 `.mcz/.zip`：每个包单独生成一个 `.osz`，文件名为包名；打包后会删除解压目录。

## 其他

- 启动时会自动检查 GitHub 上的最新版本（超时 5 秒）。
- 输出文件名会做非法字符清理；若同名 `.osz` 已存在，会自动追加 `(1)`, `(2)` 后缀避免覆盖。
- 程序崩溃会在当前工作目录生成 `CrashLog_YYYYMMDDHHMMSS.log`。

</details>
