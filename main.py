import multiprocessing
import os
from concurrent.futures import ProcessPoolExecutor
from typing import Mapping, NamedTuple, Optional, Tuple

import numpy as np
import pandas as pd
import streamlit as st

from valuation import Number, option_value

HIDE_MENU_STYLE = """
        <style>
        #MainMenu {visibility: hidden;}
        </style>
        """


class Variable(NamedTuple):
    name: str
    display_name: str
    initial_value: Optional[Number]
    min_value: Optional[Number]
    max_value: Optional[Number]
    percentage: bool
    step_size: Optional[Number]
    tooltip: str


VARIABLES = [
    Variable("strike_price", "Strike price", 10.0, 0.0, None, False, 1.0,
             "The strike price is the price at which the company stock may be bought when exercising the option."),
    Variable("stock_price", "Stock price", 10.0, 0.0, None, False, 1.0, "Current price of the company stock."),
    Variable("volatility", "Volatility (yearly)", 0.3, 0.0, 2.0, True, None,
             "The expected volatility of the underlying stock on a yearly basis. "
             "This may be difficult to estimate before IPO."),
    Variable("risk_free_rate", "Risk-free rate (yearly)", 0.04, 0.0, 2.0, True, None,
             "The yearly return that can be expected on a perfectly safe investment. "
             "In practice, the rate on government bonds is often used for this "
             "- for example the U.S. 3-Month T-Bill for US stocks/options."),
    Variable("dividend_rate", "Dividend rate (yearly)", 0.004, 0.0, 0.2, True, None,
             "The yearly dividend rate (some stocks pay dividends)."),
    Variable("exit_rate", "Employee exit rate (yearly)", 0.2, 0.0, 1.0, True, None,
             "The yearly exit rate of employees (the proportion of employees that leaves or is dismissed each year)."),
    Variable("vesting_years", "Vesting period (years)", 3.0, 0.0, 20.0, False, 0.25,
             "The minimum number of years to wait before the stock option can be exercised "
             "(after the option was emitted)."),
    Variable("expiration_years", "Expiration (years)", 5.0, 0.0, 20.0, False, 0.25,
             "The number of years until the option expires."),
]


def variable_to_input(v: Variable) -> Number:
    element = st.number_input if v.min_value is None or v.max_value is None else st.slider
    parameters = {
        "label": v.display_name,
        "min_value": v.min_value * 100 if v.percentage and v.min_value is not None else v.min_value,
        "max_value": v.max_value * 100 if v.percentage and v.max_value is not None else v.max_value,
        "value": v.initial_value * 100 if v.percentage else v.initial_value,
        "step": v.step_size,
        "help": v.tooltip
    }
    if v.percentage:
        parameters["format"] = "%0.1f %%"
    result = element(**parameters)
    return result / 100 if v.percentage else result


def read_inputs() -> Mapping[str, Number]:
    return {v.name: variable_to_input(v) for v in VARIABLES}


@st.cache_resource
def get_executor() -> ProcessPoolExecutor:
    return ProcessPoolExecutor(
        max_workers=min(8, os.cpu_count() or 1),
        mp_context=multiprocessing.get_context("forkserver"),
    )


@st.cache_data(show_spinner=False)
def sweep(variable_name: str, values: Tuple[Number, ...], inputs: Tuple[Tuple[str, Number], ...]) -> Tuple[float, ...]:
    base = dict(inputs)
    executor = get_executor()
    return tuple(executor.map(option_value, [dict(base, **{variable_name: v}) for v in values]))


def plot_free_variable(variable: Variable, inputs: Mapping[str, Number]) -> None:
    max_value = 2 * variable.initial_value if variable.max_value is None else variable.max_value
    min_value = 0 if variable.min_value is None else variable.min_value
    step_size = variable.step_size if variable.step_size else (variable.max_value - variable.min_value) / 20
    variable_range: Tuple[Number, ...] = tuple(np.arange(min_value, max_value, step_size))
    option_values = sweep(variable.name, variable_range, tuple(sorted(inputs.items())))
    display_range = [v * 100 if variable.percentage else v for v in variable_range]
    df = pd.DataFrame({variable.display_name: display_range, "Option value": option_values}).set_index(variable.display_name)
    st.line_chart(df)


def main() -> None:
    st.set_page_config(page_title="WealthWizard - an employee stock option calculator", layout="wide",
                        page_icon=":money_with_wings:")
    st.markdown(HIDE_MENU_STYLE, unsafe_allow_html=True)

    inputs = read_inputs()
    st.metric("Option value", f"{option_value(inputs):.2f}")

    variable = st.selectbox("Variable to plot: ", VARIABLES, format_func=lambda v: v.display_name)
    plot_free_variable(variable, inputs)

    st.markdown("""
    This employee stock option calculator is based on [esovalue](https://pypi.org/project/esovalue/) -
    a Python library to value employee stock options. The library can be used directly for more accurate approximations
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
