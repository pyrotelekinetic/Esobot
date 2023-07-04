{ fetchFromGitHub, python311Packages }:

python311Packages.buildPythonPackage {
  pname = "discord-ext-menus";
  version = "0.1.0";
  format = "setuptools";

  src = fetchFromGitHub {
    owner = "Rapptz";
    repo = "discord-ext-menus";
    rev = "8686b5d1bbc1d3c862292eb436ab630d6e9c9b53";
    hash = "sha256-WsPK+KyBezpKoHZUqOnhRLpMDOpmuIa6JLvqBLFRkXc=";
  };

  propagatedBuildInputs = [ python311Packages.discordpy ];
}
