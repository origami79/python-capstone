# Python Capstone - Tolkien Population Generator

While doing a deep dive into the various timelines and edits Tolkien did to his background worldbuilding in Arda, I ended up squinting at the stated population numbers for the Elves when they began the Great Journey (20k Elves who departed, with about 40% remaining behind as Avari, so a total target population of approximately 32k) as well as the Unbegotten who awoke at Cuiviénen (144, already matched up into 72 couples), and questioned the realism of such a small starting population managing to hit such large numbers without massive levels of inbreeding.

And thus, this project was born!

The original, proof of concept form is the "tolkien" folder, which does some basic simulation of matchmaking, birthing new elves, and killing off a few (presumably to Morgoth or pure accident) each year, all stored in local memory and then saved to a JSON at the end, which can later be loaded and parsed back into the same data format to be worked with some more.

The second iteration is the "tolkien-db-version" which, as the name suggests, is upgraded to use an actual SQLite database rather than just a couple dictionary objects. It also has more strict criteria for choosing potential spouses, and a parameters file to allow a certain amount of custimization when it comes to finetuning details such as the time between children and age to adulthood. 

In terms of efficiency, the database version is NOT actually faster than the non-database version, at least not at the scale of 500 years or more. I imagine that part of that can be blamed on the clumsiness of my many queries to the db itself, and intend to try and continue streamlining those. A certain amount of blame can also likely be directed at the checks for relatives used to avoid incest; the non-database version of code checks for:
- self
- parents
- children
- siblings, full and half
- grandparents
- grandchildren
- aunts/uncles, full and half
- nieces/nephews, full and half
when looking to disqualify potential suitors, while the database version has an expanded list checking for:
- self
- parents
- children
- siblings, full and half
- grandparents
- grandchildren
- aunts/uncles, full and half
- nieces/nephews, full and half
- full first cousins, NOT half
- great grandparents
- great grandchildren
- full great aunts/uncles, NOT half
- full great nieces/nephews, NOT half

The first list was thrown together as part of the simple proof of concept, while the second one was more thoughtfully compiled based on the assertion that Elves do not marry so close as first cousins (which has variously been ignored or temporized to "rarely marry so close as first cousins" depending on the the revision). Consulting a consanguinity table, I put together a list of any familial relationship as close as or closer than first cousins, and used that. The added complexity of tracking (and querying for) all these relationships is no doubt a contributing factor to why the database version is still so slow.