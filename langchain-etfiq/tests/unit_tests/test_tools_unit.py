"""Standard LangChain tool unit tests, run offline."""
from typing import Type

from langchain_tests.unit_tests import ToolsUnitTests

from langchain_etfiq import EtfiqProfileTool, EtfiqSearchTool


class TestSearchUnit(ToolsUnitTests):
    @property
    def tool_constructor(self) -> Type[EtfiqSearchTool]:
        return EtfiqSearchTool

    @property
    def tool_constructor_params(self) -> dict:
        return {}

    @property
    def tool_invoke_params_example(self) -> dict:
        return {"query": "spy", "limit": 3}


class TestProfileUnit(ToolsUnitTests):
    @property
    def tool_constructor(self) -> Type[EtfiqProfileTool]:
        return EtfiqProfileTool

    @property
    def tool_constructor_params(self) -> dict:
        return {}

    @property
    def tool_invoke_params_example(self) -> dict:
        return {"ticker": "SPY"}
