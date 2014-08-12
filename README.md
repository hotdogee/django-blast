<!--Under active development, not safe for consumption!
===================================================-->

Backend
=======
* Implemented in [Python](https://www.python.org/) with [Django](https://www.djangoproject.com/).
* Supports the latest [NCBI BLAST+ executables](http://blast.ncbi.nlm.nih.gov/Blast.cgi?PAGE_TYPE=BlastDocs&DOC_TYPE=Download).
* Task queue with [RabbitMQ](http://www.rabbitmq.com/).
* Generates all BLAST output formats for download: Text, CSV, TSV, XML, ASN.1.
* Retrieve previous results with a unique URL for every task.
* Works on Linux and Windows.

Frontend - Results
=================
* Fullscreen design dynamically scales to any screen size
* Dynamically draws a unique query converage graph and a subject converage graph for every high scoring pair(HSP) on HTML5 canvas.
* Interactive graph updates the page as the user mouse over each aligned segment.
* Graph zoom level and line height are first calculated according to the data and screen size, but can be easily adjusted to user's preference using the sliders on the left and right sides of each graph.
* Interactive results table updates the page as the user:
  * Mouse over each row.
  * Changes the sorting column.
  * Filters the table using the search box.
* Works on the latest versions of Chrome (ver. 36.0), Firefox (ver. 31.0), IE (ver. 11).

Screenshots
===========
BLAST Results
![BLAST Results](https://raw.githubusercontent.com/hotdogee/django-blast/doc/doc/images/blast-results-dynamic.gif)
