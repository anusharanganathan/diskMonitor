# -*- coding: utf-8 -*-
"""
    Disk monitor task configuration options for Celery

    Copyright: (c) 2010 by Anusha Ranganathan.
"""

BROKER_URL = 'amqp://'
CELERY_RESULT_BACKEND = "amqp://"
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Europe/London'
CELERY_ENABLE_UTC = True
CELERY_TASK_RESULT_EXPIRES=600 
CELERY_IMPORTS = ("notifyTask",)
#CELERY_ANNOTATIONS = {
#    'tasks.add': {'rate_limit': '10/s'}
#}



