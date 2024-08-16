import json
from channels.generic.websocket import AsyncWebsocketConsumer


class EventConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = "events"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json.get("action", "")
        event_id = text_data_json.get("event_id", None)

        if action == "create":
            # Handle create logic here
            pass
        elif action == "update":
            # Handle update logic here
            pass

        # Notify the group about the change
        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": "event_update", "message": f"Event {action}d with ID {event_id}"},
        )

    async def event_updated(self, event):
        await self.send(
            text_data=json.dumps(
                {"type": "event_updated", "event_data": event["event_data"]}
            )
        )

    async def event_created(self, event):
        # Enviar los datos del evento al frontend
        await self.send(
            text_data=json.dumps(
                {"type": "event_created", "event_data": event["event_data"]}
            )
        )
