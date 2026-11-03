"""ETFIQ toolkit."""
from langchain_core.tools import BaseTool, BaseToolkit

from langchain_etfiq.tools import (EtfiqCompareTool, EtfiqFlowsTool, EtfiqHoldingsTool,
                                   EtfiqProfileTool, EtfiqScreenTool, EtfiqSearchTool)


class EtfiqToolkit(BaseToolkit):
    """Six read-only tools over ETFIQ's free data. No API key.

    Setup: ``pip install langchain-etfiq``

    Instantiate::

        from langchain_etfiq import EtfiqToolkit
        tools = EtfiqToolkit().get_tools()
    """

    def get_tools(self) -> list[BaseTool]:
        return [EtfiqSearchTool(), EtfiqProfileTool(), EtfiqHoldingsTool(),
                EtfiqFlowsTool(), EtfiqCompareTool(), EtfiqScreenTool()]
