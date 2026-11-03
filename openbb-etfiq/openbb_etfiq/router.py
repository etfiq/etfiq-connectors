"""Router exposing ETFIQ-only commands: obb.etfiq.fund_flows and obb.etfiq.benchmark_gap."""
from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import ExtraParams, ProviderChoices, StandardParams
from openbb_core.app.query import Query
from openbb_core.app.router import Router

router = Router(prefix="", description="ETFIQ fund flows and benchmark gap (free, keyless).")


@router.command(model="EtfiqFundFlows")
async def fund_flows(cc: CommandContext, provider_choices: ProviderChoices, standard_params: StandardParams, extra_params: ExtraParams) -> OBBject:
    """Money in and out of an ETF over 1D, 1W, 1M, 3M, YTD, 1Y and since-record windows."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="EtfiqBenchmarkGap")
async def benchmark_gap(cc: CommandContext, provider_choices: ProviderChoices, standard_params: StandardParams, extra_params: ExtraParams) -> OBBject:
    """One-year return of an ETF against its own benchmark, in percentage points."""
    return await OBBject.from_query(Query(**locals()))
