# rekorder

Record and playback simple python CLI apps.

See [examples](examples).
Additional documentation forthcoming

## Getting Started

Setup your development environment:

    ./dev-setup.sh

Run the examples:

    examples/ex001.py
    # ...
    examples/ex005.py

Playback the recordings:

    ./rekorder.sh playback --input ex001.json
    # ...
    ./rekorder.sh playback --input ex005.json

## File Format

The output file is a Cassette(RecordingMedium).
A Cassette is a list of Tracks.
A Track has a title and a list of Tunes.
A Tune has a Device, a collection of Notes and a Timestamp

Cassette - greatest-hits.json

    [
      a list of Tracks
    ]

Track

    {
      "index": 0-n,
      "title": "header|entry|etc...",
      "tunes": [
        list of Tunes
      ]
    }

Tune

    {
      "device": {
        "class": "a Device",
        "module": "python module containing the class"
      }
      "notes": {
        Notes that are specific to this Device
      }
      "timestamp": {
        "localtime": "human readable local time",
        "time": time.time()
      }
    }


## Release Process

    bumpversion ...
    git push origin  # bitbucket
    git checkout release
    git merge -X theirs --squash master
    git commit -m v$(cat version.txt)
    git push public release:master  # github
    git tag v$(cat version.txt)
    git push public v$(cat version.txt)
    git checkout master
    git push origin v$(cat version.txt)
