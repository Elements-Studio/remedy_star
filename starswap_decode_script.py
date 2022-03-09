from dataclasses import dataclass

import starcoin.serde_types as st
import typing

import starcoin.starcoin_stdlib
from starcoin import starcoin_types, bcs
from starcoin.starcoin_stdlib import ScriptFunctionCall, ScriptCall
from starcoin.starcoin_types import Script, TransactionPayload, ScriptFunction


def print_type_arg(type_arg) -> str:
    return "{}::{}".format(type_arg.value.module.value, type_arg.value.name.value)


@dataclass(frozen=True)
class ScriptFunctionCall__addLiquidity(ScriptFunctionCall):
    """.
    """
    X: starcoin_types.TypeTag
    Y: starcoin_types.TypeTag
    amount_x_desired: st.uint128
    amount_y_desired: st.uint128
    amount_x_min: st.uint128
    amount_y_min: st.uint128

    def print(self):
        return "add_liquidity:{} {} {} {} {} {}".format(self.X, self.Y,
                                                        self.amount_x_desired.low, self.amount_y_desired.low,
                                                        self.amount_x_min.low, self.amount_y_min.low)

    def getX(self) -> str:
        return print_type_arg(type_arg=self.X)

    def getY(self) -> str:
        return print_type_arg(type_arg=self.Y)


@dataclass(frozen=True)
class ScriptFunctionCall__stake(ScriptFunctionCall):
    """.
    """
    X: starcoin_types.TypeTag
    Y: starcoin_types.TypeTag
    amount: st.uint128

    def print(self) -> str:
        return "stake: {} {} {}".format(self.X, self.Y, self.amount)

    def get_amount(self):
        return self.amount[0].low

    def get_x_y(self):
        return print_type_arg(type_arg=self.X), print_type_arg(type_arg=self.Y)


@dataclass(frozen=True)
class ScriptFunctionCall__unstake(ScriptFunctionCall):
    """.
    """
    X: starcoin_types.TypeTag
    Y: starcoin_types.TypeTag
    amount: st.uint128

    def print(self) -> str:
        return "unstake: {} {} {}".format(self.X, self.Y, self.amount)

    def get_amount(self):
        return self.amount[0].low

    def get_x_y(self):
        return print_type_arg(type_arg=self.X), print_type_arg(type_arg=self.Y)


@dataclass(frozen=True)
class ScriptFunctionCall__harvest(ScriptFunctionCall):
    """.
    """
    X: starcoin_types.TypeTag
    Y: starcoin_types.TypeTag
    amount: st.uint128

    def print(self) -> str:
        return "unstake: {} {} {}".format(self.X, self.Y, self.amount)

    def get_amount(self):
        return self.amount[0].low

    def get_x_y(self):
        return print_type_arg(type_arg=self.X), print_type_arg(type_arg=self.Y)


@dataclass(frozen=True)
class ScriptFunctionCall__setFarmMultiplier(ScriptFunctionCall):
    """.
    """
    X: starcoin_types.TypeTag
    Y: starcoin_types.TypeTag
    multiplier: st.uint64

    def get_amount(self):
        return self.multiplier[0]

    def get_x_y(self):
        return print_type_arg(type_arg=self.X), print_type_arg(type_arg=self.Y)


@dataclass(frozen=True)
class ScriptFunctionCall__resetFarmActivation(ScriptFunctionCall):
    """.
    """
    X: starcoin_types.TypeTag
    Y: starcoin_types.TypeTag
    activation: st.bool

    def get_amount(self):
        return self.activation

    def get_x_y(self):
        return print_type_arg(type_arg=self.X), print_type_arg(type_arg=self.Y)


def add_liquidity_function(script: TransactionPayload) -> ScriptFunctionCall:
    if not isinstance(script, ScriptFunction):
        raise ValueError("Unexpected transaction payload")
    return ScriptFunctionCall__addLiquidity(
        X=script.ty_args[0],
        Y=script.ty_args[1],
        amount_x_desired=bcs.deserialize(script.args[0], st.uint128),
        amount_y_desired=bcs.deserialize(script.args[1], st.uint128),
        amount_x_min=bcs.deserialize(script.args[2], st.uint128),
        amount_y_min=bcs.deserialize(script.args[3], st.uint128),
    )


def stake_function(script: TransactionPayload) -> ScriptFunctionCall:
    if not isinstance(script, ScriptFunction):
        raise ValueError("Unexpected transaction payload")
    return ScriptFunctionCall__stake(
        X=script.ty_args[0],
        Y=script.ty_args[1],
        amount=bcs.deserialize(script.args[0], st.uint128)
    )


def unstake_function(script: TransactionPayload) -> ScriptFunctionCall:
    if not isinstance(script, ScriptFunction):
        raise ValueError("Unexpected transaction payload")
    return ScriptFunctionCall__unstake(
        X=script.ty_args[0],
        Y=script.ty_args[1],
        amount=bcs.deserialize(script.args[0], st.uint128)
    )


def harvest_function(script: TransactionPayload) -> ScriptFunctionCall:
    if not isinstance(script, ScriptFunction):
        raise ValueError("Unexpected transaction payload")
    return ScriptFunctionCall__harvest(
        X=script.ty_args[0],
        Y=script.ty_args[1],
        amount=bcs.deserialize(script.args[0], st.uint128)
    )


def set_farm_multiplier_function(script: TransactionPayload) -> ScriptFunctionCall:
    if not isinstance(script, ScriptFunction):
        raise ValueError("Unexpected transaction payload")
    return ScriptFunctionCall__setFarmMultiplier(
        X=script.ty_args[0],
        Y=script.ty_args[1],
        multiplier=bcs.deserialize(script.args[0], st.uint64)
    )


def reset_farm_activation_function(script: TransactionPayload) -> ScriptFunctionCall:
    if not isinstance(script, ScriptFunction):
        raise ValueError("Unexpected transaction payload")
    return ScriptFunctionCall__resetFarmActivation(
        X=script.ty_args[0],
        Y=script.ty_args[1],
        activation=bcs.deserialize(script.args[0], st.bool)
    )


def init_custom_decode_function():
    starcoin.starcoin_stdlib.SCRIPT_FUNCTION_DECODER_MAP["TokenSwapFarmScriptstake"] = stake_function
    starcoin.starcoin_stdlib.SCRIPT_FUNCTION_DECODER_MAP["TokenSwapFarmScriptunstake"] = unstake_function
    starcoin.starcoin_stdlib.SCRIPT_FUNCTION_DECODER_MAP["TokenSwapFarmScriptharvest"] = harvest_function
    starcoin.starcoin_stdlib.SCRIPT_FUNCTION_DECODER_MAP[
        "TokenSwapFarmScriptset_farm_multiplier"] = set_farm_multiplier_function
    starcoin.starcoin_stdlib.SCRIPT_FUNCTION_DECODER_MAP[
        "TokenSwapFarmScriptreset_farm_activation"] = reset_farm_activation_function
