
import click

from rekorder import Player, What


@click.group()
@click.option('--debug/--no-debug', default=False)
@click.pass_context
def main(ctx, *args, **kwargs):
  ctx.obj = {}


@main.command()
@click.option(u'--input', required=True)
@click.pass_obj
def describe(obj, *args, **kwargs):

  click.echo("Describe [{input}]".format(**kwargs))

  player = Player(output='/dev/null',  mode=What.DESCRIBE, **kwargs)
  player.describe()


@main.command()
@click.option(u'--input', required=True)
@click.option(u'--output', required=True)
@click.pass_obj
def playback(obj, *args, **kwargs):

  click.echo("Replay [{input}] into [{output}]".format(**kwargs))

  player = Player(**kwargs)
  player.playback()
