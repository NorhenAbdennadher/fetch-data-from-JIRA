"""
File:           JiraWP.py
Description:    Mapping class for table 'jira_wp'.
"""

from sqlalchemy import Column, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mysql import MEDIUMINT

# base class
base = declarative_base()


class JiraWP(base):
    """ Derived class for ORM of the table 'jira_wp' """

    __tablename__ = "bp_jira_wp"
    date = Column(Date, primary_key=True, nullable=False)
    wp_defects = Column(MEDIUMINT, nullable=False, default=0)
    wp_open = Column(MEDIUMINT, nullable=False, default=0)
    wp_preccb_not_analysed = Column(MEDIUMINT, nullable=False, default=0)
    wp_postccb_not_analysed = Column(MEDIUMINT, nullable=False, default=0)
    wp_pr = Column(MEDIUMINT, nullable=False, default=0)
    wp_cr = Column(MEDIUMINT, nullable=False, default=0)

    def print(self):
        """
        Prints all members of the object in a formatted way.
        :return:
        """
        print("Date:", self.date, ", wp_defects:", self.wp_defects, ", wp_open:", self.wp_open,
              ", wp_preccb_not_analysed:", self.wp_preccb_not_analysed, ", wp_postccb_not_analysed:",
              self.wp_postccb_not_analysed, ", wp_pr:", self.wp_pr, ", wp_cr:", self.wp_cr)