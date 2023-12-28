# apps/utils.py

from django.contrib.auth.models import User

def find_next_reviewer(notesheet):
    # Get the list of all reviewers
    all_reviewers = list(User.objects.filter(groups__name='Reviewers'))

    # If no current reviewer is set, return the first reviewer
    if not notesheet.current_reviewer:
        return all_reviewers[0]

    # Find the index of the current reviewer in the list
    current_reviewer_index = all_reviewers.index(notesheet.current_reviewer) if notesheet.current_reviewer in all_reviewers else -1

    # If there is a next reviewer, return that user; otherwise, return None
    next_reviewer_index = current_reviewer_index + 1
    if next_reviewer_index < len(all_reviewers):
        return all_reviewers[next_reviewer_index]
    else:
        return None
