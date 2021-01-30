import requests
import json
import logging

from app.util import constants, server, runas, system
from app.simulators import basesim

"""
    Communicates with the security camera simulator. 
"""

# Global Variables:
log = logging.getLogger()

class SecuritySim(basesim.Simulator):
    def __init__(self, endpoint):
        """
        Initializes a class of the Security Camera simulator.

        Args:
            None.
        Returns:
            Initialized instance of Security Camera. 
        Examples: 
        >> security = SecuritySim(endpoint=f"http://{ip_addr}/")
        """
        basesim.Simulator.__init__(self, endpoint, 'securitysim')

    def get_last_event(self):
        """
        Gets the last event saved to the Security Camera feed.

        Args:
           None.
        
        Returns:
            (str) string that represents the last XML entry put into the security camera feed. 

        Examples:
        >> scs.get_last_event()
        >> Returns: {'success': True, 'payload': '
        <JournalEntry><RegisterID>1</RegisterID><Timestamp>16-Jun-2020 05:41:19 PM<
        /Timestamp><TermTransID>8</TermTransID><EmployeeID>91</EmployeeID><JournalText>
        </JournalText></JournalEntry>}

        """
        return self.get(f"/getlastevent")

    def get_all_events(self):
        """
        Gets all of the events saved to the Security Camera feed.

        Args:
           None.
        
        Returns:
            (str) string 
            [] if the user runs toggle() and toggles return of list or string.

        Examples:
        >>> scs.get_all_events()
        {'success': True, 'payload': '<JournalEntry><RegisterID>1</RegisterID><Timestamp>17-Jun-2020 04:52:50 PM</Timestamp><TermTransID>9</TermTransID><EmployeeID>91</EmployeeID><JournalText>Begin Sale: Op #: 91</JournalText></JournalEntry><JournalEntry><RegisterID>1</RegisterID><Timestamp>17-Jun-2020 04:52:50 PM</Timestamp><TermTransID>9</TermTransID><EmployeeID>91</EmployeeID><JournalText>Added Item: PLU (004) Item 4 $3.00 Tax Group 99</JournalText></JournalEntry><JournalEntry><RegisterID>1</RegisterID><Timestamp>17-Jun-2020 04:52:51 PM</Timestamp><TermTransID>9</TermTransID><EmployeeID>91</EmployeeID><JournalText>Added Item: PLU (004) Item 4 $3.00 Tax Group 99</JournalText></JournalEntry><JournalEntry><RegisterID>1</RegisterID><Timestamp>17-Jun-2020 04:52:52 PM</Timestamp><TermTransID>9</TermTransID><EmployeeID>91</EmployeeID><JournalText>Added Item: PLU (004) Item 4 $3.00 Tax Group 99</JournalText></JournalEntry><JournalEntry><RegisterID>1</RegisterID><Timestamp>17-Jun-2020 04:52:58 PM</Timestamp><TermTransID>9</TermTransID><EmployeeID>91</EmployeeID><JournalText>Added Item: PLU (004) Item 4 $3.00 Tax Group 99</JournalText></JournalEntry><JournalEntry><RegisterID>1</RegisterID><Timestamp>17-Jun-2020 04:52:59 PM</Timestamp><TermTransID>9</TermTransID><EmployeeID>91</EmployeeID><JournalText>Added Item: PLU (005) Item 5 $2.00 Tax Group 99</JournalText></JournalEntry><JournalEntry><RegisterID>1</RegisterID><Timestamp>17-Jun-2020 04:53:00 PM</Timestamp><TermTransID>9</TermTransID><EmployeeID>91</EmployeeID><JournalText>Added Item: PLU (005) Item 5 $2.00 Tax Group 99</JournalText></JournalEntry>'}

        """
        return self.get(f"/getallevents")

    def get_clear_events(self):
        """
        Clear all events. 

        Args:
           None.
        
        Returns:
            Array value stating whether the action was a success, and a string payoad.

        Examples:
        >>> scs.get_clear_events()
        {'success': True, 'payload': 'events cleared'}
        """
        return self.get(f"/clearevents")
    
    def post_toggle(self, checklist):
        """
        Toggles the security camera to return past values as either a String ('False') or LinkedList('True').
        Also toggles 
        Args:
           ['asLinkedList': Boolean, 'maxValue': int]
           or ['asLinkedList': Boolean]
           or []
        
        Returns:
            Array value stating whether the action was a success, and a string payload.
        Examples:
            >>> params = {'asLinkedList': True, 'maxValue': 50} 
            >>> scs.post_toggle(params)
            {'success': True, 'payload': {'asLinkedList': True, 'maxValue': 50}}
        """
        return self.post("/toggle",checklist)

def init_securitysim():
        """
        Initializes a class of the Security Camera simulator.

        Args:
            None.
        Returns:
            Initialized instance of Security Camera. 
        Examples: 
        >> security = securitysim.init_securitysim()
        
        """
    ip_addr = server.server.get_site_info()['ip']
    security = SecuritySim(endpoint=f"http://{ip_addr}/")
    return security