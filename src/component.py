'''
Template Component main class.

'''

import ast
import csv
import json
import logging
import sys

import boto3
from kbc.env_handler import KBCEnvHandler

# configuration variables
MAX_CHUNK_SIZE = 1000000
KEY_ACCESS_KEY_SECRET = '#access_key_secret'
KEY_ACCESS_KEY_ID = 'access_key_id'
KEY_REGION = 'region'

KEY_TABLE_NAME = 'table_name'
KEY_COLUMN_CONFIG = 'column_config'

MANDATORY_PARS = [KEY_ACCESS_KEY_ID, KEY_ACCESS_KEY_SECRET, KEY_COLUMN_CONFIG, KEY_REGION, KEY_TABLE_NAME]
MANDATORY_IMAGE_PARS = []

APP_VERSION = '0.0.1'


class Component(KBCEnvHandler):

    def __init__(self, debug=False):
        KBCEnvHandler.__init__(self, MANDATORY_PARS)
        # override debug from config
        if self.cfg_params.get('debug'):
            debug = True

        self.set_default_logger('DEBUG' if debug else 'INFO')
        logging.info('Running version %s', APP_VERSION)
        logging.info('Loading configuration...')

        try:
            self.validate_config()
            self.validate_image_parameters(MANDATORY_IMAGE_PARS)
        except ValueError as e:
            logging.error(e)
            exit(1)

        # create boto client

    def run(self):
        '''
        Main execution code
        '''
        params = self.cfg_params  # noqa

        # Create clients
        logging.info('Creating DynamoDB connection..')
        self.dynamodb = boto3.resource('dynamodb', region_name=params[KEY_REGION],
                                       aws_access_key_id=params[KEY_ACCESS_KEY_ID],
                                       aws_secret_access_key=params[KEY_ACCESS_KEY_SECRET])

        table_name = params[KEY_TABLE_NAME]
        logging.info(F'Fetching table "{table_name}" details')
        out_table = self.dynamodb.Table(table_name)

        in_tables = self.configuration.get_input_tables()

        if len(in_tables) == 0:
            logging.error('There is no table specified on the input mapping! You must provide one input table!')
            exit(1)

        in_table = in_tables[0]

        column_definiton = params[KEY_COLUMN_CONFIG]

        logging.info('Validating input...')
        self._validate_column_def(out_table, in_table, column_definiton)

        logging.info('Runing export...')
        self.send_data_batch(in_table, out_table, column_definiton)

        logging.info("Export finished")

    def _validate_column_def(self, out_table, in_table, column_definiton):
        pkeys = out_table.key_schema
        attr_defs = out_table.attribute_definitions
        table_manifest = self._get_table_manifest(in_table)

        cols = [col_def['name'] for col_def in column_definiton]

        # check for keys
        missing_keys = []
        for key in pkeys:
            key_name = key['AttributeName']
            if key_name not in cols:
                missing_keys.append(key_name)

        # check for attr defs
        missing_attrs = []
        for attr in attr_defs:
            att_name = attr['AttributeName']
            if att_name not in cols:
                missing_attrs.append(att_name)

        invalid_cols = []
        for col in cols:
            if col not in table_manifest['columns']:
                invalid_cols.append(col)

        err_msg = ''
        if missing_keys:
            err_msg += F'Some key attributes are missing in the column definition {missing_keys}\n'

        if missing_attrs:
            err_msg += F'Some schema attributes are missing in the column definition {missing_attrs}\n'

        if invalid_cols:
            err_msg += F'Some columns defined in the column definition ' \
                       F'are not valid (do not exist in the source table) {invalid_cols}\n'

        if err_msg != '':
            raise ValueError(err_msg)

    def send_data_batch(self, in_table, out_table, column_definiton):

        with open(in_table['full_path'], mode='r',
                  encoding='utf-8') as in_file, out_table.batch_writer() as batch_writer:
            reader = csv.DictReader(in_file, lineterminator='\n')

            for line in reader:
                item_ln = self._build_item(line, column_definiton)
                batch_writer.put_item(Item=item_ln)

        pass

    def _build_item(self, line, column_definiton):
        cols_types = {}
        for col_def in column_definiton:
            cols_types[col_def['name']] = col_def['type']

        for key in line:
            if cols_types[key] in ['set', 'object']:
                line[key] = ast.literal_eval(line[key])

        return line

    def _get_table_manifest(self, table):
        with open(table['full_path'] + '.manifest') as json_file:
            manifest = json.load(json_file)

        return manifest


"""
        Main entrypoint
"""
if __name__ == "__main__":
    if len(sys.argv) > 1:
        debug = sys.argv[1]
    else:
        debug = False
    comp = Component(debug)
    try:
        comp.run()
    except Exception as e:
        logging.exception(e)
        exit(1)
