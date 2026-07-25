# Homebrew release handoff

The source package and formula are prepared for version `0.1.0`. The remaining
steps require publishing external GitHub state and are intentionally left to the
repository owner.

## 1. Choose and add a license

Add a `LICENSE` file, then add the matching SPDX identifier to both:

- `[project]` in `pyproject.toml`
- `Formula/copit.rb`

## 2. Publish the source repository

```sh
git add .gitignore Formula LICENSE README.md main.py ocr.py pyproject.toml requirements.txt
git commit -m "Package Copit for Homebrew"
git push -u origin main
git tag v0.1.0
git push origin v0.1.0
```

## 3. Replace the release checksum

```sh
curl -L \
  https://github.com/AcastaPaloma/copit/archive/refs/tags/v0.1.0.tar.gz \
  -o /tmp/copit-v0.1.0.tar.gz
shasum -a 256 /tmp/copit-v0.1.0.tar.gz
```

Replace the all-zero `sha256` value in `Formula/copit.rb` with that output.
Then publish the finalized formula:

```sh
git add Formula/copit.rb
git commit -m "Set copit 0.1.0 release checksum"
git push
```

## 4. Refresh Python resources when dependencies change

The version `0.1.0` resource blocks are already generated and checksummed.
For later dependency updates, refresh them with:

```sh
cp Formula/copit.rb "$(brew --repository AcastaPaloma/tap)/Formula/copit.rb"
brew update-python-resources AcastaPaloma/tap/copit \
  --ignore-non-pypi-packages \
  --extra-packages pynput,pyobjc-framework-Cocoa,pyobjc-framework-Quartz,transformers \
  --exclude-packages numpy,pillow,torch,torchvision
cp "$(brew --repository AcastaPaloma/tap)/Formula/copit.rb" Formula/copit.rb
```

Homebrew installs its bottled `pytorch`, `torchvision`, `numpy`, and `pillow`
formulae separately; the generated resource list should not include them.

## 5. Stage the formula in a local tap and validate it

```sh
brew tap-new AcastaPaloma/tap
cp Formula/copit.rb "$(brew --repository AcastaPaloma/tap)/Formula/copit.rb"
brew trust --formula AcastaPaloma/tap/copit
brew style --fix --formula AcastaPaloma/tap/copit
brew audit --strict --new --online AcastaPaloma/tap/copit
HOMEBREW_NO_INSTALL_FROM_API=1 \
  brew install --build-from-source AcastaPaloma/tap/copit
brew test AcastaPaloma/tap/copit
copit --version
```

Then launch `copit`, approve macOS permissions, and test selection, Escape, OCR,
and renaming.

## 6. Publish a tap

```sh
cd "$(brew --repository AcastaPaloma/tap)"
git add Formula/copit.rb
git commit -m "Add copit 0.1.0"
gh repo create AcastaPaloma/homebrew-tap --public --source=. --remote=origin --push
```

Users can then install Copit with:

```sh
brew install AcastaPaloma/tap/copit
```
