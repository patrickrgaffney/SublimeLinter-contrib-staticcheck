import json
import logging

from SublimeLinter.lint import Linter, LintMatch

logger = logging.getLogger('SublimeLinter.plugin.terraform')


class StaticCheck(Linter):
    # The executable plus all arguments used to lint. The $file_name
    # will be set by super(), and will be the folder path of the file
    # currently in the active view. The "staticcheck" command works
    # best on directories (modules), so it's provided here to avoid the
    # command attempting to guess what directory we are at.
    cmd = ('staticcheck', '-f', 'json', '${file_path}')

    # The staticheck command uses a one-based reporting
    # for line and column numbers.
    line_col_base = (1, 1)

    # A dict of defaults for the linter’s settings.
    defaults = {
        'selector': 'source.go'
    }

    # Turn off stdin. The staticheck command requires a file.
    template_suffix = '-'

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
