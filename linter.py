from SublimeLinter.lint import Linter


class StaticCheck(Linter):
    # The executable plus all arguments used to lint. The $file_name
    # will be set by super(), and will be the folder path of the file
    # currently in the active view. The "staticcheck" command works
    # best on directories (modules), so it's provided here to avoid the
    # command attempting to guess what directory we are at.
    cmd = ('staticcheck', '-f', 'text', '${file_name}')

    regex = (
        r'^(?P<filename>\w+.go):'
        r'(?P<line>\d+):'
        r'(?P<col>\d+):\s+'
        r'(?P<message>.*)'
        r'\((?P<code>(.{4,6}|compile))\)'
    )

    # The staticheck command uses a one-based reporting
    # for line and column numbers.
    line_col_base = (1, 1)

    # A dict of defaults for the linter’s settings.
    defaults = {
        'selector': 'source.go'
    }

    # Turn off stdin. The staticheck command requires a file.
    template_suffix = '-'
