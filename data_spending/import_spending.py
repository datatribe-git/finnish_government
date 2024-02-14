import copy
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from pathlib import Path


def import_spending(f: str | Path) -> pd.DataFrame:
    """Import the raw data from CSV.
    Sets index to the category G codes."""

    na_values = ['...', ' ...']
    df = pd.read_csv(f,
                     sep=',',
                     comment='#',
                     header=0,
                     na_values=na_values)

    # Separate category-code and function description.
    code = [ s.split(maxsplit=1)[0] for s in df['Function'] ]
    name = [ s.split(maxsplit=1)[1] for s in df['Function'] ]

    df = df.assign(code=code)
    df.set_index(df['code'], inplace=True)
    df.drop(['code'], axis=1, inplace=True)
    df['Function'] = name

    return df


def transform_melt(data: pd.DataFrame, value_name: str) -> pd.DataFrame:
    """Melt the array to have all years in single column."""

    df = copy.copy(data)

    # Set years as int-type.
    df.columns = df.columns.str[:4].astype('int')

    df = df.assign(code=df.index)
    # df.set_index(np.arange(len(df)))

    res = df.melt(value_vars=df.columns,
                  id_vars='code',
                  var_name='year',
                  value_name=value_name)

    # Melt changes var_name type to 'str', have to change it back.
    res['year'] = res['year'].astype('int')

    return res


def get_spending_melted(data: pd.DataFrame) -> pd.DataFrame:
    """Transform the data into seaborne-friendly format."""

    mil_mask = data.columns.str.contains('million')
    bkt_mask = data.columns.str.contains('gdp')
    per_capita_mask = data.columns.str.contains('per_cap')
    # breakpoint()

    mil = transform_melt(data[data.columns[mil_mask]],
                         value_name='million')
    bkt = transform_melt(data[data.columns[bkt_mask]],
                         value_name='gdp_percent')
    capita = transform_melt(data[data.columns[per_capita_mask]],
                         value_name='per_capita')
    # breakpoint()

    data_melted = pd.merge(mil,
                           bkt.drop(['code', 'year'], axis=1),
                           left_index=True,
                           right_index=True)
    # breakpoint()
    data_melted = pd.merge(data_melted,
                           capita.drop(['code', 'year'], axis=1),
                           left_index=True,
                           right_index=True)
    # breakpoint()

    return data_melted


def plot(data: pd.DataFrame, 
         categories: list[str],
         labels: list[str]) -> None:
    """Basic plot of spending data as absolute
    values and as percent of GDP."""

    plot_mask = data['code'].isin(categories)
    plot_data = data[plot_mask]

    sns.set_theme()
    fig = plt.figure(figsize=(7,8))
    ax1, ax2 = fig.subplots(2, 1)

    plot_1a = sns.scatterplot(data=plot_data,
                              x='year',
                              y='million',
                              hue='code',
                              ax=ax1,
                              legend=True)

    plot_1b = sns.lineplot(data=plot_data,
                           x='year',
                           y='million',
                           hue='code',
                           ax=ax1,
                           legend=True)

    plot_2a = sns.scatterplot(data=plot_data,
                              x='year',
                              y='gdp_percent',
                              hue='code',
                              ax=ax2,
                              legend=False)

    plot_2b = sns.lineplot(data=plot_data,
                           x='year',
                           y='gdp_percent',
                           hue='code',
                           ax=ax2,
                           legend=False)

    ax1.set_xlabel(None)
    ax1.set_ylabel("Million €")
    ax2.set_ylabel("% of GDP")

    artists, _ = plot_1a.get_legend_handles_labels()
    ax1.legend(artists, labels,
               loc='upper left',
               bbox_to_anchor=(-0.15, 1.38),
               ncols=3)

    fig.subplots_adjust(left=0.125, bottom=0.067, right=0.90,
                        top=0.865,  wspace=0.2, hspace=0.116)


if __name__ == "__main__":
    spending = import_spending('government_spending_1990-2022.csv') 
    spending_alt = get_spending_melted(spending)

    # Codes for the major spending categories.
    main_categories = ['G01', 'G02', 'G03', 'G04', 'G05',
                       'G06', 'G07', 'G08', 'G09', 'G10']
    main_labels = spending.loc[main_categories, 'Function']
    # plot(spending_melted, main_categories, main_labels)

