{
  description = "Waterline";

  inputs = {
    nixpkgs.url = "nixpkgs/nixos-25.05";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem
      (system:
        let
          pkgs = nixpkgs.legacyPackages.${system};


          runInputs = with pkgs; [
            llvmPackages_21.libllvm
            llvmPackages_21.clang # -unwrapped
            llvmPackages_21.clang-unwrapped
            llvmPackages_21.stdenv
            llvmPackages_21.libunwind
            llvmPackages_21.mlir
            # llvmPackages_21.libcxxClang
            llvmPackages_21.openmp

            (gllvm.overrideAttrs {
              doCheck = false;
            })
          ];

          buildInputs = with pkgs; runInputs ++ [
            bashInteractive
          ];

        in
        with pkgs; {
          devShell = mkShell {
            inherit buildInputs;


            LOCALE_ARCHIVE = "${glibcLocales}/lib/locale/locale-archive";
            hardeningDisable = ["all"];

            shellHook = ''
              unset NIX_ENFORCE_NO_NATIVE
            '';
          };
        }
      );
}

