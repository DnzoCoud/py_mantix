from apps.events.models import Activity
from apps.sign.models import User
from django.shortcuts import get_object_or_404


def update_or_create_activities_for_event(activities, event):
    for activity_data in activities:
        tecnical = activity_data.get("technician")
        if tecnical["id"] is not None:
            userObject = get_object_or_404(User, pk=tecnical["id"])
        activity_objects = activity_data.get("activities")
        for activity in activity_objects:
            activity_id = activity.get("id")
            name = activity.get("name")
            completed = activity.get("completed")

            if activity_id:
                activityObj = get_object_or_404(Activity, id=activity_id, event=event)
                if activityObj.name != name:
                    activityObj.name = name
                    activityObj.save()
                if activityObj.completed != completed:
                    activityObj.completed = completed
                    activityObj.save()
                if activityObj.technical != userObject:
                    activityObj.technical = userObject
                    activityObj.save()

            else:
                Activity.objects.create(event=event, name=name, technical=userObject)
