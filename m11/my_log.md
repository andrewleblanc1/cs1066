## My Lab Notebook for CS1066 PSet #5

Andrew Le Blanc

NOTE: There is no video in this pset as you'll demo in section.

----
----

### ACTIVITY #1 (UNGRADED)

We don't require you to write anything around this first activity, but we leave space in case you decide to keep your own notes (**a good practice**). We won't grade anything in this section.

----

> SPACE FOR YOUR OWN NOTES

----
----

### ACTIVITY #2 (UNGRADED)

Again, you aren't required to write anything around this activity, but we leave space in case you decide to keep your own notes. We won't grade anything in this section.

----

> SPACE FOR YOUR OWN NOTES


----
----

### ACTIVITY #3 (UNGRADED)

This is your first at-home work, but it should be fairly straightforward. Make sure you understand what we ask, which you might see on a quiz. But, we won't grade anything in this section.

----

> SPACE FOR YOUR OWN NOTES

----
----

### ACTIVITY #4 (GRADED!!!)

----

Text of my first prompt:

can we just design a program that would allow me to make queries of the database we have created, exoplanets.db

Reflections on success/failure of this prompt:

*   Success: 
- It created a program that when run allows users to query the database in the terminal with SQL commands - This is perfect because its exactly what we wanted per the problem description.
- Furthermore, the queries correctly return the information we want (according to our query) in the terminal. Again, this is perfect because its exactly what we wanted per the problem description.

Failure:
- The output in the terminal does not provide instruction, for people who have never used SQL, they will be confused on what to do, perhaps, I should provide a help command to show how to query the database
- Furthermore,for people that do not know the schema, they will not know how to query the database, therefore, we should have the terminal output the schema of our database for users.

----

Text of my next prompt:

lets display the database schema when the program is run so that users know how to query this database. Also provide a help command to assist users new to SQL by showing them examples of how to query the database

Reflections on success/failure of this prompt:

*   Success- correctly displayed the database schema in the terminal
- Also provided the help command, which shows example queries and also the available tables and schema which is very helpful and can be used in the future if users forget the schema after a query.
Failure - includes an unknown table sqlite_sequence, I do not its relation to the rest of the database and how it relates to what we want to know. I am going to ask the AI about this.

----
Text of my next prompt:

what is sqlite_sequence

Reflections on success/failure of this prompt:

*   success- 
-it told me that sqlite_sequence is a hidden internal table that sqlite uses when you use autoincrememnt on a primary key. 
-Basically it serves a purpose in maintaining our database but is not useful to query. Thus, now we know we can remove it

failure - the only real "failure" is that we didn't remove it from our terminal output, but we can easily do this in our next prompt



Text of my next prompt:

can you filter it out of the schema display since it is not relevant to users

Reflections on success/failure of this prompt:

Success - all success for this prompt since it successfully removed that irrelevant table from terminal output.


----
----

### ACTIVITY #5 (GRADED!!!)

----

Three fields you pick: pl_rade (planet radius), pl_orbper (orbital period in days), pl_eqt (equilibrium temperature in Kelvin)

----

Text of my first prompt:

Please create web browser based interface, for inputting a rance of values for each of the following fields,  pl_rade,  pl_orbper, and pl_eqt. The output list should be the top 5 candidate exoplanets given the critiera. please display this output in the web-based interface and save the list to a JSON file. I am assuming top candidates are the ones with the closest resemblance to earth.

Reflections on success/failure of this prompt:

*   success:
- Created the browser based interface using a Flask framework.
- has input fields for the three fields I wanted
- has description of what the output list will show and also what earth's statitistics are in each of those fields.
- saves a json file
Failure:
- there are no limits on the range I can put in these fields, I think it would be better to have the range be the minimum value a planet has in that field through the maximum value a planet has in that field
- earth likeness scores seem to be the lower the score, the more closely related to earth a planet is, I am confused on this, this was whitespace the AI handled and I will need to ask it questions about it
- the saved json file is overridden everytime a user finds the top 5 planets based on the ranges in those fields, I need to make a folder than stores every top 5 planets

----

Text of my next prompt:

I have an easy fix for you to do, I want limits on the range a user inputs to the three fields range, specifically a user should not be able to put a value lower than the minimum value a planet has in that field on the minimum side of the range. on the otehr hand, a user should not be able to put a value higher than the maximum vlaue a planet has in that field on the maximum side of the range.

Reflections on success/failure of this prompt:

*   success- 
- it created the correct bounds for 4 out of the 6 min/maxes
- it stops users from setting ranges outside of these bounds
failure
- it created the incorrect bounds for 2 out of the 6 min/maxes
- this is confusing, it made me question whether the AI was using the same SQL commands as me and upon further evaluation, it was using the WHERE command which required all three fields to be filled out. Thus, it was giving the wrong bounds for 2 of the 6 because it did not include all of the values in that column.
----

Text of my next prompt:

Can you please describe in the web browser interface what the earth likeness score represents, specifically what do higher scores represent and what do lower scores represent. also your bounds for min(pl_orbper) and min(pl_eqt) should be the following, min(pl_orbper) = 0.090706293 and min(pl_eqt) = 34.0.
Reflections on success/failure of this prompt:

*   success- 
- it added a description that informs users that the lower the score, the more the planet resembles earth and the higher the score, the less the planet resembles earth.
- it corrected the bounds for the last 2 that were incorrect
failure
- I have just realized that for some reason, when inserting the min and max of the range, it wants exact values, im assuming values that match a planets actual value for that field. I do not like this feature, it complicates things and is just a bad design
- I will have to fix this feature in the next prompt along with managing viewlist_results.json

Text of my next prompt:

Okay when the results are saved to viewlist_results.json, every time a new result is saved, it overwrites this file, can you create a folder that stores these result files, specifically allow for different result files to be made and name that by the min max parameters per field, if a file has the same name in this case, it matches the same range values for all three fields,we can  then overwrite it

Reflections on success/failure of this prompt:

*   success- 
- it created a folder than now holds all the result jsons.
- furthermore, the files in this folder have different names corresponding to the min-max range of the three field
- the only case where files will be overridden is when the min-max range of the three fields are the same as a file already present in the results folder
- This is all great because this is exactly what I wanted
failure
- The only possible failure that I could think of is that the file names are complicated, but I do not know of a simpler way to name them, so I am going to let this complication be


Text of my next prompt:

last fix, when inserting values, it ask my values to match what a user might see as arbitrary values, for example if in put 0.5 into the min planet radius field, it will ask me to choose like either 0.47 or 0.53. I am assuming it wants to match the value of a radius actually present in the database, I do not want this feature, i want them to be able to put whatever value they want as long as it is in the valid range

Reflections on success/failure of this prompt:

*   success- 
- the AI realized that the step attribute on inputs was causing this
- so it correctly set step="any" to fix this problem which might confuse users
failures
- While this prompt was not necessarily a failure, it makes me question why the AI would do this and I'll reflect on the failure that the AI made this mistake in the first place
- Whats important to know, is that the AI defaults to this attribute when I leave this white space unspecified.
- Therefore, in future programs, I should keep this in mind and tell the AI to set step="any" to avoid this problem in the future
----
----

**FINAL QUESTIONS:** Review your work on ALL parts of this pset and answer the following questions.

-   What aspects of working with databases still feel uncomfortably hazy?

Honestly, I have taken CS50 where we learn how to use SQL. Furthermore, I have done some outside practice with websites such as W3 schools and in my personal projects. Therefore, I am fairly confident with working with databases. The only aspect I am trying to improve on is my use of ORMs like Django's ORM. I am still practicing this, it is a bit hard to learn just due to syntatical differences.


-   How did you decide what aspects of the database your query program should focus on?

If you are talking about the query program in #4, I actually made it fairly accessible to be able to use it for almost every aspect of the database. The only aspect I didn't include was a table that was used by sqlite3 to keep track of what value they had for the autoincrement ids present in the tables relevant to users. Since this table is only relevant to the sqlite3 program and not relevant to users I removed from the schema it displays at the beginning of the program. I specifically displayed schema at the start of the program in the terminal so that users can easily navigate querying the database. I wanted the aspects of the database that the query program focused on to be decided by the users. I did this because I recognize users have different needs. 

If this references activity 5, I chose the three fields because I believe those three fields are the most important in determining how closely a planet resembles earth. I wish I had my own justification for choosing these fields. To be honest, I am not an astronomer. Thus I delegated this decision to the internet and searched up which fields were the most important out of the list. Then I chose pl_rade (planet radius) because earth sized planets are more likely to be rocky/terrestrial (similar terrain) rather than gas giants. A similiar radius also suggest similar graviational forces and the terrain is necessary for life. I chose pl_orbper (orbital period) because it correlates with the distance from the host star. Its a good indicator of weather or not the planet is in its host star's habital zone. A similar orbital period suggests a possibility of being in its star's habital zone which provides earth like resemblance. Lastly, I chose pl_eqt (equilibrium temperature) as this directly measures how much energy a planet receives from its star. This is the most direct proxy of weather liquid water can exist. Planets similar to earths equlibrium temperature are more likely to have temperate surface conditions which is necessary for life. Overall, these factors made me focus my queries on those three fields.



-   Briefly describe how you decided on the interface in Activity #5.

Honestly, in the first prompt, I asked for a web-browser based interface which leaves a lot of whitespace to the AI. It created one using Flask, HTML, CSS, and Javascript. I have actually used this framework before in creating a web based application to play Blackjack so I was content with this interface. While it is not the prettiest, it gets the job done. It is much easier to use compared to command line programs such that it can be used by anyone who has ever used the internet before. Since I am focused on functionality rather than the beauty of the interface, I was more than content with the interface created by the AI. In this activity, I wanted an interface easy to use and the AI provided that, so I saw no need to change it.