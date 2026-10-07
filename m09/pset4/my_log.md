## My Lab Notebook for CS1066 PSet #4

INSERT-YOUR-NAME

INSERT-YOUR-VIDEO-LINK (after completing this assignment)

----
----

### Document Your Iterations with AI

----

Text of my first prompt (copied from the pset directions):

The folder `m09/data_room` was prepared by a startup I'm looking to acquire. In it, focus on the `people` folder. In the directory `m09/pset4`, create an interactive app in Python using Streamlit that allows me to run scenarios on the number of people I can bring on. Use a Python virtual environment for any packages that need to be installed. The app should implement a slider that sets the total headcount number, and it should display the total cost (based on compensation) for a team of that size. Prioritize people by compensation.


Reflections on success/failure of this prompt:

*  Success:
- Slider correctly implemented
- displays total cost for a team of that size
- correctly priortizes candidates/employees from highest to lowest based on compensation
Failure
- Very basic app
- Does not really explain why that team is selected
- Basically a blackbox, which is not very helpful when I want to be able to explain why I chose to retain this people

----

Text of my next prompt:
1.
So if you were in the management of a company acquiring an AI or tech startup, how would you decide who to keep from that company's team after you acquire them and who to fire?
2.
evaluate this data and give me the best prompt that I can feed my AI agent to have it use an algorithm that would evaluate personel based on the critera you have highlighted.
3.
Very long AI prompt I fed into the IDE agent

A refinement strategy from class: No

Meta prompting- using a separate AI to generate, critique, and optimize a secondary prompt for better performance
Reflections on success/failure of this prompt:

*   Success:
- It created a list of criterions for proper evaluation of the startup's employees
- It created a process for humans to evaluate each person to determine who to keep

Failure
- It changed the purpose of the app,it is now mainly a tool to individually evaluate employees
- That previous bullet point is not what we want, we want to the AI to create an algorithm to tell us who to keep based on headcount
- Honestly, this way of asking the AI to generate a prompt to feed into my IDE's AI generated more confusion. I think I will revert to the previous state of the application instead and do smaller steps on my next iterations.

----


Text of my next prompt:

I want you to take a look at the screenshots provided and adjust the UI to be professional like the one in the screenshots.

A refinement strategy from class: Yes

Provide examples or references

Reflections on success/failure of this prompt:

*   Success:
- It copied the example I provided, which is exactly what I wanted, a more corporate friendly template
Failure
- However, for certain divs, this template was not followed
- Hence, we have certain parts of the website which will not match the styling of the other elements
- This specifically occurred in the elements of the website not visible in the screenshot of the example, therefore, I should provide more screenshots next time.

----
Text of my next prompt: 
Pretend like you are the CEO evaluating this acquisition and from your MBA, you are evaluating employees based on the following, - **Strategic importance** — How connected are they to the reason the company was acquired?
- **Unique knowledge / IP** — Do they own critical systems, proprietary technology, institutional knowledge, or customer knowledge that would be hard to replace?
- **Demonstrated impact** — Have they produced measurable technical, product, revenue, cost, or operational results?
- **Performance / execution** — Do they consistently deliver strong work and execute effectively?
- **Replaceability** — How difficult would it be to replace them, and is there a credible successor or backup?
- **Customer / revenue dependency** — Are important customers, accounts, or revenue streams heavily dependent on them?
- **Integration value** — Will they be especially useful in helping combine the acquired company with the acquirer?
- **Key-person risk** — If they left immediately, how much damage would that do to the acquisition?
- **Retention / flight risk** — How likely are they to leave, and does that make a retention package more urgent?
- **Role overlap** — Does the acquiring company already have people performing essentially the same function?.

Please weight each factor according to how important each factor is in evaluating a person. Then please give each person an overall rating based on the data provided, add another filter that priortizes bringing on people with the highest scores. For example, with a headcount of 10, display the people with the 10 highest scores.

A refinement strategy from class:no

Role and persona assignment

Reflections on success/failure of this prompt:

*   Success:
- It evaluated people and gave them a score out of 100 like I wanted.
- Furthermore, it also expanded the headcount feature to have a filter that priortizes bringing on people with the highest scores
Failure:
- The UI is very buggy, there are certain fonts where its color matches the background so its hard to read
- Furthermore, a lot of the UI buttons seem like they wanted to display a figure, but instead display the literal string that represents that figure. EX: instead of ->, it says right_arrow.
-It only scored 45 people which is fine, but it should adjust the headcount slider to max out on 45.
----

Text of my next prompt:

Please fix the following problems:


The font in the yellow colored box is also the color yellow, change it to a font that will standout in this yeloow colored box

Furthermore, with all the buttons in the UI, check that they correctly display the figure you want them to display, the currently show text which overlaps with the text in box.

Also, for the side bar, the fonts color match the color of the div that contains them, please use a contrasting color

A refinement strategy from class: Yes

Describe the problem, not just the symptom

Reflections on success/failure of this prompt:

*   Success:
- It fixed the UI issues with the sidebar.

Failure:
- However, that was the only problem that was fixed
-The rest of the issues are still present
- Perhaps, this was not the best refinement strategy due to my lack of ability to explain the problems using a technical vernacular
Text of my next prompt:

Please fix the following problems:


Please fix {insert problem} in the screenshot to be {insert solution}

I used this prompt a numerous amount of times with a screenshot of the problem I was trying to fix

A refinement strategy from class: Yes

Provide examples or references

Reflections on success/failure of this prompt:

*   Success:
- All remaining UI issues were fixed.
- Multiple fast prompts actually yielded faster results than focusing on the quality of the prompt

Failure:
- This took multiple prompts because despite the screenshots and the description of the problem and solution, it still did not implement some of the UI fixes.
- In multiple cases, the AI lies about fixing the problem, and I have to reprompt the AI. Perhaps this is not lying, its just incorrectly doing its job.


### Share Your Best NEW Refinement Strategy

As you see in `cn09`,

1.  Write a short phrase that covers one of your new refinement strategies.
2.  Give a two pairs of "do" and "don't" examples.
3.  Add any description that helps others to use this refinement strategy.
