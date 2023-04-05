.. _quickstart:

Quickstart
==========

Make sure that:

* SFrout is :ref:`installed <install>`


Report list preparation
-----------------------

Prepare list of your reports and save it as ``reports.csv``, name of the file can be different::

    report_file_name,report_id,report_path,optional_export_params
    Report_1,00O1V00000999GHES,C:\reports,


Executing request
-----------------

**SFrout** can works in two modes, as importable library in Python or as CLI app in console.

Import::

    import sfrout


    sfrout.run(domain="https://corp.my.salesforce.com/", 
               reports_path="C:\\path\\to\\reports.csv")

CLI::

    $ sfrout "https://corp.my.salesforce.com/" "C:\\path\\to\\reports.csv"


That's it! Shortly after executing the command **SFrout** might ask to log in to SFDC in MS Edge. Once you authenticate entire process will start, progres bar will show up. Once **SFrout** finishes you will see conveninent table with summary. Shortly after your reports will be dropped to given location. 
Time required for entire operation is impacted by report size, bandwidth of your internet connection and current SFDC condition.
 
-----------------------

Would you like to customize the way how **SFrout** works? Check out the :ref:`advanced <advanced>` section.