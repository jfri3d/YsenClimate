import inspect
import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv

from constants import INTERVAL

load_dotenv(dotenv_path='.envrc')

logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', level=logging.DEBUG)

scheduler = BlockingScheduler()


@scheduler.scheduled_job(CronTrigger(minute='0/{}'.format(INTERVAL), hour='6-9', day='*', month='*', day_of_week='*'))
def morning_trigger():
    func_name = inspect.stack()[0][3]

    logging.info('[{}] -> Starting Job'.format(func_name))

    # TODO -> do something here!
    pass

    logging.info("[{}] -> Done".format(func_name))


if __name__ == "__main__":
    scheduler.add_job(morning_trigger)
    scheduler.start()
