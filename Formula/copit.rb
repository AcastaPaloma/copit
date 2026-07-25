class Copit < Formula
  include Language::Python::Virtualenv

  desc "Capture and automatically name macOS screenshots"
  homepage "https://github.com/AcastaPaloma/copit"
  url "https://github.com/AcastaPaloma/copit/archive/refs/tags/v0.1.0.tar.gz"
  sha256 "b9fbc1744de4c2bceb71a2c16c43763c6ce313cf8d49bfe1e9eec925b4e02c08"
  head "https://github.com/AcastaPaloma/copit.git", branch: "main"
  license "MIT"

  depends_on "rust" => :build
  depends_on "libyaml"
  depends_on :macos
  depends_on "python@3.14"
  depends_on "pytorch"
  depends_on "torchvision"

  pypi_packages package_name: "", extra_packages: %w[
    pynput
    pyobjc-framework-Cocoa
    pyobjc-framework-Quartz
    transformers
  ], exclude_packages: %w[numpy pillow torch torchvision]

  resource "annotated-doc" do
    url "https://files.pythonhosted.org/packages/57/ba/046ceea27344560984e26a590f90bc7f4a75b06701f653222458922b558c/annotated_doc-0.0.4.tar.gz"
    sha256 "fbcda96e87e9c92ad167c2e53839e57503ecfda18804ea28102353485033faa4"
  end

  resource "anyio" do
    url "https://files.pythonhosted.org/packages/61/cc/a381afa6efea9f496eff839d4a6a1aed3bfafc7b3ab4b0d1b243a12573dd/anyio-4.14.2.tar.gz"
    sha256 "cfa139f3ed1a23ee8f88a145ddb5ac7605b8bbfd8592baacd7ce3d8bb4313c7f"
  end

  resource "certifi" do
    url "https://files.pythonhosted.org/packages/a3/c2/24167ea9858356b47a87a50d39908bfdb72ceeefe0041586e704e5376b3a/certifi-2026.7.22.tar.gz"
    sha256 "741e2c3b351ddf169a738da9f2c048608ff7f2c5cc02f1ebc6b118bb090d5d55"
  end

  resource "click" do
    url "https://files.pythonhosted.org/packages/76/d4/81420972a676e8ffea40450d8c8c92943e7218a78fe9b64359836cc9876b/click-8.4.2.tar.gz"
    sha256 "9a6cea6e60b17ebe0a44c5cc636d94f09bd66142c1cd7d8b4cd731c4917a15f6"
  end

  resource "filelock" do
    url "https://files.pythonhosted.org/packages/c0/80/8232b582c4b318b817cf1274ba74976b07b34d35ef439b3eb948f98645a1/filelock-3.32.0.tar.gz"
    sha256 "7be2ad23a14607ccc71808e68fe30848aeace7058ace17852f68e2a68e310402"
  end

  resource "fsspec" do
    url "https://files.pythonhosted.org/packages/10/a1/ae4e3e5003468d6391d2c77b6fa1cd73bd5d13511d81c642d7b28ac90ed4/fsspec-2026.6.0.tar.gz"
    sha256 "f5bac145310fe30e16e1471bd6840b2d990d609e872251d7e674241822abf01a"
  end

  resource "h11" do
    url "https://files.pythonhosted.org/packages/01/ee/02a2c011bdab74c6fb3c75474d40b3052059d95df7e73351460c8588d963/h11-0.16.0.tar.gz"
    sha256 "4e35b956cf45792e4caa5885e69fba00bdbc6ffafbfa020300e549b208ee5ff1"
  end

  resource "hf-xet" do
    url "https://files.pythonhosted.org/packages/63/39/67be8d71f900d9a55761b6022821d6679fb56c64f1b6063d5af2c2606727/hf_xet-1.5.2.tar.gz"
    sha256 "73044bd31bae33c984af832d19c752a0dffb67518fee9ddbd91d616e1101cf47"
  end

  resource "httpcore" do
    url "https://files.pythonhosted.org/packages/06/94/82699a10bca87a5556c9c59b5963f2d039dbd239f25bc2a63907a05a14cb/httpcore-1.0.9.tar.gz"
    sha256 "6e34463af53fd2ab5d807f399a9b45ea31c3dfa2276f15a2c3f00afff6e176e8"
  end

  resource "httpx" do
    url "https://files.pythonhosted.org/packages/b1/df/48c586a5fe32a0f01324ee087459e112ebb7224f646c0b5023f5e79e9956/httpx-0.28.1.tar.gz"
    sha256 "75e98c5f16b0f35b567856f597f06ff2270a374470a5c2392242528e3e3e42fc"
  end

  resource "huggingface-hub" do
    url "https://files.pythonhosted.org/packages/df/9b/d3bb4e7d792835daf34dd7091bbc7d7b4e0437d9388f1ea7239cce49f478/huggingface_hub-1.24.0.tar.gz"
    sha256 "18431ff4daae0749aa9ba102fc952e314c98e1d30ebdec5319d85ca0a83e1ae5"
  end

  resource "idna" do
    url "https://files.pythonhosted.org/packages/cd/63/9496c57188a2ee585e0f1db071d75089a11e98aa86eb99d9d7618fc1edce/idna-3.18.tar.gz"
    sha256 "ffb385a7e039654cef1ab9ef32c6fafe283c0c0467bba1d9029738ce4a14a848"
  end

  resource "markdown-it-py" do
    url "https://files.pythonhosted.org/packages/06/ff/7841249c247aa650a76b9ee4bbaeae59370dc8bfd2f6c01f3630c35eb134/markdown_it_py-4.2.0.tar.gz"
    sha256 "04a21681d6fbb623de53f6f364d352309d4094dd4194040a10fd51833e418d49"
  end

  resource "mdurl" do
    url "https://files.pythonhosted.org/packages/d6/54/cfe61301667036ec958cb99bd3efefba235e65cdeb9c84d24a8293ba1d90/mdurl-0.1.2.tar.gz"
    sha256 "bb413d29f5eea38f31dd4754dd7377d4465116fb207585f97bf925588687c1ba"
  end

  resource "packaging" do
    url "https://files.pythonhosted.org/packages/d7/f1/e7a6dd94a8d4a5626c03e4e99c87f241ba9e350cd9e6d75123f992427270/packaging-26.2.tar.gz"
    sha256 "ff452ff5a3e828ce110190feff1178bb1f2ea2281fa2075aadb987c2fb221661"
  end

  resource "pygments" do
    url "https://files.pythonhosted.org/packages/c3/b2/bc9c9196916376152d655522fdcebac55e66de6603a76a02bca1b6414f6c/pygments-2.20.0.tar.gz"
    sha256 "6757cd03768053ff99f3039c1a36d6c0aa0b263438fcab17520b30a303a82b5f"
  end

  resource "pynput" do
    url "https://files.pythonhosted.org/packages/86/c6/e2d415610cfbc78308bee44218a46124aaa3301b1df08814df819b2254a1/pynput-1.8.2.tar.gz"
    sha256 "f493c87157cd3861b4468f7f896857051762f44ed26f1b641e7cc5840a457087"
  end

  resource "pyobjc-core" do
    url "https://files.pythonhosted.org/packages/b4/b1/729f7458a63758bd21716648a8abcd9a0c8f2d2e9897763c8a1a1c7fd31b/pyobjc_core-12.2.1.tar.gz"
    sha256 "7a7b9b018402342cf32bf1956366896350fbe5c0478cb3ef59778f77abed7f07"
  end

  resource "pyobjc-framework-applicationservices" do
    url "https://files.pythonhosted.org/packages/5e/4d/0ebdd8144aba94b8fe9828ccee5616a4bf53d1f8bc51cff55f3cce86d695/pyobjc_framework_applicationservices-12.2.1.tar.gz"
    sha256 "048ea663c9ac75c44a15dc7d5b8d78cbb4c97bf1c76e83835e8d5498e184001f"
  end

  resource "pyobjc-framework-cocoa" do
    url "https://files.pythonhosted.org/packages/51/34/fbe38a204643aa4e1b91391cdce07a34da565a69171ebcad08de7438a556/pyobjc_framework_cocoa-12.2.1.tar.gz"
    sha256 "b94b37fe5730e5ae1fb0052912cd174e6ec329b0bfba4a012ae5db1014b5864b"
  end

  resource "pyobjc-framework-coretext" do
    url "https://files.pythonhosted.org/packages/5a/9c/4c7f452059dc1d3845b8e627b9113c247a997b9b07518e848c2ab7ff3149/pyobjc_framework_coretext-12.2.1.tar.gz"
    sha256 "af740e784d7c592c34025ec7165f4f6c1a69b5a2d9075f06e41e4f77c212aed2"
  end

  resource "pyobjc-framework-quartz" do
    url "https://files.pythonhosted.org/packages/3b/f6/2a8b84dbf1fe7c04dd96ea73d991678d4e09a909f51971ecc51629bb2ab4/pyobjc_framework_quartz-12.2.1.tar.gz"
    sha256 "b3b8b6f71e66147f8ff9e6213864cc8527e3a0b1ee90835b93ce221f4802d9b0"
  end

  resource "pyyaml" do
    url "https://files.pythonhosted.org/packages/05/8e/961c0007c59b8dd7729d542c61a4d537767a59645b82a0b521206e1e25c2/pyyaml-6.0.3.tar.gz"
    sha256 "d76623373421df22fb4cf8817020cbb7ef15c725b9d5e45f17e189bfc384190f"
  end

  resource "regex" do
    url "https://files.pythonhosted.org/packages/20/98/04b13f1ddfb63158025291c02e03eb42fbb7acb51d091d541050eb4e35e8/regex-2026.7.19.tar.gz"
    sha256 "7e77b324909c1617cbb4c668677e2c6ae13f44d7c1de0d4f15f2e3c10f3315b5"
  end

  resource "rich" do
    url "https://files.pythonhosted.org/packages/c0/8f/0722ca900cc807c13a6a0c696dacf35430f72e0ec571c4275d2371fca3e9/rich-15.0.0.tar.gz"
    sha256 "edd07a4824c6b40189fb7ac9bc4c52536e9780fbbfbddf6f1e2502c31b068c36"
  end

  resource "safetensors" do
    url "https://files.pythonhosted.org/packages/45/06/f955dbbb1859e3bd23c8ac6141af5106e7ad5fedec4a3a6e3d60f94b7001/safetensors-0.8.0.tar.gz"
    sha256 "fabaf3e0f18a6618d9b36560682562157f77c2b71fcffc7b432be2baed9d753d"
  end

  resource "shellingham" do
    url "https://files.pythonhosted.org/packages/58/15/8b3609fd3830ef7b27b655beb4b4e9c62313a4e8da8c676e142cc210d58e/shellingham-1.5.4.tar.gz"
    sha256 "8dbca0739d487e5bd35ab3ca4b36e11c4078f3a234bfce294b0a0291363404de"
  end

  resource "six" do
    url "https://files.pythonhosted.org/packages/94/e7/b2c673351809dca68a0e064b6af791aa332cf192da575fd474ed7d6f16a2/six-1.17.0.tar.gz"
    sha256 "ff70335d468e7eb6ec65b95b99d3a2836546063f63acc5171de367e834932a81"
  end

  resource "tokenizers" do
    url "https://files.pythonhosted.org/packages/73/6f/f80cfef4a312e1fb34baf7d85c72d4411afde10978d4657f8cdd811d3ccc/tokenizers-0.22.2.tar.gz"
    sha256 "473b83b915e547aa366d1eee11806deaf419e17be16310ac0a14077f1e28f917"
  end

  resource "tqdm" do
    url "https://files.pythonhosted.org/packages/8c/69/40407dfc835517f058b603dbf37a6df094d8582b015a51eddc988febbcb7/tqdm-4.69.0.tar.gz"
    sha256 "700c5e85dcd5f009dd6222588a29180a193a748247a5d855b4d67db93d79a53b"
  end

  resource "transformers" do
    url "https://files.pythonhosted.org/packages/5a/fb/2a2ba88f325e68a921d8b69ff63b477830b2e73ade9a3c8c8cab2f06d741/transformers-5.14.1.tar.gz"
    sha256 "60d196c27781eacf8637e2b533f517582907ad6f9ae142046d6b69431a5b2173"
  end

  resource "typer" do
    url "https://files.pythonhosted.org/packages/37/78/fda3361b56efc27944f24225f6ecd13d96d6fcfe37bd0eb34e2f4c63f9fc/typer-0.27.0.tar.gz"
    sha256 "629bd12ea5d13a17148125d9a264f949eb171fb3f120f9b04d85873cab054fa5"
  end

  resource "typing-extensions" do
    url "https://files.pythonhosted.org/packages/f6/cc/6253133b5bb138fc3306cebfbda2c520f545d36b5be2c7255cc528bb45d6/typing_extensions-4.16.0.tar.gz"
    sha256 "dc983d19a509c94dba722ee6abd33940f7c05a89e243c47e907eb4db6f1a43e5"
  end

  def install
    # tokenizers and hf-xet build PyO3 extensions through maturin.
    ENV.append_to_rustflags "-C link-arg=-Wl,-undefined,dynamic_lookup"

    venv = virtualenv_install_with_resources(without: "hf-xet")

    site_packages = Language::Python.site_packages(venv.root/"bin/python3")
    pth_contents = %w[pytorch torchvision].map do |dependency|
      "import site; site.addsitedir('#{formula_opt_libexec(dependency)/site_packages}')\n"
    end
    (venv.site_packages/"homebrew-vision.pth").write pth_contents.join

    resource("hf-xet").stage do
      # Avoid building bundled aws-lc indirectly within Homebrew's superenv.
      inreplace "xet_client/Cargo.toml", 'default = ["rustls-tls"]', 'default = ["native-tls"]'

      if ENV.effective_arch == :armv8
        inreplace "xet_data/Cargo.toml",
                  'sha2 = { workspace = true, features = ["asm"] }',
                  "sha2 = { workspace = true }"
      end
      venv.pip_install Pathname.pwd
    end
  end

  def caveats
    <<~EOS
      On first launch, grant the calling terminal Accessibility/Input Monitoring
      and Screen Recording permissions in System Settings > Privacy & Security.

      Copit downloads HuggingFaceTB/SmolVLM-256M-Instruct on first use.
    EOS
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/copit --version")
  end
end
