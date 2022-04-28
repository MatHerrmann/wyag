import hashlib
import zlib

from git_repository import GitRepository


class GitObject(object):
  repo = None

  def __init__(self, repo, data=None) -> None:
      self.repo = repo

      if data != None:
        self.deserialize(data)

  # Create a bytestream from an object
  def serialize(self):
    """This function MUST be implemented by subclasse.

    It must read the object's contents from self.data, a byte string and do whatever it takes to convert it into meaningful representation.
    What exactly that means depends on each subclass"""
    raise Exception("Unimplemented")

  # Create an object from a bytestream
  def deserialize(self, data):
    raise Exception("Unimplemented")

  @staticmethod

  def read(repo, sha):

    path = GitRepository.file(repo, "objects", sha[0:2], sha[2:])

    with open(path, "rb") as f:
      raw = zlib.decompress(f.read())

      object_type_end_index=raw.find(b' ')
      object_type=raw[0:object_type_end_index]
      object_size_end_index=raw.find(b'\x00', object_type_end_index)
      object_size=int(raw[object_type_end_index:object_size_end_index].decode(encoding="ascii"))

      # Additional "-1" because the null byte follows after the object size
      if object_size != len(raw) - object_size_end_index - 1:
        raise Exception("Malformed object")

      if object_type==b'commit':
        c = GitCommit
      elif object_type==b'tree':
        c = GitTree
      elif object_type==b'tag':
        c = GitTag
      elif object_type==b'blob':
        c = GitBlob
      else:
        raise Exception("Unknown type {0} for object {1}".format(object_type.decode("ascii"), sha))

      return (c(repo, raw[object_size_end_index+1:]))

  @staticmethod
  def find(repo, name, fmt=None, follow=True):
    return name

  @staticmethod
  def write(obj, actually_write=True):
    data = obj.serialize()
    result = obj.fmt + b' ' + str(len(data)).encode() + b'\x00' + data
    sha = hashlib.sha1(result).hexdigest()

    if actually_write:
      path=GitRepository.file(obj.repo, "objects", sha[0:2], sha[2:], mkdir=actually_write)
      with open(path, 'wb') as f:
        f.write(zlib.compress(result))
    return sha

  @staticmethod
  def hash(fd, fmt, repo=None):
    data = fd.read()

    if fmt==b'commit':
      obj = GitCommit(repo, data)
    elif fmt==b'tree':
      obj = GitTree(repo, data)
    elif fmt==b'tag':
      obj = GitTag(repo, data)
    elif fmt==b'blob':
      obj = GitBlob(repo, data)
    else:
      raise Exception("Unknown type {0}".format(fmt))

    return GitObject.write(repo, obj)



class GitBlob(GitObject):
  fmt = b'blob'

  def serialize(self):
      return self.blobdata

  def deserialize(self, data):
      self.blobdata = data