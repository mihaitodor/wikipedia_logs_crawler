# Wikipedia Server Admin Log Crawler
Dumps the contents of the [Wikipedia Server Admin Log](https://wikitech.wikimedia.org/wiki/Server_Admin_Log) to a JSON file

## Usage
`python run.py`
The output will be generated in output/wiki_logs.json

## TODO
- some `<h2>` elements are followed by several `<ul>` and `<pre>` and `<dl>` and other such elements that are currently treated as identical
- some `<li>` elements might have children that are currently concatenated into a single entry
- links and other embedded html are extracted as text
- detect other inconsistencies