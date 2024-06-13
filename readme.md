# Ultraleicht Trekking Forum - Biete - Erledigt
This script looks at every thread in the [Ultraleicht Trekking/Biete Forum](https://www.ultraleicht-trekking.com/forum/forum/53-biete/) and reads the last post in there.

All these last posts are put into a .csv file at the end with their URL, thread title and whether the post contains a set of keywords indicating whether the thread can be moved to the [done forum](https://www.ultraleicht-trekking.com/forum/forum/55-erledigt/)

# Run
```python
pipenv install
pipenv run main
```

# Dev
Restarts after every edit to the python file
`pipenv run hupper main`
