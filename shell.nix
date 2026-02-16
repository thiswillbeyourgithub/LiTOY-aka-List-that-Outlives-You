{ pkgs ? import <nixpkgs> { } }:
let
  required-python-packages = ps: with ps;
    let
      get_retries =
        buildPythonPackage rec {
          pname = "get_retries";
          version = "0.1.1";
          src = fetchPypi {
            inherit pname version;
            sha256 = "sha256-Egv1hkh4C1zj3citaXB55ggu8vKYy5rf9EmwjMBIVHc=";
          };
          doCheck = false;
          propagatedBuildInputs = [
            requests
          ];
        };

      get_wayback_machine =
        buildPythonPackage rec {
          pname = "get_wayback_machine";
          version = "0.1.2";
          src = fetchPypi {
            inherit pname version;
            sha256 = "sha256-O9MwxxCXEc4fjN0jIAtbHeEJAJlgdfM+k1NOX5XV5Yg=";
          };
          doCheck = false;
          propagatedBuildInputs = [
            get_retries
          ];
        };

      feedfinder2 =
        buildPythonPackage rec {
          pname = "feedfinder2";
          version = "0.0.4";
          src = fetchPypi {
            inherit pname version;
            sha256 = "sha256-NwHuAabIX4uGWgScMLoLRgiFjIA/6OMNHSif2+idDv4=";
          };
          doCheck = false;
          propagatedBuildInputs = [
            beautifulsoup4
            requests
            six
          ];
        };

      jieba3k =
        buildPythonPackage rec {
          pname = "jieba3k";
          version = "0.35.1";
          src = fetchPypi {
            inherit pname version;
            extension = "zip";
            sha256 = "980a4f2636b778d312518066be90c7697d410dd5a472385f5afced71a2db1c10";
          };
          doCheck = false;
          propagatedBuildInputs = [
          ];
        };

      tinysegmenter =
        buildPythonPackage rec {
          pname = "tinysegmenter";
          version = "0.3";
          src = fetchPypi {
            inherit pname version;
            sha256 = "sha256-7R9tLoBqR1inO+WJdUOEy62tx+GkFMgaFm/JrfLUDG0=";
          };
          doCheck = false;
          propagatedBuildInputs = [
          ];
        };

      newspaper3k =
        buildPythonPackage rec {
          pname = "newspaper3k";
          version = "0.2.8";
          src = fetchPypi {
            inherit pname version;
            sha256 = "sha256-nxvT4ftI9ADHFav4dcx7Cme33c2H9Qya7rj8u72QBPs=";
          };
          doCheck = false;
          propagatedBuildInputs = [
            cssselect
            feedfinder2
            feedparser
            jieba3k
            lxml
            nltk
            pillow
            python-dateutil
            pyyaml
            tinysegmenter
            tldextract
          ];
        };

      ebooklib =
        buildPythonPackage rec {
          pname = "EbookLib";
          version = "0.18";
          src = fetchPypi {
            inherit pname version;
            sha256 = "sha256-OFYmQ6e8lNm/VumTC0kn5Ok7XR0JF/aXpkVNtaHBpTM=";
          };
          doCheck = false;
          propagatedBuildInputs = [
            lxml
            six
          ];
        };
    in
    [
      beautifulsoup4
      ebooklib
      get_wayback_machine
      moviepy
      newspaper3k
      pandas
      pdftotext
      prettytable
      prompt_toolkit
      pygments
      pyqt5
      requests
      tqdm
      youtube-dl
    ];
in
(pkgs.python3.withPackages required-python-packages).env
