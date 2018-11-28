import matplotlib as mpl
mpl.use('agg')
mpl.rcParams['lines.linewidth'] = 3  # 1.5 default
mpl.rcParams['axes.linewidth'] = 1.6  # 0.8 default
mpl.rcParams['axes.titlesize'] = 'xx-large'  # large default
mpl.rcParams['figure.titlesize'] = 'xx-large'  # large default
mpl.rcParams['xtick.major.size'] = 7  # 3.5 default
mpl.rcParams['xtick.minor.size'] = 4  # 2 default
mpl.rcParams['xtick.major.width'] = 1.6  # 0.8 default
mpl.rcParams['xtick.minor.width'] = 1.2  # 0.6 default
mpl.rcParams['xtick.labelsize'] = 'x-large'  # medium default
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.transforms as mtrans
from matplotlib.patches import PathPatch
from matplotlib.text import TextPath
import pandas as pd


# default parameters
FX_LABEL = 'Forecast\nEvalution\nTimeseries'
VALUE_TYPE = 'mean'
VARIABLE = 'Power'
SITE = 'Plant X'
VERTICAL_BRACESIZE = 100


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
                 start, kind=None, interval_label='left', units='',
                 variable=VARIABLE, site=SITE):

        self.lead_time_to_start = pd.Timedelta(lead_time_to_start)
        self.lead_time_to_start_str = lead_time_to_start
        self.interval_duration = pd.Timedelta(interval_duration)
        self.interval_duration_str = interval_duration
        self.intervals_per_submission = intervals_per_submission
        self.issue_frequency = pd.Timedelta(issue_frequency)
        self.issue_frequency_str = issue_frequency
        self.duration = \
            pd.Timedelta(interval_duration) * intervals_per_submission
        self.interval_label = interval_label
        self.value_type = value_type
        self.variable = variable
        self.site = site
        self.start = pd.Timestamp(start)
        self.start_str = start
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
                           show_last_tick=False, trailing_time=None, **kwargs):
    if show_lead_time:
        dashing = (2, 1)
        ax.hlines(y, xmin=forecast.issue_time, xmax=forecast.start,
                  linestyles=(0, dashing), **kwargs)
        ax.vlines(forecast.issue_time, y - start_tick_y_length,
                  y + start_tick_y_length, linestyles=(0.5, dashing), **kwargs)

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

    if trailing_time is not None:
        dashing = (2, 1)
        xmax = forecast.end + pd.Timedelta(trailing_time)
        ax.hlines(y, xmin=forecast.end, xmax=xmax,
                  linestyles=(0, dashing), **kwargs)
        # ax.vlines(forecast.end, y - start_tick_y_length,
        #           y + start_tick_y_length, linestyles=(0.5, dashing), **kwargs)
    # arrow_start = forecast.end
    # ax.arrow(forecast.start, y - start_tick_y_length,
    #          y + start_tick_y_length, **kwargs)


def curly(ax, x, y, scale, color):
    # adapted from
    # https://stackoverflow.com/questions/50039667/matplotlib-scale-text-curly-brackets
    # doesn't behave as expected
    tp = TextPath((0, 0), "}", size=.2)
    trans = mtrans.Affine2D().scale(1, scale) + \
        mtrans.Affine2D().translate(0.5, y/5) + ax.transAxes

    pp = PathPatch(tp, lw=0, fc=color, transform=trans)
    ax.add_artist(pp)


def annotate_with_brace(ax, xy, color):
    ax.annotate(r'$\}$', xy=xy, fontsize=74, textcoords='data',
                horizontalalignment='left', verticalalignment='bottom',
                rotation=90, color=color)


def label_group(ax, label, x, y, color, bracesize=None, fontsize=14):
    if bracesize:
        ax.annotate(r'$\}$', xy=(x, y), fontsize=bracesize, textcoords='data',
                    horizontalalignment='left', verticalalignment='center',
                    color=color)
    # xx = mdates.date2num(pd.Timestamp(x) - pd.Timedelta('6h'))
    # curly(ax, xx, y, 5, color)
    ax.annotate(label, xy=(pd.Timestamp(x) + pd.Timedelta('50min'), y),
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
    figsize = (12, 6.5)
    fig = plt.figure(figsize=figsize)
    ax = fig.add_axes([.06, .12, .73, .8])

    # initial axes set up
    start = pd.Timestamp('20180101 1200')
    end = pd.Timestamp('20180101 2100')
    start_end_delta = pd.Timedelta('5min')
    ax.set_xlim(start - start_end_delta, end + start_end_delta)
    ax.set_ylim(-1, 5)
    return fig, ax


def add_stats_table(ax, forecasts):
    """
    Parameters
    ----------
    ax: matplotlib.Axes
    forecasts: list of (color, Forecast) tuples
    """
    names = ['Lead time to start', 'Interval duration',
             'Intervals / sub.', 'Issue frequency', 'Interval label',
             'Value Type', 'Variable', 'Site'
             ]
    attrs = ['lead_time_to_start_str', 'interval_duration_str',
             'intervals_per_submission', 'issue_frequency_str',
             'interval_label', 'value_type', 'variable', 'site'
             ]

    xpos = .67
    ypos = .8
    kwargs = dict(horizontalalignment='left', verticalalignment='top',
                  transform=ax.figure.transFigure, fontsize=12,
                  linespacing=1.25)
    ax.text(xpos, ypos, '\n'.join(names), **kwargs)

    offset = 0.15
    spacing = 0.06

    for ii, (color, fx) in enumerate(forecasts):
        params = '\n'.join([str(getattr(fx, attr)) for attr in attrs])
        xx = xpos + offset + ii * spacing
        ax.text(xx, ypos, params, color=color, **kwargs)


def make_concat_timeline():
    fig, ax = initial_axes_setup()

    # define forecast runs
    run1 = Forecast('1h', '15min', 4, '1h', VALUE_TYPE, '20180101 1300')
    run2 = Forecast('1h', '15min', 4, '1h', VALUE_TYPE, '20180101 1400')
    run3 = Forecast('1h', '15min', 4, '1h', VALUE_TYPE, '20180101 1500')
    runs = [run1, run2, run3]

    # define concat forecasts
    hour_ahead_15min_int = Forecast('1h', '15min', 12, '1h', VALUE_TYPE,
                                    '20180101 1300')

    # draw each run
    for ii, run in enumerate(runs):
        draw_forecast_timeline(ax, ii, run, color='g', show_lead_time=True,
                               trailing_time='1h')

    # draw concat forecast
    draw_forecast_timeline(ax, len(runs), hour_ahead_15min_int, color='b')

    # indicate segments of runs for blue forecast
    # annotate_with_brace(ax, ('20180101 1300', 0), 'b')
    # annotate_with_brace(ax, ('20180101 1400', 1), 'b')
    # annotate_with_brace(ax, ('20180101 1500', 2), 'b')

    # add the labels
    label_time = '20180101 1700'
    label_group(ax, 'Identically parsed\nforecast runs', label_time, 1,
                'g', bracesize=VERTICAL_BRACESIZE)
    label_group(ax, FX_LABEL, label_time, 3, 'b')

    # format x axis, title, remove other axes
    format_xaxis(fig, ax)
    title = "Forecast runs concatenated into a forecast evaluation timeseries"
    ax.set(title=title)
    remove_left_right_top_axes(ax)

    add_stats_table(ax, (('g', run1), ('b', hour_ahead_15min_int),))

    return fig


def make_concat_timeline_1h():
    fig, ax = initial_axes_setup()

    # define forecast runs
    run1 = Forecast('1h', '1h', 1, '1h', VALUE_TYPE, '20180101 1300')
    run2 = Forecast('1h', '1h', 1, '1h', VALUE_TYPE, '20180101 1400')
    run3 = Forecast('1h', '1h', 1, '1h', VALUE_TYPE, '20180101 1500')
    runs = [run1, run2, run3]

    # define concat forecasts
    hour_ahead_hour_int = Forecast('1h', '1h', 3, '1h', VALUE_TYPE,
                                   '20180101 1300')

    # draw each run
    for ii, run in enumerate(runs):
        draw_forecast_timeline(ax, ii, run, color='g', show_lead_time=True)

    # draw concat forecast
    draw_forecast_timeline(ax, len(runs), hour_ahead_hour_int, color='b')

    # add the labels
    label_time = '20180101 1700'
    label_group(ax, 'Identically parsed\nforecast runs', label_time, 1,
                'g', bracesize=VERTICAL_BRACESIZE)
    label_group(ax, FX_LABEL, label_time, 3, 'b')

    # format x axis, title, remove other axes
    format_xaxis(fig, ax)
    title = "Forecast runs concatenated into a forecast evaluation timeseries"
    ax.set(title=title)
    remove_left_right_top_axes(ax)

    add_stats_table(ax, (('g', run1), ('b', hour_ahead_hour_int),))

    return fig


def make_merged_timeline():
    fig, ax = initial_axes_setup()

    # define forecast runs
    run1 = Forecast(0, '15min', 12, '1h', VALUE_TYPE, '20180101 1200')
    run2 = Forecast(0, '15min', 12, '1h', VALUE_TYPE, '20180101 1300')
    run3 = Forecast(0, '15min', 12, '1h', VALUE_TYPE, '20180101 1400')
    runs = [run1, run2, run3]

    # define merged forecasts
    hour_ahead_15min_int = Forecast('1h', '15min', 12, '1h', VALUE_TYPE,
                                    '20180101 1300')
    hour_ahead_15min_int.duration = pd.Timedelta('3h')
    hour_ahead_15min_int.end = (hour_ahead_15min_int.start +
                                hour_ahead_15min_int.duration)

    hour_ahead_hour_int = Forecast('2h', '1h', 3, '1h', VALUE_TYPE,
                                   '20180101 1400')

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
    label_time = '20180101 1700'
    label_group(ax, 'Identically parsed\nforecast runs', label_time, 1,
                'g', bracesize=VERTICAL_BRACESIZE)
    label_group(ax, FX_LABEL, label_time, 3, 'b')
    label_group(ax, FX_LABEL, label_time, 4, 'r')

    # format x axis, title, remove other axes
    format_xaxis(fig, ax)
    title = "Forecast runs merged into forecast evaluation timeseries"
    ax.set(title=title)
    remove_left_right_top_axes(ax)

    table_fxs = (('g', run1), ('b', hour_ahead_15min_int),
                 ('r', hour_ahead_hour_int))
    add_stats_table(ax, table_fxs)

    return fig


if __name__ == '__main__':
    dpi = 150
    fig = make_concat_timeline()
    fig.savefig('timeline_concat.svg')
    fig.savefig('timeline_concat.png', dpi=dpi)

    fig = make_concat_timeline_1h()
    fig.savefig('timeline_concat_1h.svg')
    fig.savefig('timeline_concat_1h.png', dpi=dpi)

    fig = make_merged_timeline()
    fig.savefig('timeline_merged.svg')
    fig.savefig('timeline_merged.png', dpi=dpi)
