r"""
One-stop shop for dealing with time.

## Description
You can use `cronos` in two different ways.  `cronos` exports a `Time` class:

```python
from cronos import Time
t = Time()  
```

It also exports several standalone functions:

```python
from cronos import epoch, local_time, sleep
s = epoch()
```
"""

import time, datetime

class Time():
    r"""
    Instantiate a cronos `Time` object.

    ## Usage
    
    ```python
    from cronos import Time
    t0 = Time()  # Current time
    t1 = Time(1590761574)  # Epoch seconds as integer
    t2 = Time(1590761573.598555)  # Epoch seconds as float
    t3 = Time("Fri May 29 09:12:53 2020")  # Time in ctime format
    t4 = Time("2019-12-05 16:50:06")  # ISO standard date and time
    t5 = Time(datetime.datetime.now())  # Pass a datetime.datetime object.
    ```

    ## Arguments
    - `value` : Optional time value.  If not specified, current date/time is used.  Can be epoch int or float, or various string representations.  If the value is not an int, float or string,  `Time()` tries to render it as str and then parse.  So value can be something like `datetime.datetime.now()`.
    - `fmt` : Specify an output format.  If none, `Time()` attempts to get from the passed in value. If all else fails, it uses ISO standard date and time i.e. "%Y-%m-%d %H:%M:%S".

    ## Formats

    Format strings use the following sytnax:
    
    | Code | Description                          | Example             |
    | :--- | :----------------------------------- | :----------------   |
    | %a   | Weekday, short version               | Wed                 |
    | %A   | Weekday, full version                | Wednesday           |
    | %w   | Weekday as a number 0-6, 0 is Sunday | 3                   |
    | %d   | Day of month 01-31                   | 31                  |
    | %b   | Month name, short version            | Dec                 |
    | %B   | Month name, full version             | December            |
    | %m   | Month as a number 01-12              | 12                  |
    | %y   | Year, short version, without century | 18                  |
    | %Y   | Year, full version                   | 2018                |
    | %H   | Hour 00-23                           | 17                  |
    | %I   | Hour 00-12                           | 5                   |
    | %p   | AM/PM                                | PM                  |
    | %M   | Minute 00-59                         | 41                  |
    | %S   | Second 00-59                         | 8                   |
    | %f   | Microsecond 000000-999999            | 548513              |
    | %z   | UTC offset                           | 100                 |
    | %Z   | Timezone                             | CST                 |
    | %j   | Day number of year 001-366           | 365                 |
    | %U   | Week number of year, base Sunday     | 52                  |
    | %W   | Week number of year, base Monday     | 52                  |
    | %c   | Local version of date and time       | Mon Dec 31 17:41:0  |
    | %x   | Local version of date                | 12/31/2018          |
    | %X   | Local version of time                | 17:41:00            |
    | %%   | A % character                        | %                   |

    ## Returns
    
    A `Time` object.  In string contexts, the time rendered using the specified `fmt` value. 

    """
    def __init__(self, value=None, fmt=None):
        if value is None: value = time.time()
        self.fmt = fmt
        if type(value) == int or type(value) == float: 
            t = time.localtime(value)
            self.d = datetime.datetime(t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)
        else:
            # Try to cast as string and parse.
            svalue = str(value)
            d = None
            r"""
            Code  Description                           Example
            ----  ------------------------------------  -----------------
            %a    Weekday, short version                Wed
            %A    Weekday, full version                 Wednesday
            %w    Weekday as a number 0-6, 0 is Sunday  3
            %d    Day of month 01-31                    31
            %b    Month name, short version             Dec
            %B    Month name, full version              December
            %m    Month as a number 01-12               12
            %y    Year, short version, without century  18
            %Y    Year, full version                    2018
            %H    Hour 00-23                            17
            %I    Hour 00-12                            5
            %p    AM/PM                                 PM
            %M    Minute 00-59                          41
            %S    Second 00-59                          8
            %f    Microsecond 000000-999999             548513
            %z    UTC offset                            100
            %Z    Timezone                              CST
            %j    Day number of year 001-366            365
            %U    Week number of year, Sunday as the    52
                    first day of week, 00-53
            %W    Week number of year, Monday as the    52
                    first day of week, 00-53
            %c    Local version of date and time        Mon Dec 31 17:41:0
            %x    Local version of date                 12/31/2018
            %X    Local version of time                 17:41:00
            %%    A % character                         %
            """
            formats = [
                r"%a %b %d %H:%M:%S %Y",   # Fri Jun 05 10:45:02 2020
                r"%a %b %e %H:%M:%S %Y",   # Fri Jun  5 10:45:02 2020
                r"%Y-%m-%d %H:%M:%S.%f",   # 2020-06-05 10:45:02.501236
                r"%Y-%m-%d %H:%M:%S",      # 2020-06-05 10:45:02
                r"%Y-%m-%d %H:%M",         # 2020-06-05 10:45
                r"%Y-%m-%dT%H:%M:%S.%f",   # 2020-06-05T10:45:02.501236
                r"%Y-%m-%dT%H:%M:%S",      # 2020-06-05T10:45:02
                r"%Y-%m-%dT%H:%M",         # 2020-06-05T10:45
                r"%Y-%m-%d %I:%M %p",      # 2020-06-05 10:45 AM
            ]
            match_found = False
            for fmt in formats:
                try: d = datetime.datetime.strptime(svalue, fmt)
                except: pass
                else: 
                    if self.fmt is None: self.fmt = fmt
                    match_found = True
                    break
            if not match_found: raise Exception("Could not parse date value \"{}\".".format(value))
            self.d = d
        if self.fmt is None or self.fmt.lower() == 'iso': self.fmt = r'%Y-%m-%d %H:%M:%S' #ISO standard date and time
    # Properties (with getters and setters).
    def get_year(self): return(self.d.year)
    def set_year(self, value): d = self.d; self.d = datetime.datetime(value, d.month, d.day, d.hour, d.minute, d.second)
    year = property(get_year, set_year)
    def get_month(self): return(self.d.month)
    def set_month(self, value): d = self.d; self.d = datetime.datetime(d.year, value, d.day, d.hour, d.minute, d.second)
    month = property(get_month, set_month)
    def get_day(self): return(self.d.day)
    def set_day(self, value): d = self.d; self.d = datetime.datetime(d.year, d.month, value, d.hour, d.minute, d.second)
    day = property(get_day, set_day)    
    def get_hours(self): return(self.d.hour)
    def set_hours(self, value): d = self.d; self.d = datetime.datetime(d.year, d.month, d.day, value, d.minute, d.second)
    hours = property(get_hours, set_hours)
    def get_minutes(self): return(self.d.minute)
    def set_minutes(self, value): d = self.d; self.d = datetime.datetime(d.year, d.month, d.day, d.hour, value, d.second)
    minutes = property(get_minutes, set_minutes)
    def get_seconds(self): return(self.d.second)
    def set_seconds(self, value): d = self.d; self.d = datetime.datetime(d.year, d.month, d.day, d.hour, d.minute, value)
    seconds = property(get_seconds, set_seconds)
    def set_time(self, hour, minute, second): d = self.d; self.d = datetime.datetime(d.year, d.month, d.day, hour, minute, second)
    def set_date(self, year, month, day): d = self.d; self.d = datetime.datetime(year, month, day, d.hour, d.minute, d.second)
    # Renderers.
    def datetime_object(self): return self.d
    def to_epoch(self, cast=float): return(cast(self.d.timestamp()))
    epoch = to_epoch
    def iso(self): return(self.d.strftime('%Y-%m-%d %H:%M:%S'))
    def iso_long(self): return(self.d.strftime('%Y-%m-%d %H:%M:%S'))
    def iso_short(self): return(self.d.strftime('%Y-%m-%d %H:%M'))
    def iso_date(self): return(self.d.strftime('%Y-%m-%d'))
    def ansi_ctime_asctime(self): return(self.d.strftime(r'%a %b %e %H:%M:%S %Y'))
    ansi = ansi_ctime_asctime
    def __repr__(self): return(self.d.strftime(self.fmt))
    def julian_date(self):
        fmt='%Y-%m-%d'
        d = datetime.datetime.strptime(self.iso_date(), fmt)
        d = d.timetuple()
        return(d.tm_yday)
    __str__ = __repr__
    @staticmethod
    def rand(start, end=None):
        r"""
        Return a random Time object.
        
        ## Usage
        ```python
        from cronos import Time
        t = Time.rand()
        ```

        ## Arguments
        - `start`: start date/time
        - `stop`: stop date/time (optional; if not specified, current time is used)

        ## Returns
        Time object.
        """
        import random
        min = Time(start).epoch()
        max = Time(end).epoch()
        return Time(random.randint(min, max))
   

def epoch(cast=None, fmt=None): 
    r"""
    Get seconds since epoch.

    ## Usage
    ```python
    import cronos
    # Print epoch time as float:
    print(cronos.epoch())
    >>> 1590761573.598555
    # Print epoch time as int:
    print(cronos.epoch(int))
    >>> 1590761574
    # Print epoch time as hexadecimal string.
    print(cronos.epoch(int, "0x{0:X}"))
    >>> 0x5ED11866
    ```
    
    ## Arguments
    - `cast` : cast result using function e.g. int, str
    - `fmt` : format e.g. fmt="0x{0:X}" returns hex i.e. 0x5DE92104

    ## Returns
    Seconds since epoch as a float, subject to any modifications applied by `cast` or `format`.
    """
    s = time.time()
    if cast is not None: s = cast(s)
    if fmt is not None: s = fmt.format(s)
    return(s)

def local_time(epoch=None):
    r"""
    Return local time string (via `time.ctime()` e.g. "Thu Dec 27 15:49:29 2018").
    
    ## Usage
    ```python
    import cronos
    print(cronos.local_time())
    >>> Fri May 29 09:12:53 2020
    print(cronos.local_time(1590761574))
    >>> Fri May 29 09:12:53 2020
    ```

    ## Arguments
    - `epoch`: seconds since epoch (if not specified, current time is used)
    """
    if epoch is None: epoch = time.time()
    return(time.ctime(epoch))

def sleep(seconds):
    r"""
    Pause program execution for specified number of seconds.
    
    ## Usage
    ```
    from cronos import sleep
    sleep(2)
    ```

    ## Arguments
    - `seconds`: number of seconds to pause

    ## Returns
    Nothing
    """
    time.sleep(seconds)


