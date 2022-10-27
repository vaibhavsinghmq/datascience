#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 18 18:46:20 2022

@author: vaibhavsingh
"""

import logging

from datetime import datetime
from datetime import timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from airflow.operators.email_operator import EmailOperator
from airflow.contrib.operators.bigquery_operator import BigQueryOperator


# These args will get passed on to each operator
# You can override them on a per-task basis during operator initialization
default_args = {
    'owner':'airflow',
    'depends_on_past':False, # does this dag depend on the previous run of the dag, in our case false
    'email':['vaibhav.singh@students.mq.edu.au'], #Receipient mail during failure
    'email_on_failure':True, # should we send emails on failure?
    'email_on_retry':True,# should we send an email in case of retry failure
    'retries':1, #if fails how many times should we retry?
    'retry_delay':timedelta(minutes=1), #  if we need to retry how long should we wait before retrying?
    'tags':['Task P14']
    
}

"""
P14. Schedule the pipeline so that it runs everyday. (5 points)
"""
# define the dag 
dag = DAG(
    'Assignment-3', # give the dag a name 
    default_args=default_args, # pass the default args defined above or you can override them here if you want this dag to behave a little different
    schedule_interval='@daily',# every minute-> '*/1 * * * *', Daily ->'@daily', define how often you want it to run - you can pass cron expressions here
    description='A simple tutorial DAG',
    start_date=datetime(2022,10,26)
)


"""
P13. Build a pipeline that runs queries you wrote for P4
"""
bq_task_4 = BigQueryOperator(
    dag = dag, # need to tell airflow that this task belongs to the dag we defined above
    task_id='p13_partp4',# task id's must be uniqe within the dag
    sql='sql/p13_partp4.sql', # the actual sql command we want to run on bigquery is in this file in the same folder. it is also templated
    write_disposition='WRITE_TRUNCATE',
    use_legacy_sql=False
)

"""
P13. Build a pipeline that runs queries you wrote for P5
"""
bq_task_5 = BigQueryOperator(
    dag = dag, # need to tell airflow that this task belongs to the dag we defined above
    task_id='p13_partp5',# task id's must be uniqe within the dag
    sql='sql/p13_partp5.sql', # the actual sql command we want to run on bigquery is in this file in the same folder. it is also templated
    write_disposition='WRITE_TRUNCATE',
    use_legacy_sql=False
)

"""
P13. Build a pipeline that runs queries you wrote for P12
"""
bq_task_12 = BigQueryOperator(
    dag = dag, # need to tell airflow that this task belongs to the dag we defined above
    task_id='p13_partp12',# task id's must be uniqe within the dag
    sql='sql/p13_partp12.sql', # the actual sql command we want to run on bigquery is in this file in the same folder. it is also templated
    write_disposition='WRITE_TRUNCATE',
    use_legacy_sql=False
)

"""
P.20 run shell script via pipeline
"""
bq_task_20 =  BashOperator(
            dag=dag,# need to tell airflow that this task belongs to the dag we defined above
            task_id="p13_partp20",# task id's must be uniqe within the dag
            bash_command="script/export_p12.sh" #read external script file to export the result of P12 to Google Cloud storage
)

"""
Schedule Task
"""
"""
P14. Make sure the queries run in order, P4, then P5, then P15 (5 points)
"""
"""
P20. Add that step as the last step of the Airflow pipeline (5 points).
"""
bq_task_4 >> bq_task_5 >> bq_task_12 >> bq_task_20
