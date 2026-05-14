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
        if ws.link_command:
            # Cross-compilation: use the workspace's wrapper (flags already baked in)
            ws.shell(ws.link_command, *args, *self.args, *objects, "-o", output)
        else:
            target_flags = ws.target.linker_flags if ws.target else []
            ws.shell(self.command, *args, *target_flags, *self.args, *objects, "-o", output)
