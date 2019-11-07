from flask import Flask, render_template, request, jsonify, Response
import requests
import datetime
import json
import logging
import sqlalchemy
import pymysql
import jinja2
#import sqlite3

app = Flask(__name__, template_folder='template')

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

_host = "127.0.0.1"
_port = 5002
_api_base = "/api"

db = sqlalchemy.create_engine(
    # Equivalent URL:
    # mysql+pymysql://<db_user>:<db_pass>@/<db_name>?unix_socket=/cloudsql/<cloud_sql_instance_name>
    sqlalchemy.engine.url.URL(
        drivername='mysql+pymysql',
        username="root",
        password="dbuserdbuser",
        database="colorpairs",
        query={
            'unix_socket': '/cloudsql/{}'.format("gridgame-257423:us-east1:gridgame")
        }
    )
)

# db = pymysql.connect(host='localhost',
#                      user='dbuser',
#                      password='dbuserdbuser',
#                      db='gridgame',
#                      charset='utf8mb4',
#                      cursorclass=pymysql.cursors.DictCursor)

pick_range = ['1', '20', '21', '40', '41', '70', '71', '100', '101', '130']

# create a database to store records
# connRecorddb = sqlite3.connect('record_db.sqlite', check_same_thread=False)
# curRecord = connRecorddb.cursor()
# curRecord.execute("create table"+" if not exists records (record integer);")
# connRecorddb.commit()

def handle_args(args):
  """

  :param args: The dictionary form of request.args.
  :return: The values removed from lists if they are in a list. This is flask weirdness.
      Sometimes x=y gets represented as {'x': ['y']} and this converts to {'x': 'y'}
  """
  result = {}

  if args is not None:
    for k, v in args.items():
      if type(v) == list:
        v = v[0]
      result[k] = v

  return result


def log_and_extract_input(method, path_params=None):
  path = request.path
  args = dict(request.args)
  data = None
  headers = dict(request.headers)
  method = request.method
  url = request.url
  base_url = request.base_url

  try:
    if request.data is not None:
      data = request.json
    else:
      data = None
  except Exception as e:
    # This would fail the request in a more real solution.
    data = "You sent something but I could not get JSON out of it."

  log_message = ": Method " + method

  # Get rid of the weird way that Flask sometimes handles query parameters.
  args = handle_args(args)

  inputs = {
    "path": path,
    "method": method,
    "path_params": path_params,
    "query_params": args,
    "headers": headers,
    "body": data,
    "url": url,
    "base_url": base_url
  }

  # Pull out the fields list as a separate element.
  if args and args.get('fields', None):
    fields = args.get('fields')
    fields = fields.split(",")
    del args['fields']
    inputs['fields'] = fields

  log_message += " received: \n" + json.dumps(inputs, indent=2)
  logger.debug(log_message)

  return inputs


def log_response(path, rsp):
  """

  :param path: The path parameter received.
  :param rsp: Response object
  :return:
  """
  msg = rsp
  logger.debug(str(datetime.now()) + ": \n" + str(rsp))


def generate_error(status_code, ex=None, msg=None):

  rsp = Response("Oops", status=500, content_type="text/plain")

  if status_code == 500:
    if msg is None:
      msg = "INTERNAL SERVER ERROR."

      rsp = Response(msg, status=status_code, content_type="text/plain")

  return rsp


@app.route('/', methods=['GET'])
def index():
  context = log_and_extract_input(index)
  # with db.connect() as conn:
  history_color = 0
  local_best = 0
  if request.method == 'GET':
    if context["query_params"]:
      correct_click = int(context["query_params"]["correct_click"])
      if "color" in context["query_params"].keys():
        history_color = context["query_params"]["color"]
      if "score" in context["query_params"].keys():
        local_best = context["query_params"]["score"]
    else:
      correct_click = 0

    # insert record into records db
    # curRecord.execute("insert into " + "records (record) values (" + str(local_best) + ");")
    # connRecorddb.commit()
    # curRecord.execute("select record "+"from records order by record desc limit 1;")
    # history_best = int(curRecord.fetchone()[0])

    if db:
      #cur = db.cursor()
      cur = db.connect()
      cur.execute("create "+"table if not exists records (record integer);")
      cur.execute("insert into " + "records (record) values (" + str(local_best) + ");")
      history_best = cur.execute("select record "+"from records order by record desc limit 1;").fetchall()
      if correct_click <= 4:
        # Execute the query and fetch all results
        res = cur.execute(
          "SELECT" + " * FROM " +
          "(select * from color where color.index> " + pick_range[0] +
          " and color.index<" + pick_range[1] + ") as a" +
          " ORDER BY RAND() LIMIT 2;"
        ).fetchall()
      elif 4 < correct_click <= 11:
        res = cur.execute(
          "SELECT" + " * FROM " +
          "(select * from color where color.index> " + pick_range[2] +
          " and color.index<" + pick_range[3] + ") as a" +
          " ORDER BY RAND() LIMIT 2;"
        ).fetchall()
      elif 11 < correct_click <= 17:
        res = cur.execute(
          "SELECT" + " * FROM " +
          "(select * from color where color.index> " + pick_range[4] +
          " and color.index<" + pick_range[5] + ") as a" +
          " ORDER BY RAND() LIMIT 2;"
        ).fetchall()
      elif 17 < correct_click <= 25:
        res = cur.execute(
          "SELECT" + " * FROM " +
          "(select * from color where color.index> " + pick_range[6] +
          " and color.index<" + pick_range[7] + ") as a" +
          " ORDER BY RAND() LIMIT 2;"
        ).fetchall()
      else:
        res = cur.execute(
          "SELECT" + " * FROM " +
          "(select * from color where color.index> " + pick_range[8] +
          " and color.index<" + pick_range[9] + ") as a" +
          " ORDER BY RAND() LIMIT 2;"
        ).fetchall()

      #random_color = cur.fetchall()
      random_color = res
      random_color1 = random_color[0]['deep']
      random_color2 = random_color[0]['light']
      random_color3 = random_color[1]['deep']
      random_color4 = random_color[1]['light']

      if history_color and random_color1[1:] == history_color and correct_click > 1:
        random_color1 = random_color3
        random_color2 = random_color4

    return render_template(
      'grid.html',
      random_color1=random_color1,
      random_color2=random_color2,
      random_color3=random_color3,
      random_color4=random_color4,
      history_best=history_best
    )
  # else:
  #   correct_click = context["body"]["correct_click"]
  #   result = {"result": correct_click}
  #   return result
