import os

from astronverse.scheduler.__main__ import main

from meta_build import MetaBuilder

if __name__ == "__main__":
    MetaBuilder()
    os.environ["DEBUG"] = "1"
    main()
