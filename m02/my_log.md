## My Lab Notebook for CS1066 PSet #1

INSERT-YOUR-NAME

INSERT-YOUR-VIDEO-LINK (after completing this assignment)

----
----

### SUBTASK #1: Prompt for the Search Term

----
Text of my first prompt:

> Edit this program to achieve the following goal:

We want this program, when it runs, to prompt the user for a phrase or search term to be inputted into the varaible query in main on line 16. This is so that the user does not need to edit the file every single time to change the string in query.

Reflections on success/failure of this prompt:

*  This prompt seems to be very successful. It was a simple edit as I thought, it seems to have used the input command native to python to prompt the user for a phrase. Now we will see if this is actually the correct usage.

----
Text of my next prompt:

> N/A, the first prompt worked!

Reflections on success/failure of this prompt:

*   Very successful first prompt, no issues were found and the desired task was achieved

----
**NOTE:** Delete this text and repeat the above block for as many prompts as it takes to complete this subtask.

----
**FINAL REFLECTION:** Review your work. Write a brief statement of what you might have done differently in hindsight, or defend why your work was a good approach.

I think my work was a good approach considering all design goals were achieved.

----
----

### SUBTASK #2: Just One Tool

----
Text of my first prompt:

> In the file my_tool.py, I want you to create a script that does the function of the trends_save.py to trends_plot.py pipeline. Thus first import the function in trends_save.py, then instead of having it write the csv to the m02 folder, have it stay within the code and then import the functions from trends_plot.py. Use the functions to create the plot from the CSV created by the trends_plot.py that should be in a local variable within this new file my_tool.py. The end result should be the bar graph generated from trends_plot.py

Reflections on success/failure of this prompt:

*   This prompt was again successful. My prompt was a little long, but considering that it accomplished the task at hand, that is a favorable trade off in my opinion.

----


----
**FINAL REFLECTION:** Review your work. Write a brief statement of what you might have done differently in hindsight, or defend why your work was a good approach.

... Even though my prompt was a little long, considering the goals at hand were achieved, I do not see any reason to change my approach....

----
----

### NEW TASK: Improve the Tool

----
Another idea that aligns with this challenge:

> I believe that another idea that aligns with this challenge would be to enable the tool to be able to make a graph that compared multiple search terms simultaneously. This would be a graph that overlays multiple bars on each region according to how many search queries that the user would want to compare. The amount of queries would need to be capped to avoid an excessive amount such as 100.

----
Which improvement I chose to implement (put an X on the line):

_x__  The professor's example idea -

___  My idea above

----
Text of my first prompt:

> In my_tool.py, lets set the filename of the graph that is outputted to be interest_data_{query}. Make sure to modify the query string so that it is in all lowercase and remove any nonalphabetic characters. Also in the case the file name already exists, lets tell the user that it already exists, and ask if it wants to override this file at the end, with a simple y/n prompt, make sure to protect against characters that are not y or n. 

Reflections on success/failure of this prompt:

*   This prompt worked greatly. I added unique file names while protecting against duplicates, but also giving the option to override the current file with the same name, in the case that the user does prefer to do that.

----


----
**FINAL REFLECTION:** Review your work. Write a brief statement of what you might have done differently in hindsight, or defend why your work was a good approach.

... I think my approach was great, all design goals were met. I will say that I am fortunate to have prior programming experience which makes prompting much easier ...

----
----

### Final Questions

1.  In your own words, give names to the steps in the problem-solving process you followed.

    1. Understand the problem and what needs to be done to achieve the goals laid out in the problem.
    2. Ideate specific changes/additions that need to be made to the program to achieve these goals.
    3. Prompt the AI with specific instructions for each change and addition. Remember to prompt to the AI to implement any safeguards against edge cases.
    4. Evaluate the outcome of the AI's changes to the program. If all goals are met, you are done. However, if all goals are not met, you must reprompt and possibly repeat the steps above if the failure is severe.


2.  Which step do you find most challenging, and why?

    Step 3. This is the hardest part because now you must use jargon that the AI understands (not for everyone, but I make sure to do this as it results in successful prompts on the first try, so far). Furthermore, you must remember any edge cases, such as duplicate file names, or the user inputting the wrong letter, as these possible failures might not be caught by the AI unless you specifically point them out.

3.  What two questions do you have about how Python expresses the tasks you might ask it to do?

    How can we prompt the user to input a substring into a string?

    What libaries are used to create files such as the CSV, or graphs/images?

----
----

### Other's Review

... YOU DO NOTHING HERE; ANOTHER STUDENT WILL COMPLETE THIS PART IN SECTION ...

----
----

### AI's Review

... PASTE AI'S FEEDBACK ON THIS LAB NOTEBOOK HERE ...
