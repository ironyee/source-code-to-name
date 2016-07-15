import click
from getpass import getpass

from codetoname.crawler import Crawler


@click.command()
@click.option('--number', default=1, help='number of pages')
def cli_crawler(number):
    account = input('Github account or email: ')
    password = getpass('Github password: ')

    try:
        client = Crawler(account=account, password=password)

        if number < 0:
            while client.next():
                pass
        else:
            for i in range(number):
                client.next()
    finally:
        client.close()
