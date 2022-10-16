import importlib
import pkgutil


def _iter_namespace(ns_pkg):
    # Specifying the second argument (prefix) to iter_modules makes the
    # returned name an absolute name instead of a relative one. This allows
    # import_module to work without having to do additional modification to
    # the name.
    # https://packaging.python.org/en/latest/guides/creating-and-discovering-plugins/
    return pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + ".")


def discover_agents():
    import logspyq.agents

    built_in_agents = {
        name: importlib.import_module(name)
        for _finder, name, _ispkg in _iter_namespace(logspyq.agents)
    }

    from importlib.metadata import entry_points
    agent_entry_points = entry_points(group='logspyq.agents')
    installed_agents = {
        ep.name: ep.load()
        for ep in agent_entry_points
    }
    built_in_agents.update(installed_agents)

    # If 'logseq' exists in dir(agent), then extract that as the agent
    # class. Otherwise, assume the module is the agent class.
    agents = {}
    for name, agent in built_in_agents.items():
        if 'logseq' in dir(agent):
            agents[name] = agent.logseq
        else:
            agents[name] = agent

    return agents
