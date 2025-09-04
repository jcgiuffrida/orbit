For dashboard need to add recent + total conversations back, they broke




Could you add an audit log of people/conversations/pings added, and edits made? Perhaps django-auditlog along with a view that all users could access. Remember that "private" objects should only be seen by the person who added them. 



The AI summary should be generated, and updated, based on the details of conversations involving the person. Whenever a new conversation is added, we should re-generate the AI summary. It should exclude any private conversations, of course. Since we're running this site as a single Django app, I think a good way to do this might be:
* Add a field for "incorporated into AI summary" to each Conversation
* On a regular basis e.g. nightly, check for any conversations where that field is false - this can be a django managemnet command called from a cronjob
* Re-run the AI summary for people in those conversations
* Set the field to true

Further, we should have a "Regenerate" button for the AI summary on each person's page which would immediately (synchronously) regenerate it. 

To build the summary itself, please stub out a prompt to send into a simple AI. We'll pass info about the person and all their conversations with their dates. AI will then summarize key points about the conversation history. 

