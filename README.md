# trackingshell

You can tracks makefile's targets with this tool easily. This library is part of the [night-shift](https://github.com/6wunderkinder/night-shift) framework.

## Installation

```bash
$ pip install trackingshell
```

## Write your own plugin(s)

Create a new Python file and import the `trackingshell` package.

```python
import trackingshell as ts
```

Add as many plugin as you want. You have to define the `@ts.plugin` decorator for every plugin. Every plugin has two parameters:

- **mt**: MakeTarget object.
- **next_plugin_fn**: Next plugin function.

The `MakeTarget` object has the following attributes by default:

- **target**: Name of the makefile's target
- **command**: Current command.
- **logger**: [logging](https://docs.python.org/2/library/logging.html) if you want to write something.

and the following functions:

- **has_target**: Do we have a target at the moment?
- **has_makelevel**: Is the current command in the makefile?

Let's see an example for a plugin.

```python
@ts.plugin
def timing_env_plugin(mt, next_plugin_fn):
    try:
        with io.open("logs/timing_env.log", "a", encoding = 'utf-8') as fd:
            data = {
                'command': mt.command.replace('\n', ''),
                'target': mt.target,
                'unique_nr': random.randint(0, 1000000),
                'has_make_level': mt.has_makelevel(),
                'started_at': datetime.datetime.now().isoformat(),
                'tag': 'BEGIN'
            }
            fd.write(u"{}\n".format(json.dumps(data)))
            fd.flush()

            exit_code = next_plugin_fn(mt)

            data.update({
                'tag': 'END',
                'finished_at': datetime.datetime.now().isoformat(),
                'exit_code': exit_code
            })
            fd.write(u"{}\n".format(json.dumps(data)))
            fd.flush()
    
    except IOError:
        exit_code = next_plugin_fn(mt)

    return exit_code
```

If you don't want to execute a plugin in every time you can define extra decorators as well.

- **only_run_in_make_level**: Only run when the current command in the makefile.
- **only_run_with_make_target**: Only run when we have a target name.

Let's see an example.

```python
@ts.only_run_in_make_level
@ts.only_run_with_make_target
@ts.plugin
def target_plugin(mt, next_plugin_fn):
    path = "logs/{}.log".format(mt.target.replace("/", "_"))

    try:
        with io.open(path, "a", encoding='utf-8') as fd:
            fd.write(u"\n[tracking_shell {}] Working on target {} ommand {}\n\n" \
                .format(datetime.datetime.now(), mt.target, repr(mt.command)))
            fd.flush()
        mt.command = "({}) 2>&1 | tee -a {}".format(mt.command, path)

    except IOError:
        mt.logger.error(u'Could not open target log `{}`'.format(path), extra = mt.as_dict())
        mt.command = "({}) 2>&1".format(mt.command)

    return next_plugin_fn(mt)
```

## Delegate the execution and register your plugins

```python
if __name__ == '__main__':
    shell = ts.Shell(sys.argv[1:])
    shell.plugins.register(timing_env_plugin)
    shell.plugins.register(target_plugin)
    shell.delegate()
```

You can add extra [arguments](https://docs.python.org/3/library/argparse.html) if necessary.

```python
shell.parser.add_argument('-d', '--date', help="current date")
```

This value will be available in the `MakeTarget` object. (e.g.: `mt.date`)

## Replace the shell in your makefile

```makefile
SHELL=./yourscript.py --target $@
```

That's it. Enjoy!

## License

Copyright © 2013-2015 6 Wunderkinder GmbH.

Distributed under the MIT License.
