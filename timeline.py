from datetime import datetime

import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import numpy as np
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
    label: str
    kind: str
    units: str
    """
    def __init__(self, lead_time_to_start, interval_duration,
                 intervals_per_submission, issue_frequency, value_type,
                 start, kind=None, label='left', units=''):

        self.lead_time_to_start = lead_time_to_start
        self.interval_duration = interval_duration
        self.intervals_per_submission = intervals_per_submission
        self.issue_frequency = issue_frequency
        self.duration = \
            pd.Timedelta(interval_duration) * intervals_per_submission
        self.value_type = value_type
        self.start = pd.Timestamp(start)
        # For left-labeling, forecast is exclusive of end.
        # end is the first instant that is not part of the Forecast.
        self.end = self.start + self.duration
        self.kind = kind
        # determined by corresponding observations, provided here for
        # convenience
        self.units = units

tz = 'UTC'
start = pd.Timestamp('20180101 1200')
end = pd.Timestamp('20180101 2100')
freq = '5min'
dates = pd.DatetimeIndex(start=start, end=end, freq=freq)

# levels = np.array([-5, 5, -3, 3, -1, 1])
fig, ax = plt.subplots(figsize=(10, 6))

start_end_delta = pd.Timedelta('5min')
ax.set_xlim(start - start_end_delta, end + start_end_delta)
ax.set_ylim(-1, 5)

# Create the base line
# start = datetime(2018, 1, 1, 12)
# end = datetime(2018, 1, 1, 16)
# ax.plot((start, end), (0, 0), 'k', alpha=.5)

run1 = Forecast(0, '15min', 12, '1h', 'any', '20180101 1200')
run2 = Forecast(0, '15min', 12, '1h', 'any', '20180101 1300')
run3 = Forecast(0, '15min', 12, '1h', 'any', '20180101 1400')
runs = [run1, run2, run3]

hour_ahead_15min_int = Forecast('1h', '15min', 4, '1h', 'any', '20180101 1300')
hour_ahead_15min_int.duration = pd.Timedelta('3h')
hour_ahead_15min_int.end = (hour_ahead_15min_int.start +
                            hour_ahead_15min_int.duration)

hour_ahead_hour_int = Forecast('2h', '1h', 3, '1h', 'any', '20180101 1400')

def draw_forecast_timeline(ax, y, forecast, **kwargs):
    ax.hlines(y, xmin=forecast.start, xmax=forecast.end, **kwargs)
    start_tick_y_length = .2
    ax.vlines(forecast.start, y - start_tick_y_length, y + start_tick_y_length,
              **kwargs)
    intervals = pd.DatetimeIndex(start=forecast.start, end=forecast.end,
                                 freq=forecast.interval_duration)
    ax.vlines(intervals[:-1], y - start_tick_y_length / 2,
              y + start_tick_y_length / 2, **kwargs)
    # last tick should be longer and dashed
    ax.vlines(intervals[-1], y - start_tick_y_length, y + start_tick_y_length,
              linestyles=(0, (1, 1)), **kwargs)
    # arrow_start = forecast.end
    # ax.arrow(forecast.start, y - start_tick_y_length, y + start_tick_y_length,
    #           **kwargs)

# Iterate through releases annotating each one
for ii, run in enumerate(runs):
    draw_forecast_timeline(ax, ii, run, color='g')

draw_forecast_timeline(ax, len(runs), hour_ahead_15min_int, color='b')

draw_forecast_timeline(ax, len(runs) + 1, hour_ahead_hour_int, color='r')


def annotate_with_brace(ax, xy, color):
    ax.annotate('$\}$', xy=xy, fontsize=64, textcoords='data',
                horizontalalignment='left', verticalalignment='bottom',
                rotation=90, color=color)


annotate_with_brace(ax, ('20180101 1300', 0), 'b')
annotate_with_brace(ax, ('20180101 1400', 1), 'b')
annotate_with_brace(ax, ('20180101 1500', 2), 'b')

annotate_with_brace(ax, ('20180101 1400', 0), 'r')
annotate_with_brace(ax, ('20180101 1500', 1), 'r')
annotate_with_brace(ax, ('20180101 1600', 2), 'r')

ax.annotate('$\}$', xy=('20180101 1730', 1), fontsize=90, textcoords='data',
            horizontalalignment='left', verticalalignment='center',
            color='g')
ax.annotate('Identically parsed\nforecast runs', xy=('20180101 1830', 1),
            fontsize=18, textcoords='data',
            horizontalalignment='left', verticalalignment='center',
            color='g')

ax.annotate('$\}$', xy=('20180101 1730', 3), fontsize=24, textcoords='data',
            horizontalalignment='left', verticalalignment='center',
            color='b')
ax.annotate('Forecast: merged\nseries of...', xy=('20180101 1830', 3),
            fontsize=18, textcoords='data',
            horizontalalignment='left', verticalalignment='center',
            color='b')

ax.annotate('$\}$', xy=('20180101 1730', 4), fontsize=24, textcoords='data',
            horizontalalignment='left', verticalalignment='center',
            color='r')
ax.annotate('Forecast: concatenated\nseries of...', xy=('20180101 1830', 4),
            fontsize=18, textcoords='data',
            horizontalalignment='left', verticalalignment='center',
            color='r')

ax.set(title="Forecast runs, Forecast concatenation, and Forecast merge")
# Set the xticks formatting
# format xaxis with 3 month intervals
ax.get_xaxis().set_major_locator(mdates.HourLocator(interval=1))
ax.get_xaxis().set_minor_locator(
    mdates.MinuteLocator(byminute=range(0, 60, 15)))
ax.get_xaxis().set_major_formatter(mdates.DateFormatter("%H:%M"))
fig.autofmt_xdate()

# Remove components for a cleaner look
plt.setp((ax.get_yticklabels() + ax.get_yticklines() +
          [v for k, v in ax.spines.items() if k != 'bottom']), visible=False)
plt.savefig('timeline.png')
