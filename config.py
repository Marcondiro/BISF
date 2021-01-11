START = '2018-10-01'
END = '2020-10-01'
STOCKS = [
    {
        'ticker': 'TSM',
        'label': 'Taiwan Semiconductor',
        'sector': 'Technology',
        'color': 'DarkSlateGray',
    },
    {
        'ticker': 'NVDA',
        'label': 'Nvidia',
        'sector': 'Technology',
        'color': 'DarkGreen',
    },
    {
        'ticker': 'BA',
        'label': 'Boeing',
        'sector': 'Industrials',
        'color': 'DarkBlue',
    },
    {
        'ticker': 'LUV',
        'label': 'Southwest Airlines',
        'sector': 'Industrials',
        'color': 'DarkOrange',
    },
    {
        'ticker': 'PFE',
        'label': 'Pfizer',
        'sector': 'Healthcare',
        'color': 'DodgerBlue',
    },
    {
        'ticker': 'BMY',
        'label': 'Bristol-Myers Squibb',
        'sector': 'Healthcare',
        'color': 'DeepPink',
    }
]
PREDICTION_PERIODS = {
    'N': '2009-02-01',  # 80 mesi
    'M': '2017-06-01',  # 30 mesi
    'L': '2019-12-01',  # 10 mesi
}

PREDICTION_LIMIT_SECONDS = 5

DEBUG = True #TODO turn off debug