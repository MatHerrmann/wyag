import argparse
import sys
from git_repository import GitRepository
from git_object import GitObject

arg_parser=argparse.ArgumentParser(description='The stupid content tracker')
arg_sub_parser = arg_parser.add_subparsers(title='Commands', dest='command')
arg_sub_parser.required=True
argsp=arg_sub_parser.add_parser('init', help='Initialize a new, empty repository.')
argsp.add_argument('path', metavar='directory', nargs='?', default='.', help='Where to create the repository.')
argsp=arg_sub_parser.add_parser('cat-file', help="Provide content of a repository object")
argsp.add_argument("type", metavar="type", choices=["blob","commit","tree","tag"], help="Specify the type")
argsp.add_argument("object", metavar="object", help="The object to display")
argsp=arg_sub_parser.add_parser('hash-object', help="Calculate object ID and optionally creates a blob from a file")
argsp.add_argument("-t", metavar="type", dest="type", choices=["blob","commit","tree","tag"], help="Specify the type", default="blob")
argsp.add_argument("-w", dest="write", action="store_true", help="Actually write the object into the database")
argsp.add_argument("path", help="Read object from <file>")

def main(argv=sys.argv[1:]):
  args = arg_parser.parse_args(argv)
  # if args.command == 'add':
  #   cmd_add(args)
  # elif args.command == 'commit':
  #   cmd_commit(args)
  # elif args.command == 'log':
  #   cmd_log(args)
  if args.command == 'init':
    cmd_init(args)
  elif args.command == 'cat-file':
    cmd_cat_file(args)
  elif args.command == 'hash-object':
    cmd_hash_object(args)

def cmd_init(args):
  GitRepository.create(args.path)

def cmd_cat_file(args):
  repo = GitRepository.find()
  cat_file(repo, args.object, fmt=args.type.encode())

def cat_file(repo, obj, fmt=None):
  obj = GitObject.read(repo, GitObject.find(repo, obj, fmt=fmt))
  sys.stdout.buffer.write(obj.serialize())

def cmd_hash_object(args):
  if args.write:
    repo = GitRepository(".")
  else:
    repo = None

  with open(args.path, "rb") as fd:
    sha = GitObject.hash(fd, args.type.encode(), repo)
    print (sha)
