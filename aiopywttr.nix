{ python311Packages }: let

  pywttr-models = python311Packages.buildPythonPackage rec {
    pname = "pywttr-models";
    version = "1.1.0";
    format = "pyproject";

    src = python311Packages.fetchPypi {
      pname = "pywttr_models";
      inherit version;
      hash = "sha256-4+u9I2LhO0uHTJGvXadZWukbjDLFFXxfmSNaCAFN0Mk=";
    };

    nativeBuildInputs = [ python311Packages.poetry-core ];

    propagatedBuildInputs = [ python311Packages.pydantic ];
  };

in

  python311Packages.buildPythonPackage rec {
    pname = "aiopywttr";
    version = "2.2.0";
    format = "pyproject";

    src = python311Packages.fetchPypi {
      inherit pname version;
      hash = "sha256-YtDha6HP5NginwwJenNO+pXJC2xtNBXWApl1rpA1aR0=";
    };

    nativeBuildInputs = [ python311Packages.poetry-core ];

    propagatedBuildInputs = with python311Packages; [
      pywttr-models
      aiohttp
    ];
  }
