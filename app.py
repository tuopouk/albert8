"""Albert 8: explore compound growth, investment fees, and inflation."""

import os
from html import escape
from urllib.parse import urlsplit

import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import ALL, Dash, Input, Output, State, dcc, html
from dash_bootstrap_templates import ThemeSwitchAIO, load_figure_template
from flask import Flask, request
from translations import PLOTLY_LOCALES, translate, year_marks


THEMES = [dbc.themes.FLATLY, dbc.themes.DARKLY]
load_figure_template(["flatly", "darkly"])


class SharingDash(Dash):
    def interpolate_index(self, **kwargs):
        # Render sharing metadata on the server: link crawlers do not run Dash callbacks.
        public_url = os.environ.get("PUBLIC_URL", request.url_root).rstrip("/")
        parsed = urlsplit(public_url)
        if parsed.scheme not in ("http", "https") or not parsed.netloc or parsed.query or parsed.fragment:
            raise ValueError("PUBLIC_URL must be an absolute HTTP(S) app URL without a query or fragment.")
        image_url = f"{public_url}/assets/social-preview.png"
        title = "Albert 8 | Compound interest calculator"
        description = (
            "Explore how regular savings, investment returns, fees, and inflation "
            "shape your future. Available in English, Finnish, and Chinese."
        )
        metadata = [
            ("name", "description", description),
            ("property", "og:type", "website"),
            ("property", "og:site_name", "Albert 8"),
            ("property", "og:title", title),
            ("property", "og:description", description),
            ("property", "og:url", public_url + "/"),
            ("property", "og:image", image_url),
            ("property", "og:image:type", "image/png"),
            ("property", "og:image:width", "1200"),
            ("property", "og:image:height", "630"),
            ("property", "og:image:alt", "Albert 8: compound interest calculator with the a8 logo and a growth chart."),
            ("name", "twitter:card", "summary_large_image"),
            ("name", "twitter:title", title),
            ("name", "twitter:description", description),
            ("name", "twitter:image", image_url),
            ("name", "twitter:image:alt", "Albert 8: compound interest calculator with the a8 logo and a growth chart."),
        ]
        kwargs["metas"] += "\n" + "\n".join(
            f'<meta {attribute}="{key}" content="{escape(value, quote=True)}">'
            for attribute, key, value in metadata
        )
        kwargs["favicon"] = (
            f'<link rel="icon" type="image/png" href="{escape(self.get_asset_url("icon.png"), quote=True)}">'
            f'\n<link rel="apple-touch-icon" href="{escape(self.get_asset_url("icon.png"), quote=True)}">'
        )
        return super().interpolate_index(**kwargs)


server = Flask(__name__)
server.secret_key = os.environ.get("secret_key") or os.urandom(32)
app = SharingDash(
    __name__,
    server=server,
    external_stylesheets=[THEMES[0]],
    external_scripts=[
        "https://cdn.plot.ly/plotly-locale-fi-latest.js",
        "https://cdn.plot.ly/plotly-locale-zh-cn-latest.js",
    ],
    update_title=None,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
app.title = "Albert 8 | Compound interest calculator"
theme_switch = ThemeSwitchAIO(
    aio_id="theme",
    themes=THEMES,
    switch_props={"label": "Light theme", "labelClassName": "visually-hidden"},
)


def compound_funds(
    seed_capital=100,
    monthly_savings=100,
    expected_yearly_profit=0.06,
    saving_years=5,
    yearly_expenses=0.02,
    inflation=0.02,
):
    """Keep the original monthly growth and end-of-month contribution model."""
    monthly_profit = expected_yearly_profit / 12
    monthly_expenses = yearly_expenses / 12
    monthly_inflation = inflation / 12
    compound = zero_expense_compound = bank = seed_capital
    bank_inflation = inflation_compound = zero_expense_inflation_compound = seed_capital
    compound_list = []

    for month in range(12 * saving_years):
        zero_expense_compound = zero_expense_compound * (1 + monthly_profit)
        zero_expense_compound = zero_expense_compound + monthly_savings
        compound = compound * (1 + monthly_profit - monthly_expenses)
        compound = compound + monthly_savings
        bank = bank + monthly_savings
        zero_expense_inflation_compound = zero_expense_inflation_compound * (1 + monthly_profit)
        zero_expense_inflation_compound = zero_expense_inflation_compound * (1 - monthly_inflation)
        zero_expense_inflation_compound = zero_expense_inflation_compound + monthly_savings
        inflation_compound = inflation_compound * (1 + monthly_profit - monthly_expenses)
        inflation_compound = inflation_compound * (1 - monthly_inflation)
        inflation_compound = inflation_compound + monthly_savings
        bank_inflation = bank_inflation * (1 - monthly_inflation)
        bank_inflation = bank_inflation + monthly_savings
        if (month + 1) % 12 == 0:
            compound_list.append(
                {
                    "years_saved": (month + 1) // 12,
                    "compound": compound,
                    "inflation_compound": inflation_compound,
                    "zero_expense_compound": zero_expense_compound,
                    "bank_inflation": bank_inflation,
                    "zero_expense_inflation_compound": zero_expense_inflation_compound,
                    "bank": bank,
                }
            )
    return pd.DataFrame(compound_list)


def money(value, currency, language="en"):
    number = f"{value:,.2f}".replace(",", " ")
    if language == "fi":
        number = number.replace(".", ",")
    return number + f" {currency}"


def percent(value, language):
    number = f"{value:g}"
    return (number.replace(".", ",") if language == "fi" else number) + "%"


def growth_figure(frame, currency, template, inflation_adjusted=False, language="en"):
    columns = (
        ["zero_expense_inflation_compound", "inflation_compound", "bank_inflation"]
        if inflation_adjusted
        else ["zero_expense_compound", "compound", "bank"]
    )
    figure = go.Figure()
    for column, name, color, dash_style in zip(
        columns,
        ["Before fees", "After fees", "Contributions only"],
        ["#3b82f6", "#14b8a6", "#94a3b8"],
        ["solid", "solid", "dot"],
    ):
        figure.add_trace(
            go.Scatter(
                x=frame.years_saved,
                y=np.round(frame[column], 2),
                name=translate(name, language),
                mode="lines",
                line={"color": color, "width": 3, "dash": dash_style},
                customdata=[money(value, currency, language) for value in frame[column]],
                hovertemplate="%{customdata}<extra>%{fullData.name}</extra>",
            )
        )
    figure.update_layout(
        template=template,
        font={"family": "Inter, Segoe UI, sans-serif", "size": 12},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin={"l": 12, "r": 20, "t": 20, "b": 12},
        height=355,
        hovermode="x unified",
        hoverlabel={"namelength": -1},
        xaxis={"title": translate("Years invested", language), "dtick": max(1, int(frame.years_saved.max()) // 7)},
        yaxis={"title": f"{translate('Value', language)} ({currency})", "tickformat": ",.0f", "rangemode": "tozero"},
        legend={"orientation": "h", "y": -0.25, "x": 0, "font": {"size": 11}},
        separators=", " if language == "fi" else ".,",
        uirevision="growth",
    )
    return figure


def text(key):
    return html.Span(translate(key), id={"type": "translation", "key": key})


def slider_control(identifier, label, value, maximum, step, marks, minimum=0):
    return html.Fieldset(
        [
            html.Legend(
                [
                    html.Span(text(label), id=f"{identifier}-label"),
                    html.Output(id=f"{identifier}-container", className="control-value"),
                ],
                className="control-heading",
            ),
            dcc.Slider(
                id=identifier,
                min=minimum,
                max=maximum,
                value=value,
                step=step,
                marks=marks,
                tooltip={"placement": "bottom", "always_visible": False},
            ),
        ],
        className="slider-control",
    )


def metric(label, identifier, detail, featured=False):
    return html.Div(
        [
            html.P(text(label), className="metric-label"),
            html.H2(id=identifier, className="metric-value"),
            html.P(text(detail), className="metric-detail"),
        ],
        className="metric-card featured" if featured else "metric-card",
    )


GRAPH_CONFIG = {
    "displaylogo": False,
    "responsive": True,
    "modeBarButtonsToRemove": ["lasso2d", "select2d", "sendChartToCloud"],
    "locales": PLOTLY_LOCALES,
}


def serve_layout():
    return html.Div(
        [
            html.Header(
                [
                    html.A(
                        [html.Span("a8", className="brand-mark"), html.Span("Albert 8")],
                        href="#",
                        className="brand",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Label(text("Language"), htmlFor="language", className="language-label"),
                                    dbc.Select(
                                        id="language",
                                        options=[
                                            {"label": "English", "value": "en"},
                                            {"label": "中文（简体）", "value": "zh-CN"},
                                            {"label": "Suomi", "value": "fi"},
                                        ],
                                        value="en",
                                        persistence=True,
                                        persistence_type="local",
                                    ),
                                ],
                                className="language-control",
                            ),
                            html.Span(text("Light / dark"), className="theme-label"),
                            theme_switch,
                        ],
                        className="theme-control",
                    ),
                ],
                className="app-header",
            ),
            html.Main(
                [
                    html.Section(
                        [
                            html.Div(text("A LITTLE TODAY. MORE TOMORROW."), className="eyebrow"),
                            html.H1([text("Give your savings "), html.Span(text("a clearer future."), className="hero-accent")]),
                            html.P(
                                text("See how time, regular investing, and small fees shape your wealth."),
                                className="hero-description",
                            ),
                        ],
                        className="hero",
                    ),
                    html.Div(
                        [
                            html.Aside(
                                [
                                    html.Div(text("YOUR PLAN"), className="eyebrow"),
                                    html.H2(text("Make it your own"), className="section-title"),
                                    html.P(text("Adjust the assumptions to explore what is possible."), className="muted"),
                                    html.Fieldset(
                                        [
                                            html.Legend(text("Currency"), className="currency-label"),
                                            dbc.RadioItems(
                                                id="currency",
                                                options=[{"label": item, "value": item} for item in ["€", "$", "£", "¥"]],
                                                value="€",
                                                inline=True,
                                                className="currency-picker",
                                            ),
                                        ]
                                    ),
                                    slider_control("seed", "Starting capital", 1000, 100000, 1, {0: "0", 50000: "50 000", 100000: "100 000"}),
                                    slider_control("savings", "Monthly contribution", 15, 2000, 1, {0: "0", 1000: "1 000", 2000: "2 000"}),
                                    slider_control("years", "Investment horizon", 5, 70, 1, year_marks("en"), minimum=1),
                                    html.Hr(),
                                    html.H3(text("Market assumptions"), className="assumptions-title"),
                                    slider_control("profit", "Annual return", 9.9, 100, 0.1, {0: "0%", 50: "50%", 100: "100%"}),
                                    slider_control("expenses", "Annual fees", 0.2, 5, 0.01, {0: "0%", 2.5: "2.5%", 5: "5%"}),
                                    slider_control("inflation", "Annual inflation", 2, 10, 0.1, {0: "0%", 5: "5%", 10: "10%"}),
                                    html.P(text("Currency changes the display only; no exchange rates are applied."), className="input-note"),
                                ],
                                className="plan-panel",
                                id="plan-panel",
                                **{"aria-label": "Investment plan inputs"},
                            ),
                            html.Section(
                                [
                                    html.Div(
                                        [
                                            html.Div(
                                                [html.Div(text("THE BIG PICTURE"), className="eyebrow"), html.H2(text("Your growth outlook"), className="section-title")]
                                            ),
                                            html.Span(id="horizon-badge", className="horizon-badge"),
                                        ],
                                        className="results-heading",
                                    ),
                                    html.Div(
                                        [
                                            metric("Projected balance", "balance", "After investment fees", featured=True),
                                            metric("Total contributed", "contributed", "Starting capital + monthly savings"),
                                            metric("Impact of fees", "fee-impact", "Compared with a fee-free investment"),
                                        ],
                                        className="metrics",
                                        **{"aria-live": "polite"},
                                    ),
                                    html.Div(
                                        [
                                            html.H3(text("Watch your money grow"), className="chart-title"),
                                            html.P(text("Compare investment growth with your contributions over time."), className="muted"),
                                            dcc.Loading(dcc.Graph(id="nominal-graph", config=GRAPH_CONFIG), color="#14b8a6"),
                                        ],
                                        className="chart-card",
                                    ),
                                    html.Div(
                                        [
                                            html.Div(
                                                [
                                                    html.H3(text("What about purchasing power?"), className="chart-title"),
                                                    html.Span(text("INFLATION ADJUSTED"), className="chart-tag"),
                                                ],
                                                className="chart-heading",
                                            ),
                                            html.P(text("The same plan, with the effect of inflation applied each month."), className="muted"),
                                            dcc.Loading(dcc.Graph(id="real-graph", config=GRAPH_CONFIG), color="#14b8a6"),
                                        ],
                                        className="chart-card",
                                    ),
                                    html.Details(
                                        [
                                            html.Summary(text("How this projection works")),
                                            html.P(text("methodology")),
                                        ],
                                        className="methodology",
                                    ),
                                ],
                                className="results",
                                id="results",
                                **{"aria-label": "Investment projection"},
                            ),
                        ],
                        className="dashboard",
                    ),
                    html.Footer(
                        [
                            html.Span("Albert 8", className="footer-brand"),
                            text("Built for perspective, not prediction. Illustrative projections only; not financial advice."),
                        ],
                        className="app-footer",
                    ),
                ],
                className="app-main",
            ),
        ],
        id="app-shell",
        className="app-shell",
        **{"data-bs-theme": "light", "lang": "en"},
    )


app.layout = serve_layout


@app.callback(
    Output({"type": "translation", "key": ALL}, "children"),
    Output("app-shell", "lang"),
    Output("plan-panel", "aria-label"),
    Output("results", "aria-label"),
    Output(ThemeSwitchAIO.ids.switch("theme"), "label"),
    Output("years", "marks"),
    Output("expenses", "marks"),
    Input("language", "value"),
    State({"type": "translation", "key": ALL}, "id"),
)
def update_language(language, identifiers):
    return (
        [translate(identifier["key"], language) for identifier in identifiers],
        language,
        translate("Investment plan inputs", language),
        translate("Investment projection", language),
        translate("Light theme", language),
        year_marks(language),
        {0: "0%", 2.5: percent(2.5, language), 5: "5%"},
    )


app.clientside_callback(
    """function(language) {
        const titles = {
            en: "Compound interest calculator",
            fi: "Korkoa korolle -laskuri",
            "zh-CN": "复利计算器"
        };
        document.documentElement.lang = language;
        document.title = "Albert 8 | " + titles[language];
        return window.dash_clientside.no_update;
    }""",
    Output("language", "title"),
    Input("language", "value"),
)


@app.callback(
    Output("app-shell", "data-bs-theme"),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
)
def update_theme(light):
    return "light" if light else "dark"


@app.callback(
    Output("nominal-graph", "figure"),
    Output("real-graph", "figure"),
    Output("balance", "children"),
    Output("contributed", "children"),
    Output("fee-impact", "children"),
    Output("horizon-badge", "children"),
    Output("seed-container", "children"),
    Output("savings-container", "children"),
    Output("years-container", "children"),
    Output("profit-container", "children"),
    Output("expenses-container", "children"),
    Output("inflation-container", "children"),
    Output("nominal-graph", "config"),
    Output("real-graph", "config"),
    Input("seed", "value"),
    Input("savings", "value"),
    Input("profit", "value"),
    Input("years", "value"),
    Input("expenses", "value"),
    Input("inflation", "value"),
    Input("currency", "value"),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
    Input("language", "value"),
)
def update_projection(seed, savings, profit, years, expenses, inflation_rate, currency, light, language="en"):
    frame = compound_funds(seed, savings, profit / 100, years, expenses / 100, inflation_rate / 100)
    last = frame.iloc[-1]
    template = "flatly" if light else "darkly"
    return (
        growth_figure(frame, currency, template, language=language),
        growth_figure(frame, currency, template, inflation_adjusted=True, language=language),
        money(last.compound, currency, language),
        money(last.bank, currency, language),
        money(last.zero_expense_compound - last.compound, currency, language),
        translate("{years}-year plan", language, years=years),
        money(seed, currency, language),
        money(savings, currency, language),
        translate("1 year" if years == 1 else "{years} years", language, years=years),
        percent(profit, language),
        percent(expenses, language),
        percent(inflation_rate, language),
        {**GRAPH_CONFIG, "locale": language},
        {**GRAPH_CONFIG, "locale": language},
    )


if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=int(os.environ.get("PORT", "8050")))
