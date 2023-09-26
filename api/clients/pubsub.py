import asyncio
import os
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub_asyncio import PubNubAsyncio


def _get_pubnub_client():
    # We want one pubnub client per event loop
    loop = asyncio.get_event_loop()
    if hasattr(loop, '_pubnub_client'):
        return loop._pubnub_client
    
    # Otherwise, create a new client and store it in the global variable

    pnconfig = PNConfiguration()
    pnconfig.subscribe_key = os.environ.get("VITE_PUBNUB_SUBSCRIBE_KEY")
    pnconfig.publish_key = os.environ.get("PUBNUB_PUBLISH_KEY")
    pnconfig.uuid = 'protocaas2'
    
    client = PubNubAsyncio(pnconfig)
    
    setattr(loop, '_pubnub_client', client)

    return client

async def publish_pubsub_message(*, channel: str, message: dict):
    client = _get_pubnub_client()
    envelope = await client.publish().channel(channel).message(message).future()
    return envelope.result