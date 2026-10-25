"""Build hook that bundles the repository's legal documents into the wheel."""

import importlib.util
from pathlib import Path

from setuptools import setup
from setuptools.command.build_py import build_py

ROOT = Path(__file__).resolve().parent


def _load_bundler():
    spec = importlib.util.spec_from_file_location("aegean_bundler", ROOT / "aegean_licensing" / "bundler.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load the licensing document bundler.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.bundle_documents


class BundleDocuments(build_py):
    """Copy licenses, policies, and the CLA workflow into the built package."""

    def run(self) -> None:
        super().run()
        _load_bundler()(ROOT, Path(self.build_lib))


setup(cmdclass={"build_py": BundleDocuments})
