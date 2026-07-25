# Copit

Copit is a macOS screenshot tool that lets you select a region, identifies the
visible applications, generates a short image description, and renames the
screenshot automatically.

## Usage

Run Copit in a terminal:

```sh
copit
```

Press <kbd>Command</kbd>+<kbd>`</kbd> to open the selector. Press
<kbd>Escape</kbd> to cancel before or during a drag.

The first run downloads `HuggingFaceTB/SmolVLM-256M-Instruct` into the standard
Hugging Face cache. Keep the terminal open while Copit is running.

## macOS permissions

The terminal application launching Copit needs:

- Accessibility or Input Monitoring permission for the global hotkey.
- Screen Recording permission for screenshots.

Configure these under **System Settings → Privacy & Security**.

## Python development install

```sh
python3 -m venv .venv
./.venv/bin/python -m pip install -e .
./.venv/bin/copit --version
```

## Homebrew

The repository includes a tap-ready formula and a release checklist in
[`Formula/README.md`](Formula/README.md).
