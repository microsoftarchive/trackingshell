
def plugin(f):
    def wrapper(mt, next_plugin_fn=None):
        # Set an entry message
        entry_message = 'Entry point of `{}` plugin.'.format(f.__name__)
        mt.logger.debug(entry_message, extra = mt.as_dict())

        # Execute the plugin's function
        exit_code = f(mt, next_plugin_fn)

        # Set an exit message
        exit_message = '`{func}` plugin returned {exit_code}'.format(        
            func=f.__name__, exit_code=exit_code)
        mt.logger.debug(exit_message, extra = mt.as_dict())

        # Return the exit code
        return exit_code

    return wrapper

def only_run_in_make_level(f):
    def wrapper(mt, next_plugin_fn=None):
        # If this is a makelevel function we call the current plugin
        if mt.has_makelevel():
            return f(mt, next_plugin_fn)

        # We skip this plugin and call the next one
        return next_plugin_fn(mt)

    return wrapper
    
def only_run_with_make_target(f):
    def wrapper(mt, next_plugin_fn=None):
        # If make target has a target we call the current plugin
        if mt.has_target():
            return f(mt, next_plugin_fn)

        # We skip this plugin and call the next one
        return next_plugin_fn(mt)

    return wrapper