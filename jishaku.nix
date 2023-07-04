{ python311Packages }: let

  import-expression = python311Packages.buildPythonPackage rec {
    pname = "import_expression";
    version = "1.1.4";
    format = "setuptools";

    src = python311Packages.fetchPypi {
      inherit pname version;
      hash = "sha256-BghqarO/pSixxHjmM9at8rOpkOMUQPZAGw8+oSsGWak=";
    };

    propagatedBuildInputs = [ python311Packages.astunparse ];

    doCheck = false;
  };

in

  python311Packages.buildPythonPackage rec {
    pname = "jishaku";
    version = "2.5.1";
    format = "setuptools";

    src = python311Packages.fetchPypi {
      inherit pname version;
      hash = "sha256-cQUxC7TgjT5nyEolx7+0YZ+kXKPb0TSuIZ+W9ftFENs=";
    };

    propagatedBuildInputs = with python311Packages; [
      braceexpand
      click
      import-expression
      tabulate
      discordpy
      line_profiler
      yt-dlp
    ];
  }
