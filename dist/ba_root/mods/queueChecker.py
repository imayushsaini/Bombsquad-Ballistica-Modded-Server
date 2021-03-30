queueID = None 
import _ba,ba,roles,administrator_setup
queueID = administrator_setup.party_queue_id if administrator_setup.party_queue_id else None
def getAllowed():
    return roles.owners
def _onQueueQueryResult(result):
    #print result
    inQueue = result['e']
    if inQueue != []:
        allowed = getAllowed()
        for queue in inQueue:
            if queue[2] in allowed:
                _ba.chatmessage('Making space for the CEO.')
                currentSize = _ba.get_public_party_max_size()
                _ba.set_public_party_max_size(currentSize+1)
                _ba.get_foreground_host_session().max_players = currentSize+1
def start():
    if (_ba.get_foreground_host_session() is not None) and (queueID): 
        _ba.add_transaction({'type': 'PARTY_QUEUE_QUERY','q': queueID},callback=ba.Call(_onQueueQueryResult))
        _ba.run_transactions()
timer = ba.Timer(20, ba.Call(start), timetype=ba.TimeType.REAL, repeat=True)
print('Queue Checker is enabled')


