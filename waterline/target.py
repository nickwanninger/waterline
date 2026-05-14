import os
import re
import shutil
import shlex
from pathlib import Path


class Target:
    def __init__(self, triple, sysroot=None, llc_flags=None,
                 toolchain_prefix=None, unwrapped_cc=None, dynamic_linker=None):
        self.triple = triple
        self.sysroot = sysroot
        self._llc_flags = llc_flags or []
        self.toolchain_prefix = Path(toolchain_prefix) if toolchain_prefix else None
        self.unwrapped_cc = unwrapped_cc
        self.dynamic_linker = dynamic_linker

    def _detect_unwrapped_clang(self):
        """Find the real clang binary when the in-PATH version is a Nix cc-wrapper."""
        clang = shutil.which("clang")
        if clang:
            try:
                content = Path(clang).read_text()
                m = re.search(r'/nix/store/[a-z0-9]+-clang-\d[^/]*/bin/clang', content)
                if m:
                    return m.group(0)
            except Exception:
                pass
        return "clang"

    def _detect_clang_resource_dir(self, cc):
        """Find the clang resource dir (contains built-in headers like stddef.h)."""
        # For a Nix unwrapped clang, the resource dir is in a sibling store path
        # named <hash>-clang-<version>-lib/lib/clang/<major>/
        m = re.match(r'(/nix/store/[a-z0-9]+-clang-\d[^/]*)/bin/clang', str(cc))
        if m:
            base = Path(m.group(1))
            # Try same-store-path first
            resource = base / "lib" / "clang"
            if resource.exists():
                versions = sorted(resource.iterdir())
                if versions:
                    return str(versions[-1])
            # Try the -lib companion package
            lib_path = Path(str(base) + "-lib")
            if not lib_path.exists():
                # Search for it by pattern
                store = Path("/nix/store")
                pattern = re.sub(r'^/nix/store/[a-z0-9]+-', '', str(base))
                for entry in store.iterdir():
                    if entry.name.endswith("-lib") and pattern.rstrip("-lib") in entry.name:
                        resource = entry / "lib" / "clang"
                        if resource.exists():
                            versions = sorted(resource.iterdir())
                            if versions:
                                return str(versions[-1])
            else:
                resource = lib_path / "lib" / "clang"
                if resource.exists():
                    versions = sorted(resource.iterdir())
                    if versions:
                        return str(versions[-1])
        return None

    def setup_workspace(self, workspace_dir):
        """
        Create cross-compilation helper scripts in workspace_dir/cross-tools/.
        Returns (tools_dir, cc_wrapper_path).
        """
        tools_dir = Path(workspace_dir) / "cross-tools"
        tools_dir.mkdir(exist_ok=True)

        cc = self.unwrapped_cc or self._detect_unwrapped_clang()

        flags = [f"--target={self.triple}"]
        resource_dir = self._detect_clang_resource_dir(cc)
        if resource_dir:
            flags += ["-resource-dir", resource_dir]
        if self.sysroot:
            flags.append(f"--sysroot={self.sysroot}")
        if self.dynamic_linker:
            flags.append(f"-Wl,--dynamic-linker,{self.dynamic_linker}")
        if self.toolchain_prefix:
            flags.append(f"--gcc-toolchain={self.toolchain_prefix}")
            ld = self.toolchain_prefix / "bin" / f"{self.triple}-ld"
            if ld.exists():
                flags.append(f"-fuse-ld={ld}")

        flags_str = " ".join(shlex.quote(f) for f in flags)

        wrapper = tools_dir / "cross-cc"
        wrapper.write_text(f"#!/bin/sh\nexec {cc} {flags_str} \"$@\"\n")
        wrapper.chmod(0o755)

        # C++ wrapper: same flags, clang++ instead of clang
        cxx = cc.replace("/clang", "/clang++", 1) if cc.endswith("/clang") else cc + "++"
        cxx_wrapper = tools_dir / "cross-cxx"
        cxx_wrapper.write_text(f"#!/bin/sh\nexec {cxx} {flags_str} \"$@\"\n")
        cxx_wrapper.chmod(0o755)

        # Shadow the native objcopy with the cross-target version so gllvm
        # can embed bitcode into cross-compiled (non-x86) object files.
        if self.toolchain_prefix:
            rv_objcopy = self.toolchain_prefix / "bin" / f"{self.triple}-objcopy"
            local_objcopy = tools_dir / "objcopy"
            if rv_objcopy.exists() and not local_objcopy.exists():
                local_objcopy.symlink_to(rv_objcopy)

        return tools_dir, wrapper, cxx_wrapper

    @property
    def llc_flags(self):
        return [f"-mtriple={self.triple}"] + self._llc_flags

    @property
    def linker_flags(self):
        """Flags for clang++ when used as a cross-linker (no wrapper)."""
        flags = [f"--target={self.triple}"]
        if self.sysroot:
            flags.append(f"--sysroot={self.sysroot}")
        return flags

    @classmethod
    def riscv64gc(cls, toolchain_prefix="/opt/riscv", sysroot=None, unwrapped_cc=None,
                  dynamic_linker="/lib/ld-linux-riscv64-lp64d.so.1"):
        prefix = Path(toolchain_prefix)
        if sysroot is None:
            sysroot = str(prefix / "sysroot")
        return cls(
            "riscv64-unknown-linux-gnu",
            sysroot=sysroot,
            toolchain_prefix=str(prefix),
            unwrapped_cc=unwrapped_cc,
            dynamic_linker=dynamic_linker,
            llc_flags=["-mcpu=generic-rv64", "-mattr=+m,+a,+f,+d,+c"],
        )
