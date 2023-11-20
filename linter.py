import json
import logging
import re

from SublimeLinter.lint import Linter, LintMatch

logger = logging.getLogger('SublimeLinter.plugin.terraform')


class StaticCheck(Linter):
    # The executable plus all arguments used to lint. The $file_name
    # will be set by super(), and will be the folder path of the file
    # currently in the active view. The "staticcheck" command works
    # best on directories (modules), so it's provided here to avoid the
    # command attempting to guess what directory we are at.
    cmd = ('staticcheck', '${args}', '-f', 'json', '${file_path}')

    # The staticheck command uses a one-based reporting
    # for line and column numbers.
    line_col_base = (1, 1)

    # A dict of defaults for the linter’s settings.
    defaults = {
        'selector': 'source.go',
    }

    # Turn off stdin. The staticheck command requires a file.
    tempfile_suffix = '-'

    # Regex for handling compile errors.
    compile_regex = re.compile("^(?P<fileName>.*\.go)\:(?P<lineNumber>\d+)\:(?P<columnNumber>\d+)\:\s+(?P<message>.*)")

    def handle_compile_error(self, message):
        """
        Special helper to handle compile errors. These are combined
        into a single error in staticcheck so we expand them here.
        """
        m = self.compile_regex.match(message)
        if m is not None:
            fileName = self.context.get('folder') + '/' + m.group('fileName')
            lineNumber = int(m.group('lineNumber'))
            columnNumber = int(m.group('columnNumber'))
            message = m.group('message')
            return LintMatch(
                code='compile',
                filename=fileName,
                line=lineNumber - self.line_col_base[0],
                col=columnNumber - self.line_col_base[0],
                error_type='error',
                message=message,
            )


    def find_errors(self, output):
        """
        Override find_errors() so we can parse the JSON instead
        of using a regex. Staticcheck reports errors as a steam
        of JSON object, so we parse them one line at a time.
        """
        errors = output.splitlines()

        # Return early to stop iteration if there are no errors.
        if len(errors) == 0:
            return
            yield

        for obj in output.splitlines():
            try:
                data = json.loads(obj)
            except Exception as e:
                logger.warning(e)
                self.notify_failure()


            if data['code'] == 'compile':
                for msg in data['message'].split('\n'):
                    m = self.handle_compile_error(msg)
                    if m is not None:
                        yield m
            else:
                code = data['code']
                error_type = data['severity']
                filename = data['location']['file']
                line = data['location']['line'] - self.line_col_base[0]
                col = data['location']['column'] - self.line_col_base[0]
                message = data['message']

                # Clean up the dependency message.
                if message.startswith("could not analyze dependency"):
                    message = data['message'].split('[')[0]

                # Ensure we don't set negative line/col combinations.
                if line < 0:
                    line = 0
                if col < 0:
                    col = 0

                yield LintMatch(
                    code=code,
                    filename=filename,
                    line=line,
                    col=col,
                    error_type=error_type,
                    message=message,
                )
