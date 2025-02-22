import keyboard
import asyncio
from concurrent.futures import ThreadPoolExecutor

comb_keys = ['right alt', 'j']
comb_new = ['right alt', 'n']
pressed_keys = []

def is_requested():
    return all(key in pressed_keys for key in comb_keys)

def is_new_pressed():
    return all(key in pressed_keys for key in comb_new)


class KEvents:
    async def new():
        ...

    async def open():
        ...
    
    async def close():
        ...

def read_keyboard_event():
    return keyboard.read_event()

async def kwait():
    was_requested = False
    is_new = True

    executor = ThreadPoolExecutor(max_workers=1)
    loop = asyncio.get_running_loop()

    while True:
        # Run keyboard.read_event() in a separate thread
        event = await loop.run_in_executor(executor, read_keyboard_event)
        
        if event.event_type == 'down' and event.name not in pressed_keys:
            pressed_keys.append(event.name)    

        if event.event_type == 'up' and event.name in pressed_keys:
            pressed_keys.remove(event.name)

        if is_new_pressed() and not is_new:
            asyncio.create_task(KEvents.new())
            is_new = True
    

        if is_requested():
            # If its requested and wasnt before, call the open event
            if not was_requested:
                asyncio.create_task(KEvents.open())
                was_requested = True

                is_new = False
        
        elif was_requested:
            # If its not requested and was before, call the close event
            asyncio.create_task(KEvents.close())
            was_requested = False
