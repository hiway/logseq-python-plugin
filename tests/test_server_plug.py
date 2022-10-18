import pytest
from logspyq import agents
from logspyq.server.plug import discover_agents


async def test_plug_discover():
    agents = discover_agents()
    assert len(agents) == 1  # Update when adding new agents!
    assert "logspyq.agents.hello" in agents