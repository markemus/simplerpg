def iter_cmds(cmds):
    """This will allow us to iterate over multiple input() statements in tests.
    to use: input = iter_cmds([cmds])"""

    def iterate(cmd_list):
        for x in cmd_list:
            yield x

    iter_inputs = iterate(cmds)
    return lambda _: next(iter_inputs)