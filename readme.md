# Ultraleicht Trekking Forum - Biete - Erledigt
This script looks at every thread in the [Ultraleicht Trekking/Biete Forum](https://www.ultraleicht-trekking.com/forum/forum/53-biete/) and reads the last post in there.

All these last posts are put into a .csv file at the end with their URL, thread title and whether the post contains a set of keywords indicating whether the thread can be moved to the [done forum](https://www.ultraleicht-trekking.com/forum/forum/55-erledigt/)

# Run
```python
pipenv install
pipenv run main
# now check the created csv file
```

# Dev
Restarts after every edit to the python file
`pipenv run hupper -m main`

You may want to limit the number of pages visited (`main.py` `get_all_threads(max_page=100)`) to `1` or `2` and after the first run disable that part and rely on the intermediary `threads.pkl` file, which caches the results of `get_all_threads`.