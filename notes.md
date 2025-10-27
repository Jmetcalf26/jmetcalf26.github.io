# Infrastructure ideas

## Azure

### SQL DB 
- Use a SQL database to store concert information, with a table for each venue
- Using a dedicated DB will allow for scaling?
- Issues:
 - How does it talk to the web server? 
 - Why not just run it all on a VM? A: not good for long term management, requires less learning

### Webapp
- Use an azure webapp to run the webserver and python backend. 
- Can allow for talking to the DB?
