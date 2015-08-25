import unittest
import trackingshell as ts

class TestExecute(unittest.TestCase):
    def test_echo_success(self):
        s = ts.Shell(['-c', 'echo "trackingshell" &>/dev/null'])
        exit_code = s.delegate(return_exit_code = True)
        self.assertEqual(exit_code, 0)

    def test_echo_typo(self):
        s = ts.Shell(['-c', 'ecsho "trackingshell" &>/dev/null'])
        exit_code = s.delegate(return_exit_code = True)
        self.assertEqual(exit_code, 127)

    def test_multipe_echo_success(self):
        s = ts.Shell(['-c', 'echo tracking &>/dev/null && echo shell &>/dev/null'])
        exit_code = s.delegate(return_exit_code = True)
        self.assertEqual(exit_code, 0)

    def test_multiple_echo_failed(self):
        s = ts.Shell(['-c', 'echo tracking &>/dev/null && ecsho shell &>/dev/null'])
        exit_code = s.delegate(return_exit_code = True)
        self.assertEqual(exit_code, 127)

    def test_subcommand_success(self):
        s = ts.Shell(['-c', 'echo $(date +%Y-%m-%d) &>/dev/null'])
        exit_code = s.delegate(return_exit_code = True)
        self.assertEqual(exit_code, 0)

class TestMakeTarget(unittest.TestCase):
    def test_all_arguments(self):
        command = 'echo $(date +%Y-%m-%d) &>/dev/null'
        target = 'test-target'
        s = ts.Shell(['-t', target, '-c', command])
        s.delegate(return_exit_code = True)
        self.assertEqual(s.mt.command, command)
        self.assertEqual(s.mt.target, target)

    def test_missing_target_argument(self):
        command = 'echo $(date +%Y-%m-%d) &>/dev/null'
        s = ts.Shell(['-t', '-c', command])
        s.delegate(return_exit_code = True)
        self.assertEqual(s.mt.command, command)
        self.assertEqual(s.mt.target, ts.MakeTarget.WITHOUT_TARGET)

    def test_not_defined_target_argument(self):
        command = 'echo $(date +%Y-%m-%d) &>/dev/null'
        s = ts.Shell(['-c', command])
        s.delegate(return_exit_code = True)
        self.assertEqual(s.mt.command, command)
        self.assertEqual(s.mt.target, ts.MakeTarget.WITHOUT_TARGET)

    def test_missing_command(self):
        s = ts.Shell(['-c'])
        with self.assertRaises(SystemExit):
            s.delegate()

class TestExtraArguments(unittest.TestCase):
    def test_define_extra_argument(self):
        command = 'echo $(date +%Y-%m-%d) &>/dev/null'
        target = 'test-target'
        date = '2015-08-25'
        s = ts.Shell(['-d', date, '-t', target, '-c', command])
        s.parser.add_argument('-d', '--date', help="current date")
        s.delegate(return_exit_code = True)
        self.assertEqual(s.mt.command, command)
        self.assertEqual(s.mt.target, target)
        self.assertEqual(s.mt.date, date)

    def test_missing_extra_argument(self):
        command = 'echo $(date +%Y-%m-%d) &>/dev/null'
        target = 'test-target'
        s = ts.Shell(['-t', target, '-c', command])
        s.parser.add_argument('-d', '--date', help="current date")
        s.delegate(return_exit_code = True)
        self.assertEqual(s.mt.command, command)
        self.assertEqual(s.mt.target, target)
        self.assertIsNone(s.mt.date)

@ts.plugin
def test_plugin_before_1(mt, next_plugin_fn):
    if not hasattr(mt, 'known_plugins'):
        mt.known_plugins = []
    mt.known_plugins.append(test_plugin_before_1)
    return next_plugin_fn(mt)

@ts.plugin
def test_plugin_before_2(mt, next_plugin_fn):
    if not hasattr(mt, 'known_plugins'):
        mt.known_plugins = []
    mt.known_plugins.append(test_plugin_before_2)
    return next_plugin_fn(mt)

@ts.plugin
def test_plugin_after_1(mt, next_plugin_fn):
    if not hasattr(mt, 'known_plugins'):
        mt.known_plugins = []
    exit_code = next_plugin_fn(mt)
    mt.known_plugins.append(test_plugin_after_1)
    return exit_code

@ts.plugin
def test_plugin_after_2(mt, next_plugin_fn):
    if not hasattr(mt, 'known_plugins'):
        mt.known_plugins = []
    exit_code = next_plugin_fn(mt)
    mt.known_plugins.append(test_plugin_after_2)
    return exit_code

class TestPlugins(unittest.TestCase):
    def test_single_plugin(self):
        command = 'echo $(date +%Y-%m-%d) &>/dev/null'
        target = 'test-target'
        s = ts.Shell(['-t', target, '-c', command])
        s.plugins.register(test_plugin_before_1)
        s.delegate(return_exit_code = True)
        self.assertEqual(s.mt.known_plugins, [test_plugin_before_1])

    def test_multiple_before_plugin(self):
        command = 'echo $(date +%Y-%m-%d) &>/dev/null'
        target = 'test-target'
        s = ts.Shell(['-t', target, '-c', command])
        s.plugins.register(test_plugin_before_1)
        s.plugins.register(test_plugin_before_2)
        s.delegate(return_exit_code = True)
        self.assertEqual(s.mt.known_plugins, [test_plugin_before_1, test_plugin_before_2])

    def test_multiple_after_plugin(self):
        command = 'echo $(date +%Y-%m-%d) &>/dev/null'
        target = 'test-target'
        s = ts.Shell(['-t', target, '-c', command])
        s.plugins.register(test_plugin_after_1)
        s.plugins.register(test_plugin_after_2)
        s.delegate(return_exit_code = True)
        self.assertEqual(s.mt.known_plugins, [test_plugin_after_2, test_plugin_after_1])

@ts.only_run_with_make_target
@ts.plugin
def test_plugin_with_make_target(mt, next_plugin_fn):
    if not hasattr(mt, 'known_plugins'):
        mt.known_plugins = []
    mt.known_plugins.append(test_plugin_with_make_target)
    return next_plugin_fn(mt)

class TestDecorators(unittest.TestCase):
    def test_single_plugin_with_make_target(self):
        command = 'echo $(date +%Y-%m-%d) &>/dev/null'
        target = 'test-target'
        s = ts.Shell(['-t', target, '-c', command])
        s.plugins.register(test_plugin_with_make_target)
        s.delegate(return_exit_code = True)
        self.assertEqual(s.mt.known_plugins, [test_plugin_with_make_target])

    def test_single_plugin_without_make_target(self):
        command = 'echo $(date +%Y-%m-%d) &>/dev/null'
        s = ts.Shell(['-t', '-c', command])
        s.plugins.register(test_plugin_with_make_target)
        s.delegate(return_exit_code = True)
        self.assertFalse(hasattr(s.mt, 'known_plugins'))

    def test_multiple_plugin_without_make_target(self):
        command = 'echo $(date +%Y-%m-%d) &>/dev/null'
        s = ts.Shell(['-t', '-c', command])
        s.plugins.register(test_plugin_before_1)
        s.plugins.register(test_plugin_with_make_target)
        s.plugins.register(test_plugin_before_2)
        s.delegate(return_exit_code = True)
        self.assertEqual(s.mt.known_plugins, [test_plugin_before_1, test_plugin_before_2])