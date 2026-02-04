import logging
import sys
import os
import importlib.util

# Ensure current directory is in path so we can import build script
sys.path.append(os.getcwd())

log = logging.getLogger("mkdocs")

def on_pre_build(config, **kwargs):
    """
    Generate the navigation pages before the build process starts.
    """
    log.info("Generating navigation pages from nav_data.yml")
    try:
        # Import build.py from file path directly to avoid ModuleNotFoundError
        spec = importlib.util.spec_from_file_location("build", "build.py")
        if spec and spec.loader:
            build = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(build)
            build.generate_nav()
        else:
            log.error("Could not load build.py")

    except Exception as e:
        log.error(f"Failed to generate navigation pages: {e}")
        import traceback
        traceback.print_exc()

def on_serve(server, config, builder, **kwargs):
    """
    Add nav_data.yml to the watched files list.
    """
    server.watch('nav_data.yml', builder)
    return server
