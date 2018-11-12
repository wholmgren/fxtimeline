import matplotlib as mpl
mpl.use('agg')
mpl.rcParams['lines.linewidth'] = 3  # 1.5 default
mpl.rcParams['axes.linewidth'] = 1.6  # 0.8 default
mpl.rcParams['axes.titlesize'] = 'xx-large'  # large default
mpl.rcParams['xtick.major.size'] = 7  # 3.5 default
mpl.rcParams['xtick.minor.size'] = 4  # 2 default
mpl.rcParams['xtick.major.width'] = 1.6  # 0.8 default
mpl.rcParams['xtick.minor.width'] = 1.2  # 0.6 default
mpl.rcParams['xtick.labelsize'] = 'x-large'  # medium default
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd


class Forecast:
    """
    Constrains the definition of a forecast in the Solar Forecast Arbiter.

    Parameters
    ----------
    lead_time_to_start: str
        Time between submission time and the start of the forecast.
        e.g. '1h' for hour ahead forecast

    interval_duration: str
        Period time between successive values.
        e.g. '1h' for hour interval.

    intervals_per_submission: int
        Number of intervals per submission.
        e.g. 1 for hour interval, 1 hour total duration or 4 for 15 min
        interval, hour total duration.

    issue_frequency: str
        Length of time between new forecast submissions or runs.

    value_type: str
        'any', 'mean', '95th percentile', etc.

    start: parsable to pandas.Timestamp
        Absolute start time of forecast run or concatenated/merged forecast
        series.

    kind: str
        'run', 'concat', 'merge'

    label: str
        'left' or 'right'. Not currently supported.

    units: str
        The units of the forecast. Typically determined by corresponding
        observation.

    Attributes
    ----------
    lead_time_to_start: pandas.Timedelta
    interval_duration: pandas.Timedelta
    intervals_per_submission: int
    issue_frequency: pandas.Timedelta
    duration: pandas.Timedelta
        Equal to interval_duration * intervals_per_submission
    value_type: str
    start: pandas.Timestamp
        Inclusion/exclusion determined by label.
    end: pandas.Timestamp
        Equal to start + duration. Inclusion/exclusion determined by label.
    issue_time: pandas.Timestamp
        Equal to start - lead_time_to_start
    label: str
    kind: str
    units: str
    """
    def __init__(self, lead_time_to_start, interval_duration,
                 intervals_per_submission, issue_frequency, value_type,
                 start, kind=None, label='left', units=''):

        self.lead_time_to_start = pd.Timedelta(lead_time_to_start)
        self.interval_duration = pd.Timedelta(interval_duration)
        self.intervals_per_submission = intervals_per_submission
        self.issue_frequency = pd.Timedelta(issue_frequency)
        self.duration = \
            pd.Timedelta(interval_duration) * intervals_per_submission
        self.value_type = value_type
        self.start = pd.Timestamp(start)
        # For left-labeling, forecast is exclusive of end.
        # end is the first instant that is not part of the Forecast.
        self.end = self.start + self.duration
        self.issue_time = self.start - self.lead_time_to_start
        self.kind = kind
        # determined by corresponding observations, provided here for
        # convenience
        self.units = units


def draw_forecast_timeline(ax, y, forecast, start_tick_y_length=0.2,
                           interval_tick_y_length=0.125, show_lead_time=False,
                           show_last_tick=False, **kwargs):
    if show_lead_time:
        ax.hlines(y, xmin=forecast.issue_time, xmax=forecast.start,
                  linestyles=(0, (1, 1)), **kwargs)
        ax.vlines(forecast.issue_time, y - start_tick_y_length,
                  y + start_tick_y_length, linestyles=(0, (1, 1)), **kwargs)

    # main forecast line
    ax.hlines(y, xmin=forecast.start, xmax=forecast.end, **kwargs)
    # forecast start tick
    ax.vlines(forecast.start, y - start_tick_y_length, y + start_tick_y_length,
              **kwargs)
    # intervals ticks
    intervals = pd.DatetimeIndex(start=forecast.start, end=forecast.end,
                                 freq=forecast.interval_duration)
    ax.vlines(intervals[:-1], y - interval_tick_y_length,
              y + interval_tick_y_length, **kwargs)
    if show_last_tick:
        # last tick should be longer and dashed
        ax.vlines(intervals[-1], y - start_tick_y_length,
                  y + start_tick_y_length, linestyles=(0, (1, 1)), **kwargs)
    # arrow_start = forecast.end
    # ax.arrow(forecast.start, y - start_tick_y_length,
    #          y + start_tick_y_length, **kwargs)


def annotate_with_brace(ax, xy, color):
    ax.annotate(r'$\}$', xy=xy, fontsize=64, textcoords='data',
                horizontalalignment='left', verticalalignment='bottom',
                rotation=90, color=color)


def label_group(ax, label, x, y, color, bracesize=24, fontsize=18):
    ax.annotate(r'$\}$', xy=(x, y), fontsize=bracesize, textcoords='data',
                horizontalalignment='left', verticalalignment='center',
                color=color)
    ax.annotate(label, xy=(pd.Timestamp(x) + pd.Timedelta('60min'), y),
                fontsize=fontsize, textcoords='data',
                horizontalalignment='left', verticalalignment='center',
                color=color)


def format_xaxis(fig, ax):
    # Set the xticks formatting
    # format xaxis with 3 month intervals
    ax.get_xaxis().set_major_locator(mdates.HourLocator(interval=1))
    ax.get_xaxis().set_minor_locator(
        mdates.MinuteLocator(byminute=range(0, 60, 15)))
    ax.get_xaxis().set_major_formatter(mdates.DateFormatter("%H:%M"))
    fig.autofmt_xdate()


def remove_left_right_top_axes(ax):
    plt.setp((ax.get_yticklabels() + ax.get_yticklines() +
             [v for k, v in ax.spines.items() if k != 'bottom']),
             visible=False)


def initial_axes_setup():
    figsize = (10, 6)
    fig, ax = plt.subplots(figsize=figsize)

    # initial axes set up
    start = pd.Timestamp('20180101 1200')
    end = pd.Timestamp('20180101 2100')
    start_end_delta = pd.Timedelta('5min')
    ax.set_xlim(start - start_end_delta, end + start_end_delta)
    ax.set_ylim(-1, 5)
    return fig, ax


def make_concat_timeline():
    fig, ax = initial_axes_setup()

    # define forecast runs
    run1 = Forecast('1h', '15min', 4, '1h', 'any', '20180101 1300')
    run2 = Forecast('1h', '15min', 4, '1h', 'any', '20180101 1400')
    run3 = Forecast('1h', '15min', 4, '1h', 'any', '20180101 1500')
    runs = [run1, run2, run3]

    # define concat forecasts
    hour_ahead_15min_int = Forecast('1h', '15min', 12, '1h', 'any',
                                    '20180101 1300')

    # draw each run
    for ii, run in enumerate(runs):
        draw_forecast_timeline(ax, ii, run, color='g', show_lead_time=True)

    # draw concat forecast
    draw_forecast_timeline(ax, len(runs), hour_ahead_15min_int, color='b')

    # add the labels
    label_group(ax, 'Identically parsed\nforecast runs', '20180101 1730', 1,
                'g', bracesize=90)
    label_group(ax, 'A Forecast', '20180101 1730', 3, 'b')

    # format x axis, title, remove other axes
    format_xaxis(fig, ax)
    ax.set(title="Forecast runs concatenated into evaluation forecasts")
    remove_left_right_top_axes(ax)

    return fig


def make_concat_timeline_1h():
    fig, ax = initial_axes_setup()

    # define forecast runs
    run1 = Forecast('1h', '1h', 1, '1h', 'any', '20180101 1300')
    run2 = Forecast('1h', '1h', 1, '1h', 'any', '20180101 1400')
    run3 = Forecast('1h', '1h', 1, '1h', 'any', '20180101 1500')
    runs = [run1, run2, run3]

    # define concat forecasts
    hour_ahead_hour_int = Forecast('2h', '1h', 3, '1h', 'any', '20180101 1300')

    # draw each run
    for ii, run in enumerate(runs):
        draw_forecast_timeline(ax, ii, run, color='g', show_lead_time=True)

    # draw concat forecast
    draw_forecast_timeline(ax, len(runs), hour_ahead_hour_int, color='b')

    # add the labels
    label_group(ax, 'Identically parsed\nforecast runs', '20180101 1730', 1,
                'g', bracesize=90)
    label_group(ax, 'A Forecast', '20180101 1730', 3, 'b')

    # format x axis, title, remove other axes
    format_xaxis(fig, ax)
    ax.set(title="Forecast runs concatenated into evaluation forecasts")
    remove_left_right_top_axes(ax)

    return fig


def make_merged_timeline():
    fig, ax = initial_axes_setup()

    # define forecast runs
    run1 = Forecast(0, '15min', 12, '1h', 'any', '20180101 1200')
    run2 = Forecast(0, '15min', 12, '1h', 'any', '20180101 1300')
    run3 = Forecast(0, '15min', 12, '1h', 'any', '20180101 1400')
    runs = [run1, run2, run3]

    # define merged forecasts
    hour_ahead_15min_int = Forecast('1h', '15min', 4, '1h', 'any',
                                    '20180101 1300')
    hour_ahead_15min_int.duration = pd.Timedelta('3h')
    hour_ahead_15min_int.end = (hour_ahead_15min_int.start +
                                hour_ahead_15min_int.duration)

    hour_ahead_hour_int = Forecast('2h', '1h', 3, '1h', 'any', '20180101 1400')

    # draw each run
    for ii, run in enumerate(runs):
        draw_forecast_timeline(ax, ii, run, color='g')

    # draw the merged forecasts
    draw_forecast_timeline(ax, len(runs), hour_ahead_15min_int, color='b')
    draw_forecast_timeline(ax, len(runs) + 1, hour_ahead_hour_int, color='r')

    # indicate segments of runs for blue forecast
    annotate_with_brace(ax, ('20180101 1300', 0), 'b')
    annotate_with_brace(ax, ('20180101 1400', 1), 'b')
    annotate_with_brace(ax, ('20180101 1500', 2), 'b')

    # indicate segments of runs for red forecast
    annotate_with_brace(ax, ('20180101 1400', 0), 'r')
    annotate_with_brace(ax, ('20180101 1500', 1), 'r')
    annotate_with_brace(ax, ('20180101 1600', 2), 'r')

    # add the labels
    label_group(ax, 'Identically parsed\nforecast runs', '20180101 1730', 1,
                'g', bracesize=90)
    label_group(ax, 'A Forecast', '20180101 1730', 3, 'b')
    label_group(ax, 'A Forecast', '20180101 1730', 4, 'r')

    # format x axis, title, remove other axes
    format_xaxis(fig, ax)
    ax.set(title="Forecast runs merged into evaluation forecasts")
    remove_left_right_top_axes(ax)

    return fig


if __name__ == '__main__':
    fig = make_concat_timeline()
    fig.savefig('timeline_concat.svg')
    fig.savefig('timeline_concat.png')

    fig = make_concat_timeline_1h()
    fig.savefig('timeline_concat_1h.svg')
    fig.savefig('timeline_concat_1h.png')

    fig = make_merged_timeline()
    fig.savefig('timeline_merged.svg')
    fig.savefig('timeline_merged.png')
