<!--Under active development, not safe for consumption!
===================================================-->
Live site
=========
https://i5k.nal.usda.gov/webapp/blast/

Backend
=======
* Implemented in [Python](https://www.python.org/) with [Django](https://www.djangoproject.com/).
* Supports the latest [NCBI BLAST+ executables](http://blast.ncbi.nlm.nih.gov/Blast.cgi?PAGE_TYPE=BlastDocs&DOC_TYPE=Download).
* Task queue with [RabbitMQ](http://www.rabbitmq.com/).
* Generates all BLAST output formats for download: Text, CSV, TSV, XML, ASN.1.
* Converts BLAST output to GFF3 by grouping contiguous HSPs with identical query sequence, subject sequence, strand direction and an overlap length less than 6 between neighbouring HSPs under the same match.
* Retrieve previous results with a unique URL for every task.
* Supports both Linux and Windows.

Frontend - Results
=================
The results page is an interactive data viewer, query and subject coverage graphs on the top are drawn dynamically on the HTML5 canvas for every high scoring pair (HSP), tabular output from BLAST+ is displayed in a sortable and searchable table on the bottom right, pairwise text output is displayed on the bottom left panel.
* Fullscreen design dynamically scales to any screen size
* Dynamically draws a unique query coverage graph and a subject coverage graph for every high scoring pair(HSP) on HTML5 canvas.
* Interactive graph updates the page as the user mouse over each aligned segment.
* Graph zoom level and line height are first calculated according to the data and screen size, but can be easily adjusted to user's preference using the sliders on the left and right sides of each graph.
* Interactive results table updates the page as the user:
  * Mouse over each row.
  * Changes the sorting column.
  * Filters the table using the search box.
* Tested on the latest versions of Chrome, Firefox, IE.
  * On Windows: Chrome (ver. 36.0), Firefox (ver. 31.0), IE (ver. 11)

Screenshots
===========
BLAST Results
![BLAST Results](https://raw.githubusercontent.com/hotdogee/django-blast/doc/doc/images/blast-results-dynamic.gif)
