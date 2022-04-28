import configparser
import os


class GitRepository(object):
  """A git repository"""

  worktree = None
  gitdir = None
  conf = None

  def __init__(self, path, force=False) -> None:
      self.worktree=path
      self.gitdir=os.path.join(path,'.git')

      if not (force or os.path.isdir(self.gitdir)):
        raise Exception('Not a Git repository {0}'.format(path))

      self.conf = configparser.ConfigParser()
      cf = self.file(self, 'config')

      if cf and os.path.exists(cf):
        self.conf.read([cf])
      elif not force:
        raise Exception('Configuration file missing')

      if not force:
        vers = int(self.conf.get('core','repositoryformatversion'))
        if vers != 0:
          raise Exception('Unsupported repositoryformatversion {0}'.format(vers))

  @staticmethod
  def abs_path(repo, *path):
    """Compute path under repo's gitdir."""
    return os.path.join(repo.gitdir, *path)

  @staticmethod
  def file(repo, *path, mkdir=False):
    if GitRepository.directory(repo, *path[:-1], mkdir=mkdir):
      return GitRepository.abs_path(repo, *path)

  @staticmethod
  def directory(repo, *path, mkdir=False):

    path = GitRepository.abs_path(repo, *path)
    if os.path.exists(path):
      if os.path.isdir(path):
        return path
      else:
        raise Exception('Not a directory {0}'.format(path))

    if mkdir:
      os.makedirs(path)
      return path
    else:
      return None

  @staticmethod
  def create(path):
    """Create a new repository at path."""

    repo = GitRepository(path, True)

    if os.path.exists(repo.worktree):
      if not os.path.isdir(repo.worktree):
        raise Exception('{0} is not a directory!'.format(path))
      if os.listdir(repo.worktree):
        raise Exception('{0} is not empty'.format(path))
    else:
      os.makedirs(repo.worktree)

    assert(GitRepository.directory(repo, 'branches', mkdir=True))
    assert(GitRepository.directory(repo, 'objects', mkdir=True))
    assert(GitRepository.directory(repo, 'refs','tags', mkdir=True))
    assert(GitRepository.directory(repo, 'refs', 'heads',mkdir=True))

    with open(GitRepository.file(repo, 'description'), 'w') as f:
      f.write('Unnamed repository; edit this file descritpion to name the repository.\n')

    with open(GitRepository.file(repo, 'HEAD'),'w') as f:
      f.write('ref: refs/heads/master\n')

    with open(GitRepository.file(repo, 'config'),'w') as f:
      config = GitRepository.default_config()
      config.write(f)
    return repo

  @staticmethod
  def default_config():
    ret = configparser.ConfigParser()
    ret.add_section('core')
    ret.set("core", "repositoryformatversion", "0")
    ret.set("core", "filemode", "false")
    ret.set("core", "bare", "false")

    return ret

  @staticmethod
  def repo_find(path='.', required=True):
    path=os.path.realpath(path)

    if os.path.isdir(os.path.join(path, '.git')):
      return GitRepository(path)

    parent=os.path.realpath(os.path.join(path,'..'))

    if parent == path:
      # path = /
      if required:
        raise Exception('No git directory found')
      else:
        return None

    return GitRepository.repo_find(path=parent, required=required)

