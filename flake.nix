{

inputs = {
  nixpkgs = {
    type = "github";
    owner = "NixOS";
    repo = "nixpkgs";
    ref = "nixos-unstable";
  };
};

outputs = { self, nixpkgs }: let
  pkgs = nixpkgs.legacyPackages.x86_64-linux;
  jishaku = pkgs.callPackage ./jishaku.nix {};
  discord-ext-menus = pkgs.callPackage ./discord-ext-menus.nix {};
  aiopywttr = pkgs.callPackage ./aiopywttr.nix {};
in {
  packages.x86_64-linux.default = pkgs.python311Packages.buildPythonPackage {
      pname = "esobot";
      version = "0.1.0";
      format = "setuptools";
      disabled = pkgs.python311Packages.pythonOlder "3.11";

      src = self;

      propagatedBuildInputs = with pkgs.python311Packages; [
        discordpy
        discord-ext-menus
        unidecode
        pykakasi
        openai
        jishaku
        pillow
        dateparser
        pyahocorasick
        aiopywttr
      ];

      preBuild = ''
cat > setup.py << EOF
from setuptools import setup
setup(
  name='esobot',
  version='0.1.0',
  packages=['cogs', 'constants'],
  py_modules=['utils'],
  scripts=['main.py']
)
EOF
'';

      doCheck = false;
    };
};

}
