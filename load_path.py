#!/usr/bin/env python
# coding:utf-8
"""load_path.py"""

# import argparse
import logging
import pickle

# def set_argparse():
#     """Set the args&argv for command line mode"""
#     parser = argparse.ArgumentParser()
#     parser.add_argument(
#         "file", type=str, default="", help="input schedule file")
#     parser.add_argument(
#         "--duration", "-d", type=int, default=60, help="input schedule file")
#     return parser.parse_args()


def get_logger(logname: str):
  """Config the logger in the module
    Arguments:
        logname {str} -- logger name
    Returns:
        logging.Logger -- the logger object
    """
  logger = logging.getLogger(logname)
  formater = logging.Formatter(
      fmt='%(asctime)s - %(filename)s : %(levelname)-5s :: %(message)s',
      # filename='./log.log',
      # filemode='a',
      datefmt='%m/%d/%Y %H:%M:%S')
  stream_hdlr = logging.StreamHandler()
  stream_hdlr.setFormatter(formater)
  logger.addHandler(stream_hdlr)
  logger.setLevel(logging.DEBUG)
  return logger


__logger__ = get_logger('load_path')
global all_paths
global paths_in_file
global independent_paths


def load_file(filename):
  global all_paths
  global paths_in_file
  global independent_paths
  with open(filename, 'rb') as fp:
    all_paths = pickle.load(fp)
  print("Load paths sum: %d" % len(all_paths))
  for path in all_paths:
    if path not in independent_paths:
      independent_paths.append(path)
  print("Independent paths sum: %d" % len(independent_paths))


def load_multiple_files(start_id: int, end_id: int):
  global all_paths
  global paths_in_file
  global independent_paths
  for index in range(start_id, end_id + 1):
    filename = "wuhanpath" + str(index) + ".txt"
    # print(filename)
    with open(filename, "rb") as fp:
      paths_in_file = pickle.load(fp)
      all_paths = all_paths + paths_in_file
  print("Load paths sum: %d" % len(all_paths))
  for path in all_paths:
    if path not in independent_paths:
      independent_paths.append(path)
  print("Independent paths sum: %d" % len(independent_paths))


def save_independent_paths(filename):
  global independent_paths
  print("Save independent paths to: %s" % filename)
  with open(filename, 'wb') as fp:
    pickle.dump(independent_paths, fp)


def clear_paths():
  global all_paths
  global paths_in_file
  global independent_paths
  all_paths = []
  paths_in_file = []
  independent_paths = []


def save_as_text(filename):
  global all_paths
  with open(filename, 'w') as fp:
    for path in all_paths:
      fp.write(str(path) + '\n')


def main():
  """Main function"""
  __logger__.info('Process start!')
  # load_multiple_files(1, 20)
  load_file("path/wuhan_small_paths.txt")
  # save_independent_paths("all.txt")
  save_as_text("path/wuhan_small_paths_text.txt")
  clear_paths()


if __name__ == '__main__':
  # Uncomment the next line to read args from cmd-line
  # ARGS = set_argparse()
  clear_paths()
  main()
