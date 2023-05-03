from pathlib import Path


class Linker:
    """
    A linker is a class which performs operations similar to

        $ gcc input.o -o binary

    This is intended to enable runtimes to be linked for a
    specific pipeline
    """

    # self.command: the linker command
    command = "clang++"
    # self.args: additional arguments to be passed to the linker
    args = []

    def link(self, ws, objects, output, args):
        # it's pretty safe to link using clang++.
        ws.shell(self.command, *args, *self.args, *objects, "-o", output)
