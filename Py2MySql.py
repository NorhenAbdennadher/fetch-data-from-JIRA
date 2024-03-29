"""
File:           Py2MySql.py
Description:    Module for writing data to a MySql-server.
"""
import random
import datetime
from enum import Enum

from jira import Issue
from jira.client import ResultList, JIRA
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

import Jira2Py
from JiraIssue import JiraIssue
from JiraWP import JiraWP


class IssueType(Enum):
    OPEN = "open"
    PRECBB_NOT_ANALYSED = "preccb_not_analysed"
    POSTCBB_NOT_ANALYSED = "postccb_not_analysed"
    DEFECT = "defect"
    PR = "pr"
    CR = "cr"


def connect_database(db_server, db_user, db_password, db_port, db) -> sessionmaker:
    """
    initializes a connection to a mysql database and returns a session
    :param db_server: the database server
    :param db_user: username of database
    :param db_password: password of database-user
    :param db_port: the port of the MySQL server
    :param db: name of the database
    :return: database-session | None
    """
    try:
        engine = create_engine("mysql+pymysql://" + db_user + ":" + db_password
                               + "@" + db_server + ":" + db_port + "/" + db)
        engine.connect()
        factory = sessionmaker(bind=engine)
        session = factory()

    except Exception as e:
        print("Exception: ", e)
        return None

    return session


def _insert_jira_wp(session: sessionmaker, entry: JiraWP):
    """
    Inserts a new issue into the connected database
    :param session: the database-session, in which to insert
    :param entry: a JiraWP object to insert
    :return:
    """
    session.merge(entry)
    session.commit()


def _insert_jira_issues(session: sessionmaker, data: ResultList[Issue], is_type: IssueType):
    """
    Inserts all handed issues into the database.
    :param session: database session, to insert the data onto.
    :param data: ResultList with all data to load onto the database.
    :param is_type: the type of the issues (open | defect | not_analysed)
    :return:
    """

    DATE_LEN = 10

    for issue in data:
        formatted_resolution_date = None

        # format the resolution-date if available
        if issue.fields.resolutiondate is not None:
            formatted_resolution_date = issue.fields.resolutiondate[0:DATE_LEN]

        new_entry = JiraIssue(issue_id=issue.id,
                              creation_date=issue.fields.created[0:DATE_LEN],
                              resolution_date=formatted_resolution_date,
                              issue_type=is_type.value)
        session.add(new_entry)

    session.commit()


def insert_random_data(session: sessionmaker, base_defects: int, base_open: int, base_na: int,
                       start_date: datetime.date, num: int):
    """
    Generates multiple random values and inserts them into the database
    :param session: the database session, to insert the data into
    :param base_defects: base-value for work-product-defects
    :param base_open: base-value for open work-products
    :param base_na: base-value for not analysed work-products
    :param start_date: the start date for generating data
    :param num: number of values, which are generated
    :return:
    """

    step = datetime.timedelta(days=1)
    for i in range(num):
        # generate random numbers
        rand_wp_defects = base_defects + random.randint(-100, 100)
        rand_open_wp = base_open + random.randint(-100, 100)
        rand_not_analysed = base_na + random.randint(-50, 50)

        # save the random data in order to generate more continuous data
        base_defects = rand_wp_defects
        base_open = rand_open_wp
        base_na = rand_not_analysed

        # create a new entry of JiraWP
        new_entry = JiraWP(date=start_date,
                           wp_defects=rand_wp_defects,
                           wp_open=rand_open_wp,
                           wp_not_analysed=rand_not_analysed)

        _insert_jira_wp(session, new_entry)
        start_date += step


def insert_history_data(jira_connection: JIRA, session: sessionmaker,
                        start_date: datetime.date, end_date: datetime.date) -> bool:
    """
    Inserts all three KPIs for the given timespan into the database.
    :param jira_connection: jira-connection
    :param session: database session
    :param start_date: the begin-date of the timespan
    :param end_date: the end-date of the timespan
    :return: bool: whether the insertion was successful or not
    """

    # query for truncating jira_issue table
    del_query = text('TRUNCATE jira_issue')
                 
    # check if timespan is valid
    if start_date > end_date:
        # clear issue-table
        session.execute(del_query)

        print("Error: invalid timespan!")
        return False

    # fill the jira-issue table with data
    _insert_all_wps(jira_connection, session)

    step = datetime.timedelta(days=1)

    # count all issues for each day and insert them into the table
    while start_date <= end_date:
        # get the numbers of all KPIs for each day
        open_query = text(f"SELECT COUNT(*) FROM bp_jira_issue " 
                          f"WHERE CREATION_DATE <= '{start_date}' AND (RESOLUTION_DATE > '{start_date}'"
                          f"  OR RESOLUTION_DATE IS NULL) AND ISSUE_TYPE = '{IssueType.OPEN.value}'")
        num_open_wp = session.execute(open_query).scalar()

        defect_query = text(f"SELECT COUNT(*) FROM bp_jira_issue "
                            f"WHERE CREATION_DATE <= '{start_date}' AND (RESOLUTION_DATE > '{start_date}'"
                            f" OR RESOLUTION_DATE IS NULL) AND ISSUE_TYPE = '{IssueType.DEFECT.value}'")
        num_defect_wp = session.execute(defect_query).scalar()

        precbb_na_query = text(f"SELECT COUNT(*) FROM bp_jira_issue "
                               f"WHERE CREATION_DATE <= '{start_date}' AND (RESOLUTION_DATE > '{start_date}'"
                               f" OR RESOLUTION_DATE IS NULL) AND ISSUE_TYPE = '{IssueType.PRECBB_NOT_ANALYSED.value}'")
        num_preccb_na_wp = session.execute(precbb_na_query).scalar()

        postcbb_na_query = text(f"SELECT COUNT(*) FROM bp_jira_issue "
                                f"WHERE CREATION_DATE <= '{start_date}' AND (RESOLUTION_DATE > '{start_date}'"
                                f" OR RESOLUTION_DATE IS NULL) AND "
                                f"ISSUE_TYPE = '{IssueType.POSTCBB_NOT_ANALYSED.value}'")
        num_postccb_na_wp = session.execute(postcbb_na_query).scalar()

        pr_query = text(f"SELECT COUNT(*) FROM bp_jira_issue "
                        f"WHERE CREATION_DATE <= '{start_date}' AND (RESOLUTION_DATE > '{start_date}'"
                        f" OR RESOLUTION_DATE IS NULL) AND ISSUE_TYPE = '{IssueType.PR.value}'")
        num_pr_wp = session.execute(pr_query).scalar()

        cr_query = text(f"SELECT COUNT(*) FROM bp_jira_issue "
                        f"WHERE CREATION_DATE <= '{start_date}' AND (RESOLUTION_DATE > '{start_date}'"
                        f" OR RESOLUTION_DATE IS NULL) AND ISSUE_TYPE = '{IssueType.CR.value}'")
        num_cr_wp = session.execute(cr_query).scalar()

        entry = JiraWP(date=start_date,
                       wp_defects=num_defect_wp,
                       wp_open=num_open_wp,
                       wp_preccb_not_analysed=num_preccb_na_wp,
                       wp_postccb_not_analysed=num_postccb_na_wp,
                       wp_pr=num_pr_wp,
                       wp_cr=num_cr_wp)

        _insert_jira_wp(session, entry)
        start_date += step

    # delete the temporary data from the table
    session.execute(del_query)

    return True


def _insert_all_wps(connection: JIRA, session: sessionmaker):
    """
    Inserts all different issues from jira into the table 'jira_issue'
    :param connection: jira-connection
    :param session: database-session
    :return:
    """
    # extract data from the jira server
    open_wps = Jira2Py.get_open_wps(connection)
    defect_wps = Jira2Py.get_defect_wps(connection)
    precbb_na_wps = Jira2Py.get_pre_ccb_na_wps(connection)
    postcbb_na_wps = Jira2Py.get_post_ccb_na_wps(connection)
    pr_wps = Jira2Py.get_pr_wps(connection)
    cr_wps = Jira2Py.get_cr_wps(connection)

    _insert_jira_issues(session, open_wps, IssueType.OPEN)
    _insert_jira_issues(session, defect_wps, IssueType.DEFECT)
    _insert_jira_issues(session, precbb_na_wps, IssueType.PRECBB_NOT_ANALYSED)
    _insert_jira_issues(session, postcbb_na_wps, IssueType.POSTCBB_NOT_ANALYSED)
    _insert_jira_issues(session, pr_wps, IssueType.PR)
    _insert_jira_issues(session, cr_wps, IssueType.CR)