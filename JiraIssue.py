"""
File:           JiraIssue.py
Description:    Mapping class for table 'jira_issue'.
"""

from sqlalchemy import Column, Date, String, BigInteger
from sqlalchemy.ext.declarative import declarative_base

# base class
base = declarative_base()


class JiraIssue(base):
    """ Derived class for ORM of the table 'jira_issue' """

    __tablename__ = "bp_jira_issue"
    id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    issue_id = Column(String, nullable=False)
    creation_date = Column(Date, nullable=False)
    resolution_date = Column(Date)
    issue_type = Column(String, nullable=False)