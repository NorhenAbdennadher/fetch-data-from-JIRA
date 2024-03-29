"""
File:           JiraQueries.py
Description:    Class for storing the JQL-queries.
"""


class JiraQueries:
    wp_defects_jql = ''

    wp_open_jql = ''

    wp_cr_jql = ''

    wp_pr_jql = ''

    wp_preccb_not_analysed_jql = ''

    wp_postccb_not_analysed_jql = ''

    def __init__(self, wp_defects_jql='', wp_open_jql='', wp_cr_jql='', wp_pr_jql='', wp_preccb_not_analysed_jql='',
                 wp_postccb_not_analysed_jql=''):
        """
        param-constructor
        :param wp_defects_jql: jira-query for wp-defects
        :param wp_open_jql: jira-query for open wps
        :param wp_cr_jql: jira-query for change-requests
        :param wp_pr_jql: jira-query for problem-reports
        :param wp_preccb_not_analysed_jql: jira-query for not analysed pre-ccb wps
        :param wp_postccb_not_analysed_jql: jira-query for not analysed post-ccb wps
        """
        self.wp_defects_jql = wp_defects_jql
        self.wp_open_jql = wp_open_jql
        self.wp_cr_jql = wp_cr_jql
        self.wp_pr_jql = wp_pr_jql
        self.wp_preccb_not_analysed_jql = wp_preccb_not_analysed_jql
        self.wp_postccb_not_analysed_jql = wp_postccb_not_analysed_jql