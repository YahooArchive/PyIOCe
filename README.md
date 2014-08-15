Python IOC Editor v0.9


Description: 
PyIOCe is an OpenIOC editor built using Python 2.7 and wxPython 3.0.0.0.  

There are many systems for storing complete threat intelligence, but OpenIOC excels at manipulating that data into a reduced and 
operationalized search method.  This can be used to build IOCs that describe broad threat behavior such as persistence mechanisms 
or important forensic sources or it can be used to search for more narrowly identified threats during incident response to rapidly 
scope a compromise across large enterprise networks. 

This project is meant to expand ongoing efforts to broaden the use of OpenIOC with other systems such as Snort, GRR, Splunk, and Yara

Required Python Modules:
wxPython
lxml

Features:
- Almost entirely keyboard driven
- Support for opening and editing OpenIOC 1.0 and 1.1 IOCs simultaneously
- Indicator Term management
- Preferences for default IOC version, default IOC context, and default IOC author
- IOC Cloning
- Revert IOC Changes to last saved

Roadmap:
- Term Conversion Map management
- Term Conversions to quickly change context types of IndicatorTerms based on the Conversion Map
- Import IndicatorTerms from Intel sources such as CybOX, STIX, or CRITS
- IOC Validation/Testing
- Cut/Copy/Paste Support
- More well defined Indicator Terms for GRR, Splunk, Yara, Snort, and other systems



Bug reports, questions, comments, requests:
seagill at yahoo-inc dot com
