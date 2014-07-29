Under active development, not safe for consumption!
===================================================
Set environment variable BLASTDB to the location of your db files.

Backend
=======
* Implemented in [Python](https://www.python.org/) with [Django](https://www.djangoproject.com/).
* Supports the latest [NCBI BLAST+ executables](http://blast.ncbi.nlm.nih.gov/Blast.cgi?PAGE_TYPE=BlastDocs&DOC_TYPE=Download).
* Task Queue with [RabbitMQ](http://www.rabbitmq.com/).
* Generates all BLAST output formats for download: Text, CSV, TSV, XML, ASN.1.
* Retreive previous results with a unique url for every task.

Fronend - Results
=================
* Fullscreen design scales perfectly to any screen size.
* Dynamically draws a unique query converage graph and a subject converage graph for every high scoring pair(HSP) on HTML5 canvas.
* Interactive graph updates the page as the user mouse over each aligned segment.
* Graph zoom level and line height are first calculated according to the data and screen size, but can be easily adjusted to user's preference using the sliders on the left and right sides of each graph.
* Interactive results table updates the page as the user:
  * Mouse over each row.
  * Changes the sorting column.
  * Filters the table using the search box.

Screenshots
===========
BLAST Results
![alt tag](https://github.com/hotdogee/django-blast/blob/doc/doc/images/blast-results-dynamic.gif)
