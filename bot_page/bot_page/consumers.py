from asgiref.sync import async_to_sync
from channels.generic.websocket import SyncConsumer


class ChatConsumer(SyncConsumer):
    def websocket_connect(self, event):
        self.send({'type': 'websocket.accept'})
        async_to_sync(self.channel_layer.group_add)("players", self.channel_name)

    def websocket_disconnect(self, event):
        async_to_sync(self.channel_layer.group_discard)("players", self.channel_name)

    def new_bet(self, event):
        self.send({'type': 'websocket.send', 'text': event['content']})
