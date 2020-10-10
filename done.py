import shared
import done_file
import done_db
import done_domain
import click
from typing import List
from functools import partial
from datetime import datetime


# save = partial(done_file.save, done_file.PATH)
# get = partial(done_file.get, done_file.PATH)

save = partial(done_db.save, done_db.PATH)
get = partial(done_db.get, done_db.PATH)


def save_from_string(items: List[str]):
    save([done_domain.create_default(item) for item in items])


@click.group()
def cli(): pass

@cli.command(name='a')
@click.argument('completed_item', type=str)
def save_cli(completed_item: str):
    save_from_string([completed_item])

@cli.command(name='d')
@click.argument('number_of_days_ago', type=int)
def get_by_days(number_of_days_ago):
    completed_since = done_domain.days_ago(datetime.now(), number_of_days_ago)
    shared.display(get(completed_since))

@cli.command(name='w')
@click.argument('number_of_weeks_ago', type=int)
def get_by_weeks(number_of_weeks_ago):
    completed_since = done_domain.weeks_ago(datetime.now(), number_of_weeks_ago)
    shared.display(get(completed_since))


if __name__ == "__main__":
    cli()
