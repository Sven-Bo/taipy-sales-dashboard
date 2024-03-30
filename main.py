import pandas as pd
from taipy.gui import Gui, notify
import taipy.gui.builder as tgb


data = pd.read_excel(
    io="supermarket_sales.xlsx",
    engine="openpyxl",
    sheet_name="Sales",
    skiprows=3,
    usecols="B:R",
    nrows=1000,
)
# Add 'hour' column to dataframe
data["hour"] = pd.to_datetime(data["Time"], format="%H:%M:%S").dt.hour


# Get unique values of each filter
cities = list(data["City"].unique())
customer_types = list(data["Customer_type"].unique())
genders = list(data["Gender"].unique())


layout = {
    "xaxis": {"title": ""},
    "yaxis": {"title": ""},
    "margin": {"l": 150},
}


def on_filter(state):
    if (
        len(state.cities) == 0
        or len(state.customer_types) == 0
        or len(state.genders) == 0
    ):
        notify(state, "Error", "No results found. Check the filters.")
        return

    state.data_filtered, state.sales_by_product_line, state.sales_by_hour = filter(
        state.cities, state.customer_types, state.genders
    )


def filter(cities, customer_types, genders):
    data_filtered = data[
        data["City"].isin(cities)
        & data["Customer_type"].isin(customer_types)
        & data["Gender"].isin(genders)
    ]

    # Sales by product lime
    sales_by_product_line = (
        data_filtered[["Product line", "Total"]]
        .groupby(by=["Product line"])
        .sum()[["Total"]]
        .sort_values(by="Total")
    )
    sales_by_product_line["Product line"] = sales_by_product_line.index

    # Sales by hour
    sales_by_hour = (
        data_filtered[["hour", "Total"]].groupby(by=["hour"]).sum()[["Total"]]
    )
    sales_by_hour["hour"] = sales_by_hour.index

    return data_filtered, sales_by_product_line, sales_by_hour


def to_text(value):
    return "{:,}".format(int(value))


with tgb.Page() as page:
    tgb.toggle(theme=True)
    tgb.text("📊 Sales Dashboard", class_name="h1 text-center pb2")

    with tgb.layout("1 1 1", class_name="p1"):
        with tgb.part(class_name="card"):
            tgb.text("## Total Sales:", mode="md")
            tgb.text("US $ {to_text(data_filtered['Total'].sum())}", class_name="h4")

        with tgb.part(class_name="card"):
            tgb.text("## Average Sales:", mode="md")
            tgb.text("{to_text(data_filtered['Total'].mean())}", class_name="h4")

        with tgb.part(class_name="card"):
            tgb.text("## Average Rating:", mode="md")
            tgb.text(
                "{round(data_filtered['Rating'].mean(), 1)}"
                + "{'⭐' * int(round(round(data_filtered['Rating'].mean(), 1), 0))}",
                class_name="h4",
            )

    with tgb.layout("1 1 1", class_name="p1"):
        tgb.selector(
            value="{cities}",
            lov=cities,
            dropdown=True,
            multiple=True,
            label="Select cities",
            class_name="fullwidth",
            on_change=on_filter,
        )
        tgb.selector(
            value="{customer_types}",
            lov=customer_types,
            dropdown=True,
            multiple=True,
            label="Select customer types",
            class_name="fullwidth",
            on_change=on_filter,
        )
        tgb.selector(
            value="{genders}",
            lov=genders,
            dropdown=True,
            multiple=True,
            label="Select genders",
            class_name="fullwidth",
            on_change=on_filter,
        )

    with tgb.layout("1 1"):
        tgb.chart(
            "{sales_by_hour}",
            x="hour",
            y="Total",
            type="bar",
            title="Sales by Hour",
            layout=layout,
        )
        tgb.chart(
            "{sales_by_product_line}",
            x="Total",
            y="Product line",
            type="bar",
            orientation="h",
            layout=layout,
            title="Sales by Product Line",
        )

    with tgb.expandable(title="Filtered Data", expanded=False, class_name="mt1"):
        tgb.table("{data_filtered}")


if __name__ == "__main__":
    data_filtered, sales_by_product_line, sales_by_hour = filter(
        cities, customer_types, genders
    )
    Gui(page).run(
        title="Sales Dashboard",
        use_reloader=True,
        debug=True,
        watermark="",
        margin="4em",
    )
