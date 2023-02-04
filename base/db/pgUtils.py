# coding: utf-8
"""
    base.db.database
    ~~~~~~~~~~~~~

    Cria todas as tabelas necessÃ¡rias.
"""

import sys
import psycopg2
import logging

__all__ = [ 'Database' ]

# define a function that handles and parses psycopg2 exceptions
def print_psycopg2_exception(err):
    # get details about the exception
    err_type, err_obj, traceback = sys.exc_info()
    

    # get the line number when exception occured
    line_num = traceback.tb_lineno

    # print the connect() error
    print ("\npsycopg2 ERROR:", err, "on line number:", line_num)
    print ("psycopg2 traceback:", traceback, "-- type:", err_type)

    # psycopg2 extensions.Diagnostics object attribute
    try:
        print ("\nextensions.Diagnostics:", err.diag)
    except:
        print ("pgerror:", err.pgerror)
    # print the pgcode and pgerror exceptions
    finally:
        print ("pgcode:", err.pgcode, "\n")
    