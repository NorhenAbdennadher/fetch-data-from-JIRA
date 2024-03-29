"""
File:           main.py
Description:    Test-driver for reading data from a jira server
                and putting it on a MySql server.
"""
import datetime
import pandas as pd
import Jira2Py
import Py2MySql
from JiraQueries import JiraQueries
from tap import Tap
import configparser


class ArgumentParser(Tap):
    cred: str   # config-file for credentials


if __name__ == '__main__':
    # parse the path of the credential-file
    arg = ArgumentParser().parse_args()
    date=pd.to_datetime('today').date()
    # get configuration from config-files
    config_queries = configparser.ConfigParser()
    credentials = configparser.ConfigParser()
    config_queries.read('queries.ini')
    credentials.read(arg.cred)

    # establish connection to dummy-database
    session = Py2MySql.connect_database(credentials['database']['server'], credentials['database']['user'],
                                        credentials['database']['pwd'], credentials['database']['port'],
                                        credentials['database']['db'])

    # check if connection to dummy-database was successful
    if session is None:
        print("Error connecting to database!")
        raise SystemExit(1)

    queries = JiraQueries(wp_defects_jql=config_queries['jira_queries']['wp_defects'],
                          wp_open_jql=config_queries['jira_queries']['wp_open'],
                          wp_cr_jql=config_queries['jira_queries']['wp_cr'],
                          wp_pr_jql=config_queries['jira_queries']['wp_pr'],
                          wp_preccb_not_analysed_jql=config_queries['jira_queries']['wp_preccb_not_analysed'],
                          wp_postccb_not_analysed_jql=config_queries['jira_queries']['wp_postccb_not_analysed'])

    # create a connection to the jira server
    jira_connection = Jira2Py.connect_jira(
        credentials['jira_credentials']['server'],
        credentials['jira_credentials']['user'],
        credentials['jira_credentials']['pwd'],
        queries)

    # check if connection to jira-server was successful
    if jira_connection is None:
        print("Error connecting to jira-server!")
        raise SystemExit(1)

    # fill the jira-wp table for representation
    # with data from e.g. 2022-05-01 to 2023-01-01
    ret = Py2MySql.insert_history_data(jira_connection, session, datetime.date(2021, 5, 1), date)

    # check if insertion was successful
    if ret is False:
        raise SystemExit(1)