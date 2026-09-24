## My Lab Notebook for CS1066 PSet #2

Andrew Le Blanc

INSERT-YOUR-VIDEO-LINK (after completing this assignment)

----
----

### Describe Your Decomposition Approach

The first sub-problem that I want to tackle is building a python scraper to pull the relevant information from the EDGAR API using the Python requests module. Specifically, I know that one of the key first steps of the program is first being able to get the right information. Thus, I want to ensure that the function to pull our data has all the right headers and will work as we need it to.

Then, I will take this information and parse it to create a CSV for the desired columns dating back min(10 years, age of company). Then I will iterate on the csv files to ensure that they give out the correct values. This is the most important part because we will use these values to construct our plots on the HTML, thus we must ensure that we have accurate information.

After I ensure that this scraper is returning the correct values, I will then tackle the problem of creating a plot from these values. After creating the prompt I will then have the AI create the HTML page with this plot displayed as well as information from the previous to create a financials dashboard.

Overall the main four subproblems are the following. First, create a working scraper with the EDGAR API. Second, correctly parse the data to retrieve the financial figures for what we are interested in. Third, create a plot of these figures. Lastly, create an HTML page displaying this plot as well as other information relevant for a financials dashboard.

----
----

### Document Your Iterations with AI

----

Text of my first prompt:

lets build a python scraper using the requests module that will scrape data from the SEC using the EDGAR API. Use the following User-agent header : "UniversityStudent your.emal@university.edu"

Reflections on success/failure of this prompt:

Success:
- Correctly uses requests modules and user-agent header 
- Ensures that there won't be problems pulling the data with the correct headers

Failures
- Very vague, doesn't give the exact URL to access the API

----

Text of my next prompt:

 With the information returned from the API, I want you to create CSV files with the company's revenue, net income, and assets over the past 10 years or as far back as the data goes if it doesnt go back at least 10 years.

Reflections on success/failure of this prompt:

*  Success:
- The CSV files are created with values for the past 10 years
- Furthermore, theres data for all 3 categories.
Failure:
- I did not give an exact parsing "algorithm" or general guideine
- Thus, some values were inaccurate due to later revisions in later filing reports 


Text of my next prompt:

 Have this file prompt users to fill in the 10 digit CIK of the company they want to look up, make sure their input is 10 numerical characters and if the program fails because the 10 digit CIK is not a valid company CIK, return an error message stating that this is the reason why.

Reflections on success/failure of this prompt:

*   Success
- Fairly simple task that the AI succeeded on because I was able to specify the problem in detail
- I handle all edge cases here, and thus after testing these edge cases, I can confirm the AI handled this task correctly

Text of my next prompt:

Now take the CSVs generated and create a single plot showing a companies revenue, net income, and assets over the past 10 years. Display this plot on an html page and have the program when run, display this html page for the user.

Reflections on success/failure of this prompt:

Success - The HTML page was generated
Failure - It did run at the end of the program
- The page would not render

- Later I learned that this IDE would not render the html page. I would have to download the HTML file to see it, but at this point I wanted to ensure the CSVs had the correct values because that is the most important part of this program


Text of my next prompt:

I have a Python scraper that uses the SEC EDGAR `companyfacts` API to retrieve a company's annual financial history for the last 10 years.

The scraper currently retrieves:

- revenue
- net income
- total assets
I discovered an important issue: companies sometimes restate or retrospectively adjust prior-year financial figures. For example, AMD originally reported one revenue figure for 2017, but a later 10-K reported a revised value for that same fiscal period.

Please modify my scraper so that the historical series for **revenue, net income, and assets reflects the latest value reported by the company for each historical period**, rather than simply taking the value from the original filing.

Reflections on success/failure of this prompt:

 success
- I have great specification and identify the problem for the AI
- I give good instructions on to take the information from the most recent filing detailing the financials of that year.
failures:
- Again, I do not give specific instructions on how to parse, which will lead to a random parsing algorithm that I might have to debug

Text of my next prompt:

there seems to be a bug for collecting assets, in the 0000002488_assets.csv, you report the wrong number for 2016. the same bug doesnt persist for net income and revenue, so it may just be for assets since it only has end dates and requires a different function

Reflections on success/failure of this prompt:

success:
- I identified the bug for the AI and told it to investiagte why it might not be working.
- I gave it a possible explanation
Failure:
- The AI does not think its wrong.


Text of my next prompt:

im getting that its 3.32 B in the 2018 filing can you double check that

Reflections on success/failure of this prompt:

Failure- AI still thinks that it is write.
- Maybe, I should specify the year that the figure is revised.

Text of my next prompt:

double check the february 8, 2019 filing, I do not thinnk that is correct

Reflections on success/failure of this prompt:

- Success
- AI correctly identifies issue
- This is important because I wanted the AI to have context of the issue in the program, the AI recognized that it will need to parse the primary 10-K filing itself, beyond the companyfacts API

Text of my next prompt:

Build this fall back for assets, net_income, and revenue

Reflections on success/failure of this prompt:

Success:
- I recognize that if this fall back (reading the 10-k filing)didn't exist for assets, then it probably doesn't exist for net_income, and revenue.
Failure:
- vagueness, I am not telling the AI how to parse the 10-k filing, partly because I am not familiar with the form myself. I may have to debug later

Text of my next prompt:
it seems that you have cut off 0s in revenue and net_income, could this be because the numbers are represented as 6731 million, if so please add a feature that will correctly output the numbers in the CSV

Reflections on success/failure of this prompt:

Success-
I correctly recognize that the reason that there may be small numbers in the CSV is because these filing report these figures like "6743 million"
- Thus I tell the chatbot to correctly output numbers that are in this format

Failures
- Again, not much specificity, but I do not think that this will be an issue since it is a minor addition

Text of my next prompt:

Make sure for assets, we are only pulling figures from the consolidated-non dimensional fact. It seems that you extracted fair value assets for some years

Reflections on success/failure of this prompt:

Success
- I again recognized a bug that results from how the script parses the 10-k filing.
- I specified the bug and told it to only pull numbers from the specific financial figure we want, not another one with a similar name.


Text of my next prompt:

For the html page, can you make the plot a png file in the sec_data folder in this pipeline. Then in the html file, make it a nice webpage displaying the plot with the company's revenue, net income, and assets as a png file. Then make the webpage interface appealing

Reflections on success/failure of this prompt:

Success-
-I gave explicit instructions on how to create the financials dashboard.

Failures-
- I made the wrong assumption that the webpage wasn't loading because of an issue with the image tag, and I tried to implement the wrong fix

Text of my next prompt:

also have this pipeline output everything in a file called sec_data_{CIK}

if this file already exists, ask user if it wants to override this file

Reflections on success/failure of this prompt:

Success
-Minor task with explicit instructions
-No bugs found with this task.

Text of my next prompt:

is there a way to actually graph this in the HTML file to make this standalone

Reflections on success/failure of this prompt:

Success
- The prompt did convert the image tag to instead be a plot of the figure that is created inside the HTML file when this script runs.
- Thus the HTML file is standalone, and accomplishes the task of creating a webpage detailing the companies financials
Failures:
-Sort of a question instead of me telling the AI what to do.
- Luckily the AI just created it but maybe I could tell it what to do depending on its answer to my question

----

**NOTE:** Delete this text and repeat the above block for as many prompts as it takes to complete the pset.

----

**FINAL REFLECTION:** Review your prompting work. How does your work on this pset compare with that of the first pset?

Clearly, this pset took much more work than the first pset. I think that my prompting on this pset was not as good as the first. I can attribute this to my lack of domain knowledge of how K-10 filing works. In fact, now that I think about it, I didn't even check to see if the revised figures would pop up in the JSON retrieved from the API. Instead I let the AI create an algorithm to parse the K-10. To improve, I would want to gain more domain knowledge on the topic at hand and also the structure of the JSON returned from the API. I think if I have more knowledge on these issues, then I can be more specific in telling the AI what I want it to do. On this pset, I treated the AI too much like a blackbox, which is probably why there was a lot more bugs than the first pset. This is okay and why its good to be challenged so that I can recognize my shortcomings and improve on them. In the next pset, I will try to have a better understanding of the task at hand and the JSON structure as well as any other files structure. I will do this so that I can be more specific in my prompts which should lead to better outcomes.

----
----

### Handling the Problem's Whitespace

When you have a working solution, write a brief statement describing how you ultimately approached the problem's whitespace. What you might have done differently in hindsight, and why? Or defend why your work was a good approach.

I think for simpler tasks, I definitely gave more specific instructions for the AI. However, for the larger and more important tasks such as parsing the JSON/K-10 filing to retrieve the correct information, I gave the AI too much whitespace. I would not want to do this again in the future because I feel like I spent a lot of time debugging in this PSET. As I said in my reflection, I will want to gain more knowledge on the architecture of the pipeline and also domain knowledge on these financial filing reports. I think I lacked specificity due to a lack of knowledge, thus it will be important to gain more architecture and domain knowledge for the future. I want to eliminate as much whitespace as I can for these AI models to ensure that the results I want to retrieve are the results I ultimately get. Therefore, in the future I am going to change my approach to minimize the amount of whitespace given to the AI's discretion.

----
----

### Other's Review

... YOU DO NOTHING HERE; ANOTHER STUDENT WILL COMPLETE THIS PART IN SECTION ...

----
----

### AI's Review

... PASTE AI'S FEEDBACK ON THIS LAB NOTEBOOK HERE ...
