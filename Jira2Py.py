"""
File:           Jira2Py.py
Description:    Module for fetching data from a jira server
                into python.
"""


from jira import JIRA, Issue

# disable 'InsecureRequestWarning' (we know the server we are working with)
from jira.client import ResultList
from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings

from JiraQueries import JiraQueries
from JiraWP import JiraWP
from datetime import date

disable_warnings(InsecureRequestWarning)

# variable for storing the jql-queries
jira_queries = JiraQueries()


def connect_jira(jira_server, jira_user, jira_password, queries: JiraQueries) -> JIRA:
    """
    Function to create a connection to a jira-server with credentials
    :param jira_server: url of the jira-server
    :param jira_user: username
    :param jira_password: password of the jira-user
    :param queries: jql-queries for extracting the data
    :return: JIRA | None
    """
    try:
        print("Connecting to JIRA: %s" % jira_server)
        jira_options = {'server': jira_server, 'verify': False}
        jira_connection = JIRA(options=jira_options, basic_auth=(jira_user, jira_password))

    except Exception as e:
        print("Failed to connect to JIRA: %s" % jira_server)
        print('Exception: ', e)
        return None

    # set the queries
    global jira_queries
    jira_queries = queries

    print("Connection successful!")
    return jira_connection


def _get_num_of_issues(connection: JIRA, jql: str) -> int:
    """
    Sends a request to the taken jira-connection, in order to get the number of issues found.
    :param: connection: jira-connection
    :param: JQL: the query to determine the issues found
    :return: int: number of all found issues
    """

    result = connection.search_issues(jql,
                                      startAt=0,
                                      maxResults=0,
                                      json_result=True)

    # return the 'total' number of issues found
    return result.get("total")


def get_open_wps(connection: JIRA) -> ResultList[Issue]:
    """
    Returns all open workproduct issues.
    :param connection: jira-connection
    :return:  ResultList[Issue]
    """
    return connection.search_issues(jira_queries.wp_open_jql, maxResults=False, fields=["key", "created", "resolutiondate"])


def get_cr_wps(connection: JIRA) -> ResultList[Issue]:
    """
    Returns all cangerequest workproduct issues.
    :param connection: jira-connection
    :return:  ResultList[Issue]
    """
    return connection.search_issues(jira_queries.wp_cr_jql, maxResults=False, fields=["key", "created", "resolutiondate"])


def get_pr_wps(connection: JIRA) -> ResultList[Issue]:
    """
    Returns all problemreport workproduct issues.
    :param connection: jira-connection
    :return:  ResultList[Issue]
    """
    return connection.search_issues(jira_queries.wp_pr_jql, maxResults=False, fields=["key", "created", "resolutiondate"])


def get_pre_ccb_na_wps(connection: JIRA) -> ResultList[Issue]:
    """
    Returns a list of all workproducts, which are not analysed and pre-ccb.
    :param connection: jira-connection
    :return: ResultList[Issue]
    """
    return connection.search_issues(jira_queries.wp_preccb_not_analysed_jql, maxResults=False, fields=["key", "created", "resolutiondate"])


def get_post_ccb_na_wps(connection: JIRA) -> ResultList[Issue]:
    """
    Returns a list of all workproducts, which are not analysed and post-ccb.
    :param connection: jira-connection
    :return: ResultList[Issue]
    """
    return connection.search_issues(jira_queries.wp_postccb_not_analysed_jql, maxResults=False, fields=["key", "created", "resolutiondate"])


def get_defect_wps(connection: JIRA) -> ResultList[Issue]:
    """
    Returns a list of all workproduct defects.
    :param connection: jira-connection
    :return: ResultList[Issue]
    """
    return connection.search_issues(jira_queries.wp_defects_jql, maxResults=False, fields=["key", "created", "resolutiondate"])


def get_current_data(connection: JIRA) -> JiraWP:
    """
    Sends different JQLs to the jira-server, in order to determine the current total numbers
    of all workproduct defects, open CRs/PRs, not analysed workproducts.
    :param: connection: the connection to the jira-server, where to send the requests to
    :return: a JiraWP object with all data
    """

    # get the number of current issues
    num_defects = _get_num_of_issues(connection, jira_queries.wp_defects_jql)
    num_open = _get_num_of_issues(connection, jira_queries.wp_open_jql)
    num_preccb_not_analysed = _get_num_of_issues(connection, jira_queries.wp_preccb_not_analysed_jql)
    num_postccb_not_analysed = _get_num_of_issues(connection, jira_queries.wp_postccb_not_analysed_jql)
    num_pr = _get_num_of_issues(connection, jira_queries.wp_pr_jql)
    num_cr = _get_num_of_issues(connection, jira_queries.wp_cr_jql)

    return JiraWP(date=date.today(),
                  wp_defects=num_defects,
                  wp_open=num_open,
                  wp_preccb_not_analysed=num_preccb_not_analysed,
                  wp_postccb_not_analysed=num_postccb_not_analysed,
                  wp_pr=num_pr,
                  wp_cr=num_cr)