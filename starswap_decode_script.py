from dataclasses import dataclass

import starcoin.serde_types as serde_types

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
    amount_x_desired: serde_types.uint128
    amount_y_desired: serde_types.uint128
    amount_x_min: serde_types.uint128
    amount_y_min: serde_types.uint128

    def print(self):
        return "add_liquidity:{} {} {} {} {} {}".format(self.X, self.Y,
                                                        self.amount_x_desired.__int__, self.amount_y_desired.__int__,
                                                        self.amount_x_min.__int__, self.amount_y_min.__int__)

    def get_x_y(self):
        return print_type_arg(type_arg=self.X), print_type_arg(type_arg=self.Y)

    def get_amount(self):
        return (int(self.amount_x_desired[0]), int(self.amount_y_desired[0]))

    def get_amount_x_desired(self):
        return int(self.amount_x_desired[0])

    def get_amount_y_desired(self):
        return int(self.amount_y_desired[0])


@dataclass(frozen=True)
class ScriptFunctionCall__removeLiquidity(ScriptFunctionCall):
    """.
    """
    X: starcoin_types.TypeTag
    Y: starcoin_types.TypeTag
    liquidity: serde_types.uint128
    amount_x_min: serde_types.uint128
    amount_y_min: serde_types.uint128

    def print(self):
        return "remove_liquidity :{} {} {} {} {}".format(self.X, self.Y,
                                                         int(self.amount_x_min), int(self.amount_y_min),
                                                         int(self.liquidity))

    def get_x_y(self):
        return print_type_arg(type_arg=self.X), print_type_arg(type_arg=self.Y)

    def get_amount(self) -> int:
        return int(self.liquidity[0])


@dataclass(frozen=True)
class ScriptFunctionCall__stake(ScriptFunctionCall):
    """.
    """
    X: starcoin_types.TypeTag
    Y: starcoin_types.TypeTag
    amount: serde_types.uint128

    def print(self) -> str:
        return "stake: {} {} {}".format(self.X, self.Y, self.amount)

    def get_amount(self) -> int:
        return int(self.amount[0])

    def get_x_y(self):
        return print_type_arg(type_arg=self.X), print_type_arg(type_arg=self.Y)


@dataclass(frozen=True)
class ScriptFunctionCall__unstake(ScriptFunctionCall):
    """.
    """
    X: starcoin_types.TypeTag
    Y: starcoin_types.TypeTag
    amount: serde_types.uint128

    def print(self) -> str:
        return "unstake: {} {} {}".format(self.X, self.Y, self.amount)

    def get_amount(self) -> int:
        return int(self.amount[0])

    def get_x_y(self):
        return print_type_arg(type_arg=self.X), print_type_arg(type_arg=self.Y)


@dataclass(frozen=True)
class ScriptFunctionCall__harvest(ScriptFunctionCall):
    """.
    """
    X: starcoin_types.TypeTag
    Y: starcoin_types.TypeTag
    amount: serde_types.uint128

    def print(self) -> str:
        return "unstake: {} {} {}".format(self.X, self.Y, self.amount)

    def get_amount(self) -> int:
        return int(self.amount[0])

    def get_x_y(self):
        return print_type_arg(type_arg=self.X), print_type_arg(type_arg=self.Y)


@dataclass(frozen=True)
class ScriptFunctionCall__setFarmMultiplier(ScriptFunctionCall):
    """.
    """
    X: starcoin_types.TypeTag
    Y: starcoin_types.TypeTag
    multiplier: serde_types.uint64

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
    activation: serde_types.bool

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
        amount_x_desired=bcs.deserialize(script.args[0], obj_type=serde_types.uint128),
        amount_y_desired=bcs.deserialize(script.args[1], serde_types.uint128),
        amount_x_min=bcs.deserialize(script.args[2], serde_types.uint128),
        amount_y_min=bcs.deserialize(script.args[3], serde_types.uint128),
    )


def remove_liquidity_function(script: TransactionPayload) -> ScriptFunctionCall:
    if not isinstance(script, ScriptFunction):
        raise ValueError("Unexpected transaction payload")
    return ScriptFunctionCall__removeLiquidity(
        X=script.ty_args[0],
        Y=script.ty_args[1],
        liquidity=bcs.deserialize(script.args[0], serde_types.uint128),
        amount_x_min=bcs.deserialize(script.args[1], serde_types.uint128),
        amount_y_min=bcs.deserialize(script.args[2], serde_types.uint128),
    )


def stake_function(script: TransactionPayload) -> ScriptFunctionCall:
    if not isinstance(script, ScriptFunction):
        raise ValueError("Unexpected transaction payload")
    return ScriptFunctionCall__stake(
        X=script.ty_args[0],
        Y=script.ty_args[1],
        amount=bcs.deserialize(script.args[0], serde_types.uint128)
    )


def unstake_function(script: TransactionPayload) -> ScriptFunctionCall:
    if not isinstance(script, ScriptFunction):
        raise ValueError("Unexpected transaction payload")
    return ScriptFunctionCall__unstake(
        X=script.ty_args[0],
        Y=script.ty_args[1],
        amount=bcs.deserialize(script.args[0], serde_types.uint128)
    )


def harvest_function(script: TransactionPayload) -> ScriptFunctionCall:
    if not isinstance(script, ScriptFunction):
        raise ValueError("Unexpected transaction payload")
    return ScriptFunctionCall__harvest(
        X=script.ty_args[0],
        Y=script.ty_args[1],
        amount=bcs.deserialize(script.args[0], serde_types.uint128)
    )


def set_farm_multiplier_function(script: TransactionPayload) -> ScriptFunctionCall:
    if not isinstance(script, ScriptFunction):
        raise ValueError("Unexpected transaction payload")
    return ScriptFunctionCall__setFarmMultiplier(
        X=script.ty_args[0],
        Y=script.ty_args[1],
        multiplier=bcs.deserialize(script.args[0], serde_types.uint64)
    )


def reset_farm_activation_function(script: TransactionPayload) -> ScriptFunctionCall:
    if not isinstance(script, ScriptFunction):
        raise ValueError("Unexpected transaction payload")
    return ScriptFunctionCall__resetFarmActivation(
        X=script.ty_args[0],
        Y=script.ty_args[1],
        activation=bcs.deserialize(script.args[0], serde_types.bool)
    )


def init_custom_decode_function():
    starcoin.starcoin_stdlib.SCRIPT_FUNCTION_DECODER_MAP["TokenSwapScriptsadd_liquidity"] = add_liquidity_function
    starcoin.starcoin_stdlib.SCRIPT_FUNCTION_DECODER_MAP["TokenSwapScriptsremove_liquidity"] = remove_liquidity_function
    # starcoin.starcoin_stdlib.SCRIPT_FUNCTION_DECODER_MAP["TokenSwapFarmScriptstake"] = stake_function
    # starcoin.starcoin_stdlib.SCRIPT_FUNCTION_DECODER_MAP["TokenSwapFarmScriptunstake"] = unstake_function
    # starcoin.starcoin_stdlib.SCRIPT_FUNCTION_DECODER_MAP["TokenSwapFarmScriptharvest"] = harvest_function
    starcoin.starcoin_stdlib.SCRIPT_FUNCTION_DECODER_MAP[
        "TokenSwapFarmScriptset_farm_multiplier"] = set_farm_multiplier_function
    starcoin.starcoin_stdlib.SCRIPT_FUNCTION_DECODER_MAP[
        "TokenSwapFarmScriptreset_farm_activation"] = reset_farm_activation_function
