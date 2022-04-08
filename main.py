from functools import partial
from multiprocessing import Pool
from typing import NamedTuple, Optional, Union

from esovalue.eso import value_eso
import streamlit as st
import numpy as np
import pandas as pd
import holoviews as hv

hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

pd.options.plotting.backend = 'holoviews'

Number = Union[int, float]


class Variable(NamedTuple):
    name: str
    display_name: str
    initial_value: Optional[Number]
    min_value: Optional[Number]
    max_value: Optional[Number]
    percentage: bool
    step_size: Optional[Number]


variables = [
    Variable("strike_price", "Strike price", 10.0, 0.0, None, False, 1.0),
    Variable("stock_price", "Stock price", 10.0, 0.0, None, False, 1.0),
    Variable("volatility", "Volatility (yearly)", 0.3, 0.0, 2.0, True, None),
    Variable("risk_free_rate", "Risk-free rate (yearly)", 0.04, 0.0, 2.0, True, None),
    Variable("dividend_rate", "Dividend rate (yearly)", 0.004, 0.0, 0.2, True, None),
    Variable("exit_rate", "Employee exit rate (yearly)", 0.2, 0.0, 1.0, True, None),
    Variable("vesting_years", "Vesting period (years)", 3.0, 0.0, 20.0, False, 0.25),
    Variable("expiration_years", "Expiration (years)", 5.0, 0.0, 20.0, False, 0.25),
]


def variable_to_input(v: Variable) -> Number:
    element = st.number_input if v.min_value is None or v.max_value is None else st.slider
    parameters = {
        "label": v.display_name,
        "min_value": v.min_value * 100 if v.percentage and v.min_value is not None else v.min_value,
        "max_value": v.max_value * 100 if v.percentage and v.max_value is not None else v.max_value,
        "value": v.initial_value * 100 if v.percentage else v.initial_value,
        "step": v.step_size
    }
    if v.percentage:
        parameters["format"] = "%0.1f %%"
    result = element(**parameters)
    return result / 100 if v.percentage else result


DEFAULT_PARAMETERS = dict({
    "iterations": 100,
    "m": None
}, **{v.name: variable_to_input(v) for v in variables})


def get_option_value(**parameters):
    return float(value_eso(**dict(DEFAULT_PARAMETERS, **parameters)))


st.metric("Option value", f"{get_option_value():.2f}")


def hvplot_chart(plot):
    return st.bokeh_chart(hv.render(plot, backend='bokeh'))


def _get_option_value_with_override(variable_name: str, value: Number):
    return get_option_value(**dict(DEFAULT_PARAMETERS, **{variable_name: value}))


def plot_free_variable(variable: Variable):
    max_value = 2*variable.initial_value if variable.max_value is None else variable.max_value
    min_value = 0 if variable.min_value is None else variable.min_value
    step_size = variable.step_size if variable.step_size else (variable.max_value - variable.min_value) / 20
    variable_range = pd.Series(np.arange(min_value, max_value, step_size))
    with Pool() as p:
        option_values = p.map(partial(_get_option_value_with_override, variable.name), variable_range)
    hvplot_chart(pd.DataFrame({variable.display_name: variable_range * 100 if variable.percentage else variable_range,
                               "Option value": option_values}).set_index(variable.display_name).plot.line())


plot_free_variable(st.selectbox("Variable to plot: ", variables, format_func=lambda v: v.display_name))
