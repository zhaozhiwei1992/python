import datetime
from datetime import date


def is_workday(day=None):
    """
        Args:
            day: 日期, 默认为今日

        Returns:
            True: 上班
            False: 放假
    """
    # 如果不传入参数则为今天
    today = date.today()
    # logger.info(today)
    day = day or today

    week_day = date.weekday(day) + 1  # 今天星期几(星期一 = 1，周日 = 7)
    is_work_day_in_week = week_day in range(1, 6)  # 这周是不是非周末，正常工作日, 不考虑调假

    if is_work_day_in_week:
        return True
    else:
        return False


if __name__ == '__main__':
    print("今天是不是工作日: ", is_workday())
