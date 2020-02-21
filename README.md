# rekorder

Record and playback simple python CLI apps.

See [examples](examples).
Additional documentation forthcoming

## Release Process

  bumpversion
  git push origin  # bitbucket
  git checkout release
  git merge master --squash
  git push public master  # github
  git push public v$(cat version.txt)
  
